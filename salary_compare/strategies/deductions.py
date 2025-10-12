"""Deduction calculation strategies."""

from decimal import Decimal
from typing import Callable, Dict, List, Optional

from ..models.config import DeductionConfig, TaxBracketConfig
from ..models.enums import DeductionBase
from ..models.tax_result import Deduction, TaxBracket
from .base import DeductionStrategy


class FlatRateDeduction(DeductionStrategy):
    """Simple flat-rate deduction (e.g., pension at 9.3%)."""

    def __init__(self, config: DeductionConfig):
        """Initialize with deduction configuration."""
        self.config = config

    def get_base_amount(self, gross_salary: Decimal, tax_base: Decimal, context: Dict) -> Decimal:
        """Get base amount based on applies_to configuration."""
        if self.config.applies_to == DeductionBase.GROSS:
            return gross_salary
        elif self.config.applies_to in (DeductionBase.TAXABLE, DeductionBase.TAX_BASE):
            return tax_base
        elif self.config.applies_to == DeductionBase.INCOME_TAX:
            return context.get("income_tax_amount", Decimal("0"))
        return gross_salary

    def calculate(self, base_amount: Decimal, context: Dict) -> Deduction:
        """Calculate flat-rate deduction with optional ceiling."""
        # Apply ceiling if specified
        actual_base = min(base_amount, self.config.ceiling) if self.config.ceiling else base_amount
        amount = actual_base * self.config.rate

        # Build calculation details
        details = f"{actual_base:,.0f} × {self.config.rate:.1%} = {amount:,.0f}"
        if self.config.ceiling and base_amount > self.config.ceiling:
            details += f" (capped at €{self.config.ceiling:,.0f})"

        return Deduction(
            name=self.config.name,
            amount=amount,
            rate=self.config.rate,
            description=self.config.description,
            calculation_details=details,
        )


class ProgressiveTaxDeduction(DeductionStrategy):
    """Progressive tax with multiple brackets."""

    def __init__(
        self,
        config: DeductionConfig,
        brackets: List[TaxBracketConfig],
        discount: Optional[Decimal] = None,
    ):
        """
        Initialize progressive tax deduction.

        Args:
            config: Deduction configuration
            brackets: List of tax brackets
            discount: Optional flat discount to subtract from total tax
        """
        self.config = config
        self.brackets = brackets
        self.discount = discount or Decimal("0")

    def get_base_amount(self, gross_salary: Decimal, tax_base: Decimal, context: Dict) -> Decimal:
        """Get base amount based on applies_to configuration."""
        if self.config.applies_to == DeductionBase.GROSS:
            return gross_salary
        elif self.config.applies_to in (DeductionBase.TAXABLE, DeductionBase.TAX_BASE):
            return tax_base
        return tax_base

    def calculate(self, base_amount: Decimal, context: Dict) -> Deduction:
        """Calculate progressive tax across all brackets."""
        total_tax = Decimal("0")
        remaining_income = base_amount
        bracket_objects = []

        for bracket_config in self.brackets:
            if remaining_income <= 0:
                break

            lower_bound = bracket_config.lower_bound
            upper_bound = bracket_config.upper_bound
            rate = bracket_config.rate

            # Handle infinity upper bound
            if upper_bound == Decimal("inf"):
                upper_bound = base_amount

            # Calculate taxable amount in this bracket
            taxable_in_bracket = min(remaining_income, upper_bound - lower_bound)

            if taxable_in_bracket > 0:
                tax_in_bracket = taxable_in_bracket * rate
                total_tax += tax_in_bracket

                # Create bracket object for result
                bracket_obj = TaxBracket(
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    rate=rate,
                    taxable_amount=taxable_in_bracket,
                    tax_amount=tax_in_bracket,
                )
                bracket_objects.append(bracket_obj)

                remaining_income -= taxable_in_bracket

        # Apply discount if specified
        tax_before_discount = total_tax
        total_tax = max(Decimal("0"), total_tax - self.discount)

        # Store brackets in context for HTML expandable display
        context["income_tax_brackets"] = bracket_objects
        context["income_tax_amount"] = total_tax

        # Build calculation details
        if self.discount > 0:
            details = f"Tax: {tax_before_discount:,.0f}, Discount: {self.discount:,.0f}, Final: {total_tax:,.0f}"
        else:
            details = f"Total tax from all applicable brackets = {total_tax:,.0f}"

        return Deduction(
            name=self.config.name,
            amount=total_tax,
            rate=total_tax / base_amount if base_amount > 0 else Decimal("0"),
            description=self.config.description,
            calculation_details=details,
        )


