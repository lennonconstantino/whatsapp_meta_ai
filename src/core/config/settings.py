"""
Configuration module for the project.
Handles environment variables and application settings.
"""

from pydantic import Field, field_validator, model_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """API server settings."""

    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )
    use_fake_sender: bool = Field(
        default=False, description="Use fake sender in development environment"
    )
    bypass_subscription_check: bool = Field(
        default=False,
        description="Bypass subscription validation (Development only)",
    )

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class SupabaseSettings(BaseSettings):
    """Supabase connection settings."""

    url: str | None = Field(default=None, description="Supabase project URL")
    key: str | None = Field(default=None, description="Supabase anon key")
    service_key: str | None = Field(
        default=None, 
        description="Supabase service role key",
        validation_alias=AliasChoices("SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_ROLE_KEY")
    )
    db_schema: str = Field(
        default="public", description="Default database schema (e.g. public, app)"
    )
    project_ref: str | None = Field(default=None, description="Supabase project reference")
    anon_key: str | None = Field(default=None, description="Supabase anon key")

    model_config = SettingsConfigDict(
        env_prefix="SUPABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class MetaSettings(BaseSettings):
    """Default Meta settings (can be overridden per owner)."""

    bearer_token_access: str | None = Field(default=None, description="Meta Bearer Token Access")
    verification_token: str | None = Field(default=None, description="Meta Verification Token")
    phone_number_id: str | None = Field(
        default=None, description="Meta Phone Number ID"
    )
    version_api: str | None = Field(default=None, description="Meta Version API")
    phone_number: str | None = Field(default=None, description="Meta Phone Number (owner)")
    business_account_id: str | None = Field(
        default=None, description="Meta Business Account ID"
    )

    model_config = SettingsConfigDict(
        env_prefix="META_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

class Settings(BaseSettings):
    """Main application settings."""
    
    api: APISettings = Field(default_factory=APISettings)
    supabase: SupabaseSettings = Field(default_factory=SupabaseSettings)
    meta: MetaSettings = Field(default_factory=MetaSettings)


    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


# Global settings instance
settings = Settings()