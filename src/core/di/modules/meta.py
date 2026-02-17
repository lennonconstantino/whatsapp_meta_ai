from dependency_injector import containers, providers

from src.core.di.modules.core import CoreContainer
from src.modules.channels.meta.repositories.impl.supabase_meta_account_repository import SupabaseMetaAccountRepository
from src.modules.channels.meta.services.meta_service import MetaService


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
