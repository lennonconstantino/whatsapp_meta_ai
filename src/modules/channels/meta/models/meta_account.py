
import json
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator
from typing import Annotated, Any, List, Optional

from src.core.utils.custom_ulid import is_valid_ulid


def parse_phone_numbers(v: Any) -> List[str]:
    """Parse phone numbers from string (JSON) if necessary."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return []
    return v


class MetaAccount(BaseModel):
    """ MetaAccounts """
    
    id: Optional[int] = Field(default=None, description="ID único da conta")
    meta_business_account_id: str = Field(..., max_length=255, description="account business id")
    phone_number_id: str = Field(..., max_length=255, description="phone number id")
    phone_number: str = Field(..., max_length=50, description="whatsapp phone number (owner)")
    phone_numbers: Annotated[List[str], BeforeValidator(parse_phone_numbers)] = Field(default_factory=list)
    system_user_access_token: str = Field(..., max_length=500, description="access token using bearer")
    webhook_verification_token: str = Field(..., max_length=500, description="webhook verification token to receive events")
    owner_id: str = Field(..., description="owner id")
    
    model_config = ConfigDict(from_attributes=True)

    def __repr__(self) -> str:
        return f"MetaAccount(id={self.id}, meta_business_account_id={self.meta_business_account_id}, phone_number_id={self.phone_number_id}, phone_number={self.phone_number}, system_user_access_token={self.system_user_access_token}, webhook_verification_token={self.webhook_verification_token}, owner_id={self.owner_id})"
