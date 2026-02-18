

from typing import Any, Dict


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

    async def handle_webhook(self, payload: Dict[str, Any]):
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
            self.meta_service.send_message(owner_id, payload)

        except Exception as e:
            logger.error(f"Error sending message via Meta to owner {owner_id}: {e}")
            return None