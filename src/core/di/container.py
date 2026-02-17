"""
Dependency Injection Container.
"""

from dependency_injector import containers, providers

from src.core.di.modules.core import CoreContainer
from src.core.di.modules.meta import MetaContainer


class Container(containers.DeclarativeContainer):
    """
    Main Dependency Injection Container.
    
    Aggregates all modular containers and provides a centralized access point
    for the application's dependencies.
    """

    # Wiring configuration
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.modules.channels.meta.services.meta_service",
        ],
    )
    # Core Infrastructure
    core = providers.Container(CoreContainer)

    # Meta Module
    meta = providers.Container(MetaContainer)
