"""Tax calculation strategies."""

from .base import DeductionStrategy, TaxBaseStrategy
from .deductions import (
    CappedPercentageDeduction,
    ConditionalDeduction,
    FlatRateDeduction,
    PercentageOfTaxBaseDeduction,
    ProgressiveTaxDeduction,
)
from .tax_base import (
    AfterSocialSecurityTaxBase,
    FlatRateExpenseTaxBase,
    StandardTaxBase,
)

__all__ = [
    "DeductionStrategy",
    "TaxBaseStrategy",
    "FlatRateDeduction",
    "ProgressiveTaxDeduction",
    "CappedPercentageDeduction",
    "PercentageOfTaxBaseDeduction",
    "ConditionalDeduction",
    "StandardTaxBase",
    "AfterSocialSecurityTaxBase",
    "FlatRateExpenseTaxBase",
]
