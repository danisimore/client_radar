import yaml
from pydantic import BaseModel


class Range(BaseModel):
    """Range for fields with the ability to specify values 'from' and 'to'."""

    min: int
    max: int | None = None


class Contacts(BaseModel):
    """Contacts data defined in the YAML configuration."""

    phone: bool = False
    email: bool = False
    site: bool = False


class Filters(BaseModel):
    """Filter data defined in the YAML configuration."""

    okved_codes: list[str]
    regions: list[str]
    employees_number: Range
    statuses: list[str]
    legal_form: list[str]
    revenue: Range
    contacts: Contacts


class ClientRadar(BaseModel):
    """client_radar data defined in the YAML configuration."""

    filters: Filters


class Config(BaseModel):
    """YAML Configuration schema top-level data."""

    client_radar: ClientRadar


def load_yaml() -> Config:
    """Loads yaml configuration file.

    Returns:
        Config: object with data from yaml config file.
    """
    with open("config.yaml", "r", encoding="UTF-8") as f:
        data = yaml.safe_load(f)
    config = Config.model_validate(data)
    return config
