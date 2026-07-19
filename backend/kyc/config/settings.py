from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseModel):
    environment: str = "test"
    version: str = Field(default="1.0.0")
    frontend_url: str = Field(default="http://localhost:5173")
    secret_key: str = Field(..., description="Secret key for JWT")
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
    cors_origins: list[str] = Field(default=["http://localhost:5173"])

class Settings(BaseSettings):
    app: AppConfig
    database: DatabaseConfig
    email: EmailConfig = Field(default_factory=EmailConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",  # Maps APP__ENVIRONMENT to app.environment
        extra="ignore",
    )

settings = Settings()