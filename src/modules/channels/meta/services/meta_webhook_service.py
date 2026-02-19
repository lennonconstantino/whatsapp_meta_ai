
from src.modules.channels.meta.dtos.inbound import Payload, Message
from src.modules.channels.meta.services.webhook.owner_resolver import MetaWebhookOwnerResolver
from src.modules.channels.meta.services.meta_service import MetaService
from src.core.utils.logging import get_logger

logger = get_logger(__name__)


class MetaWebhookService:
    def __init__(self, 
                 owner_resolver: MetaWebhookOwnerResolver,
                 meta_service: MetaService):
        self.owner_resolver = owner_resolver
        self.meta_service = meta_service

    async def handle_webhook(self, payload: Payload):
        logger.info(f"Meta Webhook received: {payload}")

        try:
            owner_id = await self.owner_resolver.resolve_owner_id(payload)
            if not owner_id:
                logger.error(f"Owner lookup failed for payload: {payload}")
                return None

            entry = payload.entry[0]
            change = entry.changes[0]
            value = change.value

            if self._is_status_event(value):
                self._handle_status_event(value)
                return None

            if not self._is_inbound_message_event(value):
                logger.info(f"Unsupported webhook event: {value}")
                return None

            display_phone_number = value.metadata.display_phone_number
            from_number = value.contacts[0].wa_id

            text = await self._extract_text_from_message(
                value,
                owner_id,
                from_number,
                display_phone_number,
            )

            if text:
                await self.meta_service.send_message(
                    owner_id=owner_id,
                    from_number=from_number,
                    to_number=display_phone_number,
                    message=text,
                    media_type=value.messages[0].type,
                )
                logger.info(
                    f"Inbound message handled: reply sent from {from_number} to "
                    f"{display_phone_number} for owner {owner_id}"
                )

        except Exception as e:
            logger.error(f"Error sending message via Meta webhook: {e}")
            return None

    def _is_status_event(self, value):
        return (not value.messages or len(value.messages) == 0) and bool(value.statuses)

    def _handle_status_event(self, value):
        status = value.statuses[0]
        logger.info(f"Status update: {status.status} for message {status.id}")

    def _is_inbound_message_event(self, value):
        if not value.messages or len(value.messages) == 0:
            return False
        if not value.contacts or len(value.contacts) == 0:
            logger.error("Missing contacts in payload for message event")
            return False
        return True

    async def _extract_text_from_message(
        self,
        value,
        owner_id: str | None = None,
        from_number: str | None = None,
        display_phone_number: str | None = None,
    ) -> str | None:
        first_message: Message = value.messages[0]

        if first_message.type == "text" and first_message.text:
            return first_message.text.body

        if first_message.type == "reaction" and first_message.reaction:
            emoji = first_message.reaction.emoji
            logger.info(
                f"Reaction received: {emoji} on message {first_message.reaction.message_id}"
            )
            return f"Received reaction: {emoji}"

        if first_message.type == "audio" and first_message.audio:
            audio_id = first_message.audio.id
            logger.info(
                f"Audio ID: {audio_id}, MIME Type: {first_message.audio.mime_type}"
            )
            audio_bytes = await self.meta_service.download_media(
                audio_id, "audio", first_message.audio.mime_type
            )
            if audio_bytes:
                audio_path = await self.meta_service.save_media(
                    audio_bytes,
                    "audio",
                    audio_id,
                    first_message.audio.mime_type,
                )
                logger.info(f"Audio downloaded: {audio_path}")
            return None

        if first_message.type == "image" and first_message.image:
            image_id = first_message.image.id
            caption = first_message.image.caption
            logger.info(f"Image ID: {image_id}, Caption: {caption}")
            image_bytes = await self.meta_service.download_media(
                image_id, "image", first_message.image.mime_type
            )
            if image_bytes:
                image_path = await self.meta_service.save_media(
                    image_bytes,
                    "image",
                    image_id,
                    first_message.image.mime_type,
                )
                logger.info(f"Image downloaded: {image_path}, caption: {caption}")
            return caption

        if first_message.type == "video" and first_message.video:
            video_id = first_message.video.id
            caption = first_message.video.caption
            logger.info(f"Video ID: {video_id}, Caption: {caption}")
            video_bytes = await self.meta_service.download_media(
                video_id, "video", first_message.video.mime_type
            )
            if video_bytes:
                video_path = await self.meta_service.save_media(
                    video_bytes,
                    "video",
                    video_id,
                    first_message.video.mime_type,
                )
                logger.info(f"Video downloaded: {video_path}, caption: {caption}")
            return caption

        return None
