import logging
import logging.config
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


def configure_logging():
    """
    Configure logging for the application.
    - Uses a simple console logger with a custom format.
    - Logs all messages with level INFO and above.
    """
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[ %(levelname)s ] %(asctime)s %(name)s %(message)s",
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["default"]},
    })


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    Includes database configuration and API tokens.
    """

    # === Database Settings ===
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432  # Default PostgreSQL port

    DATABASE_URL: Optional[str] = None  # Constructed dynamically

    # === API Tokens ===
    HUGGINGFACE_HUB_TOKEN: Optional[str] = None
    REPLICATE_API_TOKEN: Optional[str] = None
    GEMMA_API_KEY: Optional[str] = None  #  Required for Gemma 3 integration

    @model_validator(mode="after")
    def compute_database_url(self):
        """
        Automatically generate the DATABASE_URL string
        from the PostgreSQL environment variables.
        Raises an error if any required setting is missing.
        """
        if all([
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB
        ]):
            object.__setattr__(
                self,
                "DATABASE_URL",
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}",
            )
        else:
            raise ValueError("Incomplete database configuration.")
        return self

    # Tell Pydantic to load variables from `.env`
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Load settings globally
settings = Settings()
print("DEBUG TOKEN:", settings.REPLICATE_API_TOKEN)
