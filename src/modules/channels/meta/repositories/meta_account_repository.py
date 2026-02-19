from abc import ABC, abstractmethod
from typing import List, Optional

from src.modules.channels.meta.models.meta_account import MetaAccount


class MetaAccountRepository(ABC):
    @abstractmethod
    async def create_meta_account(self, meta_account: MetaAccount) -> MetaAccount:
        ...

    @abstractmethod
    async def get_by_id(self, account_id: str) -> Optional[MetaAccount]:
        ...


    @abstractmethod
    async def get_by_owner_id(self, owner_id: str) -> List[MetaAccount]:
        ...

    @abstractmethod
    async def get_by_meta_business_account_id(self, business_account_id: str) -> Optional[MetaAccount]:
        ...

    @abstractmethod
    async def get_by_meta_business_account_id(self, business_account_id: str) -> Optional[MetaAccount]:
        ...

    @abstractmethod
    async def get_by_phone_number(self, phone_number: str) -> Optional[MetaAccount]:
        ...

    @abstractmethod
    async def update_meta_account(self, account_id: str, data: dict) -> Optional[MetaAccount]:
        ...

    @abstractmethod
    async def delete_meta_account(self, account_id: str) -> bool:
        ...

