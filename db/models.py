from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.db import Base


class Company(Base):
    """Represents a company stored in the database."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    director: Mapped[str] = mapped_column(String(255))
    phones: Mapped[list["CompanyPhone"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    email: Mapped[str] = mapped_column(String(255))
    site: Mapped[str] = mapped_column(String(255))
    revenue: Mapped[str] = mapped_column(String(255))
    profit: Mapped[str] = mapped_column(String(255))
    employees_number: Mapped[int] = mapped_column(Integer())
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
