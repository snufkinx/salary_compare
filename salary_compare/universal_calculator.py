"""Universal tax calculator using declarative configuration."""

from decimal import Decimal
from typing import Dict

from .models.config import TaxRegimeConfig
from .models.enums import Currency
from .models.tax_result import Deduction, TaxResult
from .services.currency import get_currency_converter


class UniversalTaxCalculator:
    """Universal tax calculator that works for any country using declarative configuration."""

    def __init__(self, gross_salary: Decimal, regime: TaxRegimeConfig):
        """
        Initialize calculator with salary and tax regime.

        Args:
            gross_salary: The gross salary amount in EUR
            regime: Tax regime configuration
        """
        self.gross_salary = gross_salary
        self.regime = regime

        # Initialize currency converter if needed
        if regime.threshold_currency != Currency.EUR:
            self.currency_converter = get_currency_converter(
                from_currency=regime.threshold_currency.value, to_currency=Currency.EUR.value
            )
        else:
            self.currency_converter = None

    def calculate_net_salary(self) -> TaxResult:
        """
        Calculate net salary using the regime's declarative configuration.

        Returns:
            Complete tax calculation result
        """
        # Create base result
        # Use title if available, otherwise fallback to country + employment_type
        display_country = self.regime.title or f"{self.regime.country.value}"
        display_employment = "" if self.regime.title else self.regime.employment_type.value
        
        result = TaxResult(
            gross_salary=self.gross_salary,
            tax_base=Decimal("0"),  # Will be set later
            net_salary=Decimal("0"),  # Will be set later
            total_deductions=Decimal("0"),  # Calculated from deductions
            country=display_country,
            employment_type=display_employment,
            description=self.regime.description,
        )

        # Set currency info
        if self.currency_converter:
            result.local_currency = self.regime.local_currency.value
            result.local_currency_rate = Decimal("1") / self.currency_converter.rate

        # Context for sharing data between strategies
        context: Dict = {}

        # Track which deductions have been calculated (for Germany special case)
        calculated_deductions = set()

        # Step 1: Pre-calculate social security if needed for tax base
        # (For AfterSocialSecurityTaxBase strategy)
        from .strategies.tax_base import AfterSocialSecurityTaxBase

        if isinstance(self.regime.tax_base_strategy, AfterSocialSecurityTaxBase):
            # Calculate social security deductions first
            for i, strategy in enumerate(self.regime.deduction_strategies):
                if strategy.config.applies_to.value == "gross":
                    base_amount = self.gross_salary
                    deduction = strategy.calculate(base_amount, context)
                    if deduction.amount > 0:
                        result.add_deduction(deduction)
                    self._update_context(context, deduction)
                    calculated_deductions.add(i)

        # Step 2: Calculate tax base
        tax_base = self.regime.tax_base_strategy.calculate(self.gross_salary, context)
        result.tax_base = tax_base

        # Step 3: Apply remaining deductions
        for i, strategy in enumerate(self.regime.deduction_strategies):
            # Skip if already calculated
            if i in calculated_deductions:
                continue

            # Get the appropriate base amount for this deduction
            base_amount = strategy.get_base_amount(self.gross_salary, tax_base, context)

            # Calculate the deduction
            deduction = strategy.calculate(base_amount, context)

            # Only add non-zero deductions
            if deduction.amount > 0:
                result.add_deduction(deduction)

            # Update context for subsequent deductions
            self._update_context(context, deduction)

        # Transfer income tax brackets from context to result
        if "income_tax_brackets" in context:
            result.income_tax_brackets = context["income_tax_brackets"]

        # Step 3: Calculate final net salary
        result.net_salary = self.gross_salary - result.total_deductions

        # Step 4: Add calculation explanations
        result.calculation_explanations = self._build_explanations(tax_base, context)

        return result

    def _update_context(self, context: Dict, deduction: Deduction) -> None:
        """Update shared context after applying a deduction."""
        # Track social security total for AfterSocialSecurityTaxBase
        if "insurance" in deduction.name.lower() or "social" in deduction.name.lower():
            current_social = context.get("social_security_total", Decimal("0"))
            context["social_security_total"] = current_social + deduction.amount

        # Track income tax for solidarity surcharge
        if deduction.name.lower() == "income tax":
            context["income_tax_amount"] = deduction.amount

    def _build_explanations(self, tax_base: Decimal, context: Dict) -> Dict[str, str]:
        """Build calculation explanations based on context."""
        explanations = {
            "tax_base": f"Taxable income = {tax_base:,.0f}",
        }

        # Add expense explanation if applicable
        if "deductible_expenses" in context:
            expenses = context["deductible_expenses"]
            explanations["expenses"] = f"Deductible expenses: {expenses:,.0f}"

        return explanations
