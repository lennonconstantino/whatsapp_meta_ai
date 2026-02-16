from typing import List, Optional
from pydantic import BaseModel, Field

from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class RoleType(str, Enum):
    ADMIN: str = "admin"
    BASIC: str = "basic"


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    role: RoleType = RoleType.BASIC


class Profile(BaseModel):
    name: str


class Contact(BaseModel):
    profile: Profile
    wa_id: str


class Text(BaseModel):
    body: str


class Image(BaseModel):
    mime_type: str
    sha256: str
    id: str


class Audio(BaseModel):
    mime_type: str
    sha256: str
    id: str
    voice: bool


class Message(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    text: Optional[Text] = None
    image: Optional[Image] = None
    audio: Optional[Audio] = None
    type: str


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class Value(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None

class Change(BaseModel):
    value: Value
    field: str
    statuses: Optional[List[dict]] = None


class Entry(BaseModel):
    id: str
    changes: List[Change]


class Payload(BaseModel):
    object: str
    entry: List[Entry]


class UserMessage(BaseModel):
    user: User
    message: str | None = None
    image: Image | None = None
    audio: Audio | None = None