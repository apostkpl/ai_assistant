import os
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseModel):
    # app block config in config.yaml
    environment: str = "dev"
    secret_key: str = Field(..., description="Secret key for JWT token generation")
    token_expire_minutes: int = 60

class DatabaseConfig(BaseModel):
    url: str = Field(..., description="Postgres connection string")

class EmailConfig(BaseModel):
    """
    SMTP configurations.
    Currently populated with Resend placeholders.
    """
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
            "http://localhost:8080"
            """ MORE TO BE ADDED WHEN DEPLOYED"""
        ]

class Settings(BaseSettings):
    # bind blocks to settings
    app: AppConfig
    database: DatabaseConfig
    email: EmailConfig
    cors: CorsConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"
    )

    @classmethod
    def load_settings(cls) -> "Settings":
        """Load settings from the YAML config file."""
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file missing at {config_path}")

        with open(config_path, "r") as f:
            yaml_data = yaml.safe_load(f)

        return cls(**yaml_data)

# Global settings instance to import across the app
settings = Settings.load_settings()
