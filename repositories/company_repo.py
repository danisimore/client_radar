import logging
from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from db.models import Company, CompanyPhone, CompanySite, CompanyEmail
from dto.company_data import CompanyData

_logger = logging.getLogger("client.radar.logger")


class CompanyRepo:
    """Repository for performing CRUD operations on Company entities."""

    def __init__(self, session: Session):
        self._session = session

    def exists_by_ogrn(self, ogrn: str) -> bool:
        """
        Check whether a company with the specified OGRN exists.

        Args:
            ogrn: Primary State Registration Number (OGRN) of the company.

        Returns:
            True if a company with the given OGRN exists, otherwise False.
        """
        stmt = select(exists().where(Company.ogrn == ogrn))
        return self._session.scalar(stmt)

    def create(self, company_data: CompanyData) -> None:
        """
        Creates company and company phones in db.

        Args:
            company_data: data to create.
        """
        company = Company(
            name=company_data.name,
            director=company_data.director,
            revenue=company_data.revenue,
            profit=company_data.profit,
            employees_number=company_data.employees_number,
            okved=company_data.okved,
            address=company_data.address,
            ogrn=company_data.ogrn,
        )
        company.phones = [
            CompanyPhone(phone_number=phone) for phone in company_data.phones
        ]
        company.emails = [
            CompanyEmail(email=email_address) for email_address in company_data.emails
        ]
        company.sites = [
            CompanySite(site=site_address) for site_address in company_data.sites
        ]
        self._session.add(company)
