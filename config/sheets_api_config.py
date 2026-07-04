from config.base_config import BaseConfig


class SheetsApiConfig(BaseConfig):
    """API Google Sheets settings."""

    credentials: str
    table_key: str
