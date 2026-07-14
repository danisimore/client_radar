from config.spider_config import SpiderConfig
from config.sheets_api_config import SheetsApiConfig
from config.yaml_config import load_yaml
from config.db_config import DBConfig


spider_config = SpiderConfig()
sheets_api_config = SheetsApiConfig()
db_config = DBConfig()
yaml_config = load_yaml()
