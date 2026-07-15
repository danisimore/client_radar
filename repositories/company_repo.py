import logging
from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from db.models import Company

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
