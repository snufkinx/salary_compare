"""Configuration models for tax regimes."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from .enums import Country, Currency, DeductionBase, EmploymentType


@dataclass
class DeductionConfig:
    """Configuration for a single deduction."""

    name: str
    description: str
    rate: Decimal
    applies_to: DeductionBase = DeductionBase.GROSS
    ceiling: Optional[Decimal] = None
    floor: Optional[Decimal] = None


@dataclass
class TaxBracketConfig:
    """Configuration for a single tax bracket."""

    lower_bound: Decimal
    upper_bound: Decimal  # Use Decimal("inf") for no upper bound
    rate: Decimal


@dataclass
class TaxRegimeConfig:
    """Complete configuration for a tax regime."""

    country: Country
    employment_type: EmploymentType
    local_currency: Currency
    threshold_currency: Currency  # Currency used for defining thresholds/brackets

    # Optional region identifier (e.g., "Madrid", "Barcelona" for Spain)
    region: Optional[str] = None

    # Description of the tax regime
    description: str = ""

    # Note: Strategies are set separately to avoid circular imports
    tax_base_strategy: Optional[object] = None
    deduction_strategies: List[object] = field(default_factory=list)