class CappedPercentageDeduction(DeductionStrategy):
    """Percentage deduction with a cap (e.g., Keren Hishtalmut)."""

    def __init__(self, config: DeductionConfig):
        """Initialize with configuration including ceiling."""
        self.config = config
        if not config.ceiling:
            raise ValueError("CappedPercentageDeduction requires a ceiling")

    def get_base_amount(self, gross_salary: Decimal, tax_base: Decimal, context: Dict) -> Decimal:
        """Get base amount based on applies_to configuration."""
        if self.config.applies_to == DeductionBase.GROSS:
            return gross_salary
        elif self.config.applies_to in (DeductionBase.TAXABLE, DeductionBase.TAX_BASE):
            return tax_base
        return gross_salary

    def calculate(self, base_amount: Decimal, context: Dict) -> Deduction:
        """Calculate percentage deduction with cap."""
        # Apply cap to base amount
        capped_base = min(base_amount, self.config.ceiling)
        amount = capped_base * self.config.rate

        # Build calculation details
        cap_note = (
            f" (capped at €{self.config.ceiling:,.0f})" if base_amount > self.config.ceiling else ""
        )
        details = f"{capped_base:,.0f} × {self.config.rate:.1%} = {amount:,.0f}{cap_note}"

        return Deduction(
            name=self.config.name,
            amount=amount,
            rate=self.config.rate,
            description=self.config.description,
            calculation_details=details,
        )


class PercentageOfTaxBaseDeduction(DeductionStrategy):
    """Deduction calculated as percentage of a portion of base amount (e.g., 50% of taxable, or 70% of gross)."""

    def __init__(self, config: DeductionConfig, base_multiplier: Decimal):
        """
        Initialize deduction with base multiplier.

        Args:
            config: Deduction configuration
            base_multiplier: Multiplier for the base amount (e.g., 0.50 for 50% of tax base, or 0.70 for 70% of gross)
        """
        self.config = config
        self.base_multiplier = base_multiplier

    def get_base_amount(self, gross_salary: Decimal, tax_base: Decimal, context: Dict) -> Decimal:
        """Get base amount based on applies_to, then multiply by base_multiplier."""
        if self.config.applies_to == DeductionBase.GROSS:
            return gross_salary * self.base_multiplier
        elif self.config.applies_to in (DeductionBase.TAXABLE, DeductionBase.TAX_BASE):
            return tax_base * self.base_multiplier
        return gross_salary * self.base_multiplier

    def calculate(self, base_amount: Decimal, context: Dict) -> Deduction:
        """Calculate deduction on modified base."""
        amount = base_amount * self.config.rate

        # Get original tax base for explanation
        details = f"Base: {base_amount:,.0f}, {self.config.name}: {base_amount:,.0f} × {self.config.rate:.1%} = {amount:,.0f}"

        return Deduction(
            name=self.config.name,
            amount=amount,
            rate=self.config.rate,
            description=self.config.description,
            calculation_details=details,
        )


class ConditionalDeduction(DeductionStrategy):
    """Deduction that only applies if a condition is met (e.g., solidarity surcharge)."""

    def __init__(self, config: DeductionConfig, condition: Callable[[Dict], bool]):
        """
        Initialize conditional deduction.

        Args:
            config: Deduction configuration
            condition: Function that takes context and returns True if deduction applies
        """
        self.config = config
        self.condition = condition

    def get_base_amount(self, gross_salary: Decimal, tax_base: Decimal, context: Dict) -> Decimal:
        """Get base amount based on applies_to configuration."""
        if self.config.applies_to == DeductionBase.INCOME_TAX:
            return context.get("income_tax_amount", Decimal("0"))
        elif self.config.applies_to == DeductionBase.GROSS:
            return gross_salary
        elif self.config.applies_to in (DeductionBase.TAXABLE, DeductionBase.TAX_BASE):
            return tax_base
        return gross_salary

    def calculate(self, base_amount: Decimal, context: Dict) -> Deduction:
        """Calculate deduction if condition is met."""
        # Check condition
        if not self.condition(context):
            # Return zero deduction (won't be added to result)
            return Deduction(
                name=self.config.name,
                amount=Decimal("0"),
                rate=Decimal("0"),
                description=self.config.description,
                calculation_details="Condition not met",
            )

        # Calculate deduction
        amount = base_amount * self.config.rate
        details = f"{base_amount:,.0f} × {self.config.rate:.1%} = {amount:,.0f}"

        return Deduction(
            name=self.config.name,
            amount=amount,
            rate=self.config.rate,
            description=self.config.description,
            calculation_details=details,
        )
