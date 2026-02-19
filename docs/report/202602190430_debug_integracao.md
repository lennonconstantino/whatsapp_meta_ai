# Resumo do Caso: Debug de Integração WhatsApp Business API (Meta)

## Contexto

Sistema de chatbot integrado à **WhatsApp Business API (Meta Graph API)**, com backend em Python (FastAPI), banco de dados **Supabase** e envio de mensagens via `httpx`.

---

## Problema Inicial

### Erro
```
GraphMethodException: Unsupported post request. Object with ID '933589126512285' does not exist
Code: 100 | Subcode: 33
```

### Causa
O **Phone Number ID** armazenado na tabela `meta_accounts` do Supabase estava desatualizado. O número `5511963408111` havia sido reconfigurado no Meta Business Manager, gerando um novo Phone Number ID (`960393240499705`), mas o banco ainda guardava o ID antigo (`933589126512285`).

### Solução
Atualizar o `.env` com o Phone Number ID correto e rodar `make migrate seed` para sincronizar o banco de dados.

---

## Segundo Problema

Após a correção do ID, um novo erro surgiu:

### Erro
```
OAuthException: (#100) Invalid parameter
error_data: { messaging_product: "whatsapp", details: "Invalid parameter" }
```

### Causa Raiz
Bug lógico no `MetaWebhookService`. Ao receber uma mensagem do usuário, o serviço respondia com os parâmetros `from_number` e `to_number` **invertidos**:

```python
# ERRADO — bot respondendo para si mesmo
await self.meta_service.send_message(
    from_number=from_number,           # número do usuário (wa_id)
    to_number=display_phone_number,    # número do bot ← destino errado!
)
```

O `display_phone_number` é o número do **bot** (`5511963408111`), e o `from_number` é o número do **usuário** (`5511991490733`). O bot estava tentando enviar mensagens para si mesmo.

### Solução

```python
# CORRETO
await self.meta_service.send_message(
    owner_id=owner_id,
    from_number=display_phone_number,  # número do bot (remetente)
    to_number=from_number,             # número do usuário (destinatário)
    message=text,
)
```

---

## Problema Estrutural Identificado (não crítico, mas relevante)

O método `_build_post_request` em `MetaService` ignora o banco de dados e usa sempre as credenciais fixas do `settings` (`.env`):

```python
def _build_post_request(self):
    PHONE_NUMBER_ID = settings.meta.phone_number_id  # sempre fixo
    BEARER_TOKEN_ACCESS = settings.meta.bearer_token_access  # sempre fixo
```

O método `_get_client(owner_id)`, que deveria buscar as credenciais dinamicamente por owner, está comentado com um `TODO` e nunca é chamado. Isso significa que o sistema **não suporta múltiplos owners/contas Meta** corretamente — todas as mensagens saem sempre pelas credenciais do `.env`.

---

## Linha do Tempo dos Erros

| Horário | Erro | Causa |
|---|---|---|
| 04:08 | `subcode 33` — ID `933589126512285` não existe | Phone Number ID desatualizado no banco |
| 04:25 | `subcode 33` — mesmo erro | Banco ainda com ID antigo |
| 04:33 | `subcode 33` — mesmo erro | App ainda rodando com config antiga |
| 04:34 | `(#100) Invalid parameter` | ID correto, mas `to_number` apontando para o próprio bot |

---

## Lições Aprendidas

1. **Phone Number ID muda** quando a conta WhatsApp Business é reconfigurada — o banco de dados deve ser atualizado sempre que isso ocorrer.
2. **Credenciais hardcoded via `settings`** criam acoplamento e impedem suporte a múltiplos tenants.
3. **Logs detalhados** (como os do `httpx`) são essenciais para distinguir erros de ID, token e payload na Graph API.
4. **Atenção à direção `from/to`** em webhooks — o remetente da mensagem recebida deve ser o destinatário da resposta, nunca o contrário.