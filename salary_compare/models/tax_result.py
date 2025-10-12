"""Tax calculation result models."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List


@dataclass
class TaxBracket:
    """Represents a tax bracket with its rate and amount."""

    lower_bound: Decimal
    upper_bound: Decimal
    rate: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal

    def __post_init__(self):
        """Convert numeric types to Decimal."""
        for attr in ["lower_bound", "upper_bound", "rate", "taxable_amount", "tax_amount"]:
            if not isinstance(getattr(self, attr), Decimal):
                setattr(self, attr, Decimal(str(getattr(self, attr))))


@dataclass
class Deduction:
    """Represents a tax deduction or contribution."""

    name: str
    amount: Decimal
    rate: Decimal
    description: str
    calculation_details: str = ""

    def __post_init__(self):
        """Convert numeric types to Decimal."""
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
        if not isinstance(self.rate, Decimal):
            self.rate = Decimal(str(self.rate))


@dataclass
class TaxResult:
    """Complete tax calculation result."""

    gross_salary: Decimal
    tax_base: Decimal
    net_salary: Decimal
    total_deductions: Decimal
    income_tax_brackets: List[TaxBracket] = field(default_factory=list)
    deductions: List[Deduction] = field(default_factory=list)
    country: str = ""
    employment_type: str = ""
    description: str = ""
    calculation_explanations: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Convert numeric types to Decimal."""
        for attr in ["gross_salary", "tax_base", "net_salary", "total_deductions"]:
            if not isinstance(getattr(self, attr), Decimal):
                setattr(self, attr, Decimal(str(getattr(self, attr))))

    @property
    def total_income_tax(self) -> Decimal:
        """Calculate total income tax from brackets."""
        return sum(bracket.tax_amount for bracket in self.income_tax_brackets)

    def add_deduction(self, deduction: Deduction) -> None:
        """Add a deduction to the result."""
        self.deductions.append(deduction)
        self.total_deductions += deduction.amount
        self.net_salary = self.gross_salary - self.total_deductions

    def add_income_tax_bracket(self, bracket: TaxBracket) -> None:
        """Add an income tax bracket."""
        self.income_tax_brackets.append(bracket)
        self.add_deduction(
            Deduction(
                name=f"Income Tax (Bracket {len(self.income_tax_brackets)})",
                amount=bracket.tax_amount,
                rate=bracket.rate,
                description=f"Tax at {bracket.rate:.1%} on income {bracket.lower_bound:,.0f} - {bracket.upper_bound:,.0f}",
                calculation_details=f"Taxable amount: {bracket.taxable_amount:,.0f}, Rate: {bracket.rate:.1%}, Tax: {bracket.tax_amount:,.0f}",
            )
        )
