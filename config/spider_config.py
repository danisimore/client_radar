from config.base_config import BaseConfig


class SpiderConfig(BaseConfig):
    """Parser Settings."""

    chrome_path: str
    base_url: str = "https://www.rusprofile.ru"
