import requests
from src.core.config.settings import settings
import time


def build_payload() -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": settings.meta.business_account_id, # WhatsApp Business Account ID
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "5511991490733",
                                "phone_number_id": settings.meta.phone_number_id, # Phone Number ID
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
                                    "timestamp": str(int(time.time())),
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
