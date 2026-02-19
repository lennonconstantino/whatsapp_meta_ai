
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
        """Handle incoming webhook payload from Meta.

        Args:
            payload: Incoming webhook payload as a dictionary.
        """

        logger.info(f"Meta Webhook received: {payload}")

        try:
            # 1. Resolve Owner
            owner_id = await self.owner_resolver.resolve_owner_id(payload)
            if not owner_id:
                logger.error(f"Owner lookup failed for payload: {payload}")
                return None

            # 2. Route based on flow (Local Sender vs Normal Inbound)
            value = payload.entry[0].changes[0].value
            display_phone_number = value.metadata.display_phone_number

            text: str | None = None
            if value.messages and len(value.messages) > 0:
                first_message: Message = value.messages[0]
                
                if first_message.type == "text" and first_message.text:
                    text = first_message.text.body
                elif first_message.type == "reaction" and first_message.reaction:
                    emoji = first_message.reaction.emoji
                    logger.info(f"Reaction received: {emoji} on message {first_message.reaction.message_id}")
                    # do it what you want with the reaction                    
                    text = f"Received reaction: {emoji}"
                elif first_message.type == "audio" and first_message.audio:
                    audio_id = first_message.audio.id

                    logger.info(
                        f"Audio ID: {audio_id}, MIME Type: {first_message.audio.mime_type}"
                    )

                    # 1. Baixar o arquivo de mídia via Meta API
                    audio_bytes = await self.meta_service.download_media(
                        audio_id, "audio", first_message.audio.mime_type
                    )
                    # 2. Salvar o arquivo de áudio localmente
                    if audio_bytes:
                        audio_path = await self.meta_service.save_media(
                            audio_bytes,
                            "audio",
                            audio_id,
                            first_message.audio.mime_type,
                        )
                        logger.info(f"Audio downloaded: {audio_path}")

                    # TODO future: implement transcription service
                    # 3. Transcrever (Whisper, etc.)
                    # text = await self.transcription_service.transcribe(audio_bytes)
                    # logger.info(f"Audio transcribed: {text}")
                elif first_message.type == "image" and first_message.image:
                    image_id = first_message.image.id
                    text = first_message.image.caption

                    logger.info(f"Image ID: {image_id}, Caption: {text}")
                    
                    # 1. Baixar o arquivo de mídia via Meta API
                    image_bytes = await self.meta_service.download_media(
                        image_id, "image", first_message.image.mime_type
                    )
                    if image_bytes:
                        image_path = await self.meta_service.save_media(
                            image_bytes,
                            "image",
                            video_id,
                            first_message.image.mime_type,
                        )
                        logger.info(f"Image downloaded: {image_path}, caption: {text}")
                elif first_message.type == "video" and first_message.video:
                    video_id = first_message.video.id
                    text = first_message.video.caption

                    logger.info(f"Video ID: {video_id}, Caption: {text}")

                    # 1. Baixar o arquivo de mídia via Meta API
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
                        logger.info(f"Video downloaded: {video_path}, caption: {text}")

            if text:
                await self.meta_service.send_message(
                    owner_id,
                    display_phone_number,
                    "5511991490733",
                    text,
                )

        except Exception as e:
            logger.error(f"Error sending message via Meta webhook: {e}")
            return None
