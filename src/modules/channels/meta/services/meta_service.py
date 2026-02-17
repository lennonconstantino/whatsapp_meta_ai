
import datetime
from typing import Any, Dict, Optional

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
        media_url: Optional[str] = None,
    ):
        """
        Send message via fake sender (development only).

        Args:
            owner_id: Owner ID (ULID)
            from_number: Sender phone number
            to_number: Recipient phone number
            body: Message body
            media_url: Optional media URL
        """
        logger.info(
            "FAKE SENDER - WhatsApp message",
            owner_id=owner_id,
            from_number=from_number,
            to_number=to_number,
            body=body,
            media_url=media_url,
        )

    async def send_message(
        self,
        owner_id: str,
        from_number: str,
        to_number: str,
        body: str,
        media_url: Optional[str] = None
    ) -> Any:
        """
        Send a message via Meta.

        Args:
            owner_id: Owner ID (ULID)
            from_number: Sender phone number
            to_number: Recipient phone number
            body: Message body
            media_url: Optional media URL to send with message

        Returns:
            True if message sent successfully
        """
        # Only send via fake sender in development environment
        if settings.api.environment == "development" and settings.api.use_fake_sender:
            logger.warning("Message sent via fake sender")
            return self.__send_via_fake_sender(
                owner_id, from_number, to_number, body, media_url
            )

        # meta_client = await self._get_client(owner_id)
        # if not meta_client:
        #     logger.error(f"Meta client not found for owner {owner_id}")
        #     return None

        try:
            # TODO: Implement actual message sending logic
            logger.info(f"Sending message via Meta to owner {owner_id}: {body}")

        except Exception as e:
            logger.error(f"Error sending message via Meta to owner {owner_id}: {e}")
            return None
