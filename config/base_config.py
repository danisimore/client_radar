import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """
    The base class of the configuration.

    Loads environment variables from `.env` in UTF-8 encoding.
    Other configuration classes should inherit from it.
    """

    model_config = ConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=os.getenv("ENV_FILE", ".env"),
    )
