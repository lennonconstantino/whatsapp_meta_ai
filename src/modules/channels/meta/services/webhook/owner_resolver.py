from typing import Any, Dict

from fastapi import HTTPException

from src.modules.channels.meta.services.meta_account_service import MetaAccountService
from src.core.utils.logging import get_logger


logger = get_logger(__name__)


class MetaWebhookOwnerResolver:
    def __init__(self, meta_account_service: MetaAccountService):
        self.meta_account_service = meta_account_service
        

    async def resolve_owner_id(self, payload: Dict[str, Any]) -> str:
        """Resolve owner ID from webhook payload.

        Args:
            payload: Incoming webhook payload as a dictionary.

        Returns:
            Owner ID (ULID) as a string.
        """
        # TODO: Implement actual owner ID resolution logic
        # For now, return a placeholder owner ID

        #owner_id = payload["entry"][0]["id"] # WhatsApp Business Account ID

        business_account_id = payload["entry"][0]["id"] # WhatsApp Business Account ID
        display_phone_number = payload["entry"][0]["changes"][0]["value"]["metadata"]["display_phone_number"]
        # phone_number_id = payload["entry"][0]["changes"][0]["value"]["metadata"]["phone_number_id"]

        account = await self.meta_account_service.resolve_account(
            phone_number=display_phone_number,
            business_account_id=business_account_id,
        )

        if not account:
            logger.error(
                "Owner lookup failed",
                business_account_id=business_account_id,
                display_phone_number=display_phone_number,
            )
            raise HTTPException(
                status_code=403, detail="Owner not found for inbound/outbound number"
            )            

        return account.owner_id
    
    async def validate_owner_access(self, owner_id: str) -> bool:
        """Validate if the owner has access to the Meta Business Account.

        Args:
            owner_id: Owner ID (ULID) to validate.

        Returns:
            True if owner has access, False otherwise.
        """
        # TODO: Implement actual access validation logic
        # For now, return a placeholder value
        logger.info(f"Validating access for owner {owner_id}")
        return True
    