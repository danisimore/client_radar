from config.base_config import BaseConfig


class DBConfig(BaseConfig):
    """sqlite connect settings."""

    database_url: str
