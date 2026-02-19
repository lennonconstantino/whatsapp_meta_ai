
from typing import Optional


from src.core.utils.logging import get_logger
from src.core.config.settings import settings
from src.modules.channels.meta.repositories.meta_account_repository import MetaAccountRepository
from src.modules.channels.meta.models.meta_account import MetaAccount


logger = get_logger(__name__)


class MetaAccountService:
    def __init__(self, repo: MetaAccountRepository):
        self.repo = repo

    async def resolve_account(self, phone_number: str, business_account_id: str) -> Optional[MetaAccount]:
        """Resolve the MetaAccount based on the phone number.

        Args:
            number: Phone number to resolve the account for.
            business_account_id: Business account ID to resolve the account for.

        Strategies:
        1. Try by business_account_id
        2. Try by Phone Number
        3. Fallback to default from settings (Development only ideally)

        Returns:
            MetaAccount instance.
        """
        account = None

        # 1. Try by Whatsapp Business Account ID
        if business_account_id:
            account = await self.repo.get_by_meta_business_account_id(business_account_id)

        # 2. Try by Phone Number
        if phone_number:
            account = await self.repo.get_by_phone_number(phone_number)

        # 3. Fallback to default from settings (Development only ideally)
        if not account and getattr(settings.api, "environment", "production") == "development":
            account = await self.repo.get_by_meta_business_account_id(settings.meta.business_account_id)

        if not account:
            logger.warning("MetaAccount lookup failed", 
                           phone_number=phone_number, 
                           business_account_id=business_account_id
            )

        return account
