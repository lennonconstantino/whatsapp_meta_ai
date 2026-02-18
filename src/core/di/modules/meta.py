from dependency_injector import containers, providers

from src.core.di.modules.core import CoreContainer
from src.modules.channels.meta.repositories.impl.supabase_meta_account_repository import SupabaseMetaAccountRepository
from src.modules.channels.meta.services.meta_service import MetaService
from src.modules.channels.meta.services.meta_account_service import MetaAccountService
from src.modules.channels.meta.services.webhook.owner_resolver import MetaWebhookOwnerResolver
from src.modules.channels.meta.services.meta_webhook_service import MetaWebhookService


class MetaContainer(containers.DeclarativeContainer):
    """
    Meta Module Container.
    """
    core = providers.Container(CoreContainer)

    # Repositories
    meta_account_repository = providers.Selector(
        core.db_backend,
        supabase=providers.Factory(
            SupabaseMetaAccountRepository,
            client=core.supabase_session,
        ),
    )

    # Services
    meta_service = providers.Factory(
        MetaService, meta_account_repo=meta_account_repository
    )

    meta_account_service = providers.Factory(
        MetaAccountService, repo=meta_account_repository
    )

    meta_webhook_owner_resolver = providers.Factory(
        MetaWebhookOwnerResolver, meta_account_service=meta_account_service
    )

    meta_webhook_service = providers.Factory(
        MetaWebhookService,
        owner_resolver=meta_webhook_owner_resolver,
        meta_service=meta_service,
    )
