from typing import List, Optional

from src.core.database.interface import IDatabaseSession
from src.core.database.supabase_async_repository import SupabaseAsyncRepository
from src.core.utils.logging import get_logger
from src.modules.channels.meta.models.meta_account import MetaAccount
from src.modules.channels.meta.repositories.meta_account_repository import MetaAccountRepository

logger = get_logger(__name__)


class SupabaseMetaAccountRepository(SupabaseAsyncRepository[MetaAccount], MetaAccountRepository):
    def __init__(self, client: IDatabaseSession) -> None:
        super().__init__(
            client=client,
            table_name="meta_accounts",
            model_class=MetaAccount,
            validates_ulid=False,
            primary_key="id",
        )

    async def create_meta_account(self, meta_account: MetaAccount) -> MetaAccount:
        data = meta_account.model_dump(exclude={"id"})
        created = await self.create(data)
        if not created:
            logger.error("Failed to create MetaAccount")
            raise RuntimeError("Failed to create MetaAccount")
        return created


    async def get_by_id(self, account_id: str) -> Optional[MetaAccount]:
        return await self.find_by_id(account_id)


    async def get_by_owner_id(self, owner_id: str) -> List[MetaAccount]:
         return await self.find_by({"owner_id": owner_id})


    async def get_by_meta_business_account_id(self, business_account_id: str) -> Optional[MetaAccount]:
        results = await self.find_by({"meta_business_account_id": business_account_id}, limit=1)
        return results[0] if results else None


    async def get_by_meta_phone_number(self, meta_phone_number: str) -> Optional[MetaAccount]:
        results = await self.find_by({"meta_phone_number": meta_phone_number}, limit=1)
        return results[0] if results else None


    async def update_meta_account(self, account_id: str, data: dict) -> Optional[MetaAccount]:
        if "id" in data:
            data = {**data}
            data.pop("id", None)
        return await self.update(account_id, data)


    async def delete_meta_account(self, account_id: str) -> bool:
        return await self.delete(account_id)
