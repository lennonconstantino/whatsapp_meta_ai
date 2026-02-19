

from typing import Annotated
from fastapi import Depends, Request

from src.modules.channels.meta.dtos.inbound import Audio, Contact, Image, Message, Payload, User


async def parse_payload(request: Request) -> Payload:
    data = await request.json()
    return Payload(**data)


async def parse_contact(payload: Payload) -> Contact | None:
    if not payload.entry[0].changes[0].value.contacts:
        return None

    return payload.entry[0].changes[0].value.contacts[0]


async def parse_message(payload: Payload) -> Message | None:
    if not payload.entry[0].changes[0].value.messages:
        return None
    return payload.entry[0].changes[0].value.messages[0]


async def get_current_user(contact: Annotated[Contact, Depends(parse_contact)]) -> User | None:
    if not contact:
        return None
    
    return User(profile_name=contact.profile.name, phone=contact.wa_id)


async def parse_audio_file(message: Annotated[Message, Depends(parse_message)]) -> Audio | None:
    if message and message.type == "audio":
        return message.audio
    return None


async def parse_image_file(message: Annotated[Message, Depends(parse_message)]) -> Image | None:
    if message and message.type == "image":
        return message.image
    return None


async def message_extractor(
        message: Annotated[Message, Depends(parse_message)],
        audio: Annotated[Audio, Depends(parse_audio_file)],
):
    if audio:
        return "" # message_service.transcribe_audio(audio)
    if message and message.text:
        return message.text.body
    return None