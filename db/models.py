from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.db import Base


class Company(Base):
    """Represents a company stored in the database."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    director: Mapped[str] = mapped_column(String(255), nullable=True)
    phones: Mapped[list["CompanyPhone"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    emails: Mapped[list["CompanyEmail"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    sites: Mapped[list["CompanySite"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    revenue: Mapped[str] = mapped_column(String(255))
    profit: Mapped[str] = mapped_column(String(255))
    employees_number: Mapped[int] = mapped_column(Integer(), nullable=True)
    okved: Mapped[str] = mapped_column(String())
    address: Mapped[str] = mapped_column(String())
    ogrn: Mapped[str] = mapped_column(String(13), unique=True)


class CompanyPhone(Base):
    """Represents a company's phone number."""

    __tablename__ = "company_phones"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    phone_number: Mapped[str]
    company: Mapped["Company"] = relationship(back_populates="phones")


class CompanyEmail(Base):
    """Represents a company's emails."""

    __tablename__ = "company_emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    email: Mapped[str]
    company: Mapped["Company"] = relationship(back_populates="emails")


class CompanySite(Base):
    """Represents a company's sites."""

    __tablename__ = "company_sites"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    site: Mapped[str]
    company: Mapped["Company"] = relationship(back_populates="sites")
