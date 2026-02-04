from pydantic_settings import BaseSettings, SettingsConfigDict

class ApplicationConfig(BaseSettings):
    PORT: int = 8000
    ENV: str = "DEV"

    model_config = SettingsConfigDict(
        env_prefix="APP_", 
        extra="ignore",
        env_file=(".env"),
        env_file_encoding='utf-8'
    )
    
application_config = ApplicationConfig()