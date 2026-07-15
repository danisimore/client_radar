from dataclasses import dataclass


@dataclass
class CompanyData:
    """Represents company data extracted from the parsed HTML page."""

    name: str
    director: str | None
    address: str
    okved: str
    ogrn: str

    revenue: str | None
    profit: str | None
    employees_number: int | None

    phones: list[str]
    emails: list[str]
    sites: list[str]
