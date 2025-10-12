"""Enums for tax calculation system."""

from enum import Enum


class Currency(str, Enum):
    """Supported currencies."""

    EUR = "EUR"
    CZK = "CZK"
    ILS = "ILS"
    USD = "USD"
    GBP = "GBP"


class DeductionBase(str, Enum):
    """Base amount for deduction calculation."""

    GROSS = "gross"  # Deduction calculated on gross salary
    TAXABLE = "taxable"  # Deduction calculated on taxable income (tax base)
    TAX_BASE = "tax_base"  # Alias for taxable
    INCOME_TAX = "income_tax"  # Deduction calculated on income tax (e.g., solidarity surcharge)


class EmploymentType(str, Enum):
    """Employment types."""

    SALARIED = "Salaried Employee"
    FREELANCER = "Freelancer"
    CONTRACTOR = "Contractor"
    SELF_EMPLOYED = "Self-Employed"


class Country(str, Enum):
    """Supported countries."""

    GERMANY = "Germany"
    CZECHIA = "Czechia"
    ISRAEL = "Israel"
    USA = "USA"
    UK = "UK"
