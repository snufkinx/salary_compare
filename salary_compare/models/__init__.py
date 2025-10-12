"""Models for salary calculations."""

from .config import DeductionConfig, TaxBracketConfig, TaxRegimeConfig
from .employee import Employee, Freelancer, SalariedEmployee
from .enums import Country, Currency, DeductionBase, EmploymentType
from .tax_result import Deduction, TaxBracket, TaxResult

__all__ = [
    "Employee",
    "SalariedEmployee",
    "Freelancer",
    "TaxResult",
    "Deduction",
    "TaxBracket",
    "DeductionConfig",
    "TaxBracketConfig",
    "TaxRegimeConfig",
    "Country",
    "Currency",
    "DeductionBase",
    "EmploymentType",
]
