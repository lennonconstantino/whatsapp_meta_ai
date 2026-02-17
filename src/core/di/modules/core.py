from dependency_injector import containers, providers

from src.core.config.settings import settings
from src.core.database.session import DatabaseConnection


class CoreContainer(containers.DeclarativeContainer):
    """
    Core Infrastructure Container.
    """

    # Database
    db_backend = providers.Object(settings.database.backend)

    supabase_connection = providers.Singleton(DatabaseConnection)

    supabase_session = providers.Singleton(lambda db: db.session, supabase_connection)

    supabase_client = providers.Singleton(lambda db: db.client, supabase_connection)
