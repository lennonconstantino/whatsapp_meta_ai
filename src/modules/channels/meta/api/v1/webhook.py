



from typing import Container
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Annotated

from core.di import container
from src.modules.channels.meta.api.dependencies import get_current_user, message_extractor, parse_image_file, parse_message, parse_payload
from src.modules.channels.meta.services.meta_webhook_service import MetaWebhookService
from src.core.utils.logging import get_logger
from src.modules.channels.meta.api import router
from src.modules.channels.meta.dtos.inbound import Image, Message, Payload, User


logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/inbound")
@inject
async def handle_inbound_message(
        payload: Payload = Depends(parse_payload),
        user: User = Depends(get_current_user),
        user_message: str = Depends(message_extractor),
        image: Image = Depends(parse_image_file),
        message: Message = Depends(parse_message),
        meta_webhook_service: MetaWebhookService = Depends(Provide[Container.meta.meta_webhook_service]),
):
    logger.info("Received payload", payload=payload.model_dump())

    if not user or not message:
        value = payload.entry[0].changes[0].value
        if value.statuses:
            status = value.statuses[0]
            logger.info(f"Status update: {status.status} for message {status.id}")
        else:
            logger.info(f"Unknown webhook event: {value}")
        return {"status": "ok"}

    if image:
        caption = image.caption or ""
        logger.info(f"Image received with caption: '{caption}'")
        
        if caption:
            logger.info("Image with caption processed successfully")
        else:
            logger.info("Image received without caption")
        
        return {"status": "ok"}

    if user_message:
        logger.info(
            "Text message received",
            message_id=message.id,
            phone=user.phone,
            message=user_message,
        )
        await meta_webhook_service.send_message(payload) # message.id, message.from_, user.phone, user_message

    return {"status": "ok"}

