from dependency_injector import containers, providers

from src.core.di.modules import core
from src.modules.channels.meta.repositories.impl.supabase_meta_account_repository import SupabaseMetaAccountRepository
from src.modules.channels.meta.services.meta_service import MetaService

class MetaContainer(containers.DeclarativeContainer):
    """
    Meta Module Container.
    """

    # Repositories
    meta_account_repository = providers.Selector(
        core.db_backend,
        supabase=providers.Factory(SupabaseMetaAccountRepository, client=core.supabase_session),
    )

    # Services
    meta_service = providers.Factory(
        MetaService, meta_repo=meta_account_repository
    )