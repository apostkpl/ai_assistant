import os
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, InitSettingsSource

class AppConfig(BaseModel):
    environment: str = "dev"
    secret_key: str = Field(..., description="Secret key for JWT token generation")
    token_expire_minutes: int = 60

class DatabaseConfig(BaseModel):
    url: str = Field(..., description="Postgres connection string")

class EmailConfig(BaseModel):
    smtp_host: str = "smtp.resend.com"
    smtp_port: int = 587
    smtp_username: str = "resend"
    smtp_password: str = "PLACEHOLDER_API_KEY"
    from_email: str = "noreply@yourdomain.local"
    from_name: str = "KYC Verification"

class CorsConfig(BaseModel):
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://ai.dev-yapping.eu"
    ]

class Settings(BaseSettings):
    app: AppConfig
    database: DatabaseConfig
    email: EmailConfig = Field(default_factory=EmailConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        *args,
        **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        
        class YamlConfigSettingsSource(InitSettingsSource):
            def __call__(self) -> dict[str, any]:
                config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
                if not os.path.exists(config_path):
                    return {}
                with open(config_path, "r") as f:
                    return yaml.safe_load(f) or {}
                
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls, {})
        )

settings = Settings()