
import datetime
from typing import Any, Dict, Optional

import httpx

from src.core.config.settings import settings
from src.core.utils.logging import get_logger
from src.modules.channels.meta.models.meta_client import MetaClient
from src.modules.channels.meta.repositories.meta_account_repository import MetaAccountRepository


logger = get_logger(__name__)


class MetaService:
    def __init__(self, meta_account_repo: MetaAccountRepository):
        """
        Initialize Meta service.

        Args:
            meta_account_repo: Meta account repository
        """
        self.meta_account_repo = meta_account_repo
        self._clients: Dict[str, MetaClient] = {}  
      

    async def _get_client(self, owner_id: str) -> Optional[MetaClient]:
        """
        Get or create Meta client for an owner.

        Args:
            owner_id: Owner ID (ULID)

        Returns:
            Meta client or None
        """
        # TODO: Implement actual client creation logic
        # meta_account = await self.meta_account_repo.get_by_owner_id(owner_id)
        meta_account = None
        if not meta_account:
            logger.warning(f"No Meta account found for owner {owner_id}")

            # try to use default credentials (development only)
            if settings.api.environment == "development":
                meta_client = MetaClient(access_token="", expires_at=datetime.datetime.now())
                self._clients[owner_id] = meta_client
                return meta_client

            return None
        
        # Create Client
        try:
            meta_client = MetaClient(
                access_token=meta_account.access_token,
                expires_at=meta_account.expires_at,
            )
            self._clients[owner_id] = meta_client
            return meta_client
        except Exception as e:
            logger.error(f"Error creating Meta client for owner {owner_id}: {e}")
            return None

    def __send_via_fake_sender(
        self,
        owner_id: str,
        from_number: str,
        to_number: str,
        body: str,
        media_type: Optional[str] = None,
    ):
        """
        Send message via fake sender (development only).

        Args:
            owner_id: Owner ID (ULID)
            from_number: Sender phone number
            to_number: Recipient phone number
            body: Message body
            media_type: Optional media type (image, audio, video)
        """
        logger.info(
            "FAKE SENDER - WhatsApp message",
            owner_id=owner_id,
            from_number=from_number,
            to_number=to_number,
            body=body,
            media_type=media_type,
        )

    def _build_post_request(self):
        VERSION_API = settings.meta.version_api
        PHONE_NUMBER_ID = settings.meta.phone_number_id
        BEARER_TOKEN_ACCESS = settings.meta.bearer_token_access
        url = f"https://graph.facebook.com/{VERSION_API}/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": "Bearer " + BEARER_TOKEN_ACCESS,
            "Content-Type": "application/json"
        }

        return url, headers


    async def download_media(self, file_id: str, file_type: str, mime_type: str) -> bytes | None:
        url = f"https://graph.facebook.com/{settings.meta.version_api}/{file_id}"
        headers = {"Authorization": f"Bearer {settings.meta.bearer_token_access}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise ValueError(f"Failed to retrieve download URL. Status code: {response.status_code}")

            download_url = response.json().get("url")

            response = await client.get(download_url, headers=headers)
            if response.status_code != 200:
                raise ValueError(f"Failed to download file. Status code: {response.status_code}")

            # suporta image, audio e video
            if file_type in ("image", "audio", "video"):
                return response.content

        return None

    async def save_media(
        self,
        content: bytes,
        file_type: str,
        file_id: str,
        mime_type: str,
    ) -> str | None:
        file_extension = mime_type.split("/")[-1].split(";")[0]
        file_path = f"{file_id}.{file_extension}"

        with open(file_path, "wb") as file:
            file.write(content)

        if file_type in ("image", "audio", "video"):
            return file_path

        return None

    async def send_template(
            self, 
            owner_id: str,
            from_number: str,
            to_number: str,
            message: str,
            media_url: Optional[str] = None) -> Any:

        # Only send via fake sender in development environment
        if settings.api.environment == "development" and settings.api.use_fake_sender:
            logger.warning("Message sent via fake sender")
            return self.__send_via_fake_sender(
                owner_id, from_number, to_number, message, media_url
            )

        url, headers = self._build_post_request()

        logger.info(f"Meta API request: {url} {headers} - "
                    f"Owner ID: {owner_id} To: {to_number} Message: {message}")
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {
                    "code": "en_US"
                }
            }
        }

        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=data)
            logger.info(f"Meta API response: {response.status_code} {response.text}")
            
        return response.json()


    async def send_message(
            self, 
            owner_id: str,
            from_number: str,
            to_number: str,
            message: str,
            media_type: Optional[str] = None) -> Any:
        
        # Only send via fake sender in development environment
        if settings.api.environment == "development" and settings.api.use_fake_sender:
            logger.warning("Message sent via fake sender")
            return self.__send_via_fake_sender(
                owner_id, from_number, to_number, message, media_type
            )
        
        url, headers = self._build_post_request()

        logger.info(f"Meta API request: {url} {headers} "
                    f"Owner ID: {owner_id} To: {to_number} Message: {message}")

        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=data)
            logger.info(f"Meta API response: {response.status_code} {response.text}")

        return response.json()
