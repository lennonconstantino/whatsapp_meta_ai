from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class User(BaseModel):
    profile_name: str
    phone: str


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
    caption: str | None = None


class Audio(BaseModel):
    mime_type: str # ex: "audio/ogg; codecs=opus"
    sha256: str
    id: str
    voice: bool | None = None  # True if recorded in WhatsApp


class Video(BaseModel):
    mime_type: str
    sha256: str
    id: str
    caption: str | None = None


class Reaction(BaseModel):
    message_id: str
    emoji: str  # ex: "❤️"


class Message(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str
    reaction: Optional[Reaction] | None = None
    text: Optional[Text] | None = None
    image: Optional[Image] | None = None
    audio: Optional[Audio] | None = None
    video: Optional[Video] | None = None
    


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class StatusUpdate(BaseModel):
    id: str
    status: str  # "sent", "delivered", "read", "failed"
    timestamp: str
    recipient_id: str
    

class Value(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None
    statuses: list[StatusUpdate] | None = None  # ← adicione isso

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

