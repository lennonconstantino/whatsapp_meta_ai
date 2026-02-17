import requests


def build_payload() -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "5511991490733",
                                "phone_number_id": "PHONE_NUMBER_ID",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Lennon Bahia"},
                                    "wa_id": "5511991490733",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5511991490733",
                                    "id": "wamid.TEST_MESSAGE_ID",
                                    "timestamp": "1737052800",
                                    "text": {"body": "Olá, isso é um teste de webhook"},
                                    "type": "text",
                                }
                            ],
                        },
                        "field": "messages",
                        "statuses": [],
                    }
                ],
            }
        ],
    }


def main() -> None:
    url = "http://localhost:8000/webhook"
    payload = build_payload()
    body = {
        "payload": payload,
        "data": payload,
    }
    response = requests.post(url, json=body)
    print("Status:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    main()
