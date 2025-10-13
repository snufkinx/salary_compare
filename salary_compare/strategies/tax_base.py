"""Tax base calculation strategies."""

from decimal import Decimal
from typing import Dict

from .base import TaxBaseStrategy


class StandardTaxBase(TaxBaseStrategy):
    """Standard tax base = Gross salary (most common)."""

    def calculate(self, gross_salary: Decimal, context: Dict) -> Decimal:
        """Tax base equals gross salary."""
        return gross_salary


class AfterSocialSecurityTaxBase(TaxBaseStrategy):
    """Tax base = Gross - Social Security (used in Germany)."""

    def calculate(self, gross_salary: Decimal, context: Dict) -> Decimal:
        """Tax base equals gross minus social security contributions."""
        social_security_total = context.get("social_security_total", Decimal("0"))
        return gross_salary - social_security_total


class FlatRateExpenseTaxBase(TaxBaseStrategy):
    """Tax base with flat-rate expense deduction and cap (Czech Freelancer 60/40)."""

    def __init__(self, taxable_rate: Decimal, expense_cap: Decimal):
        """
        Initialize flat-rate expense tax base.

        Args:
            taxable_rate: Rate of income that is taxable (e.g., 0.40 for 60/40 rule)
            expense_cap: Maximum gross income for flat-rate expense application
        """
        self.taxable_rate = taxable_rate
        self.expense_cap = expense_cap

    def calculate(self, gross_salary: Decimal, context: Dict) -> Decimal:
        """
        Calculate tax base with expense cap.

        If income <= cap: taxable = income × taxable_rate
        If income > cap: taxable = (cap × taxable_rate) + (income - cap)
        """
        if gross_salary <= self.expense_cap:
            # Below cap: apply flat rate
            taxable_income = gross_salary * self.taxable_rate
            deductible_expenses = gross_salary * (Decimal("1") - self.taxable_rate)
        else:
            # Above cap: flat rate only up to cap, rest is 100% taxable
            taxable_up_to_cap = self.expense_cap * self.taxable_rate
            income_above_cap = gross_salary - self.expense_cap
            taxable_income = taxable_up_to_cap + income_above_cap
            deductible_expenses = self.expense_cap * (Decimal("1") - self.taxable_rate)

        # Store for use in explanations
        context["deductible_expenses"] = deductible_expenses
        context["expense_cap_applied"] = gross_salary > self.expense_cap

        return taxable_income


class SpanishEmploymentIncomeTaxBase(TaxBaseStrategy):
    """
    Tax base for Spanish employment income with standard reduction.

    Spanish tax law provides a reduction for employment income (reducción por rendimientos del trabajo):
    - €6,498 for net income up to €14,047.50
    - Gradual reduction between €14,047.50 and €19,747.50
    - €2,000 minimum for all employment income

    Tax base = Gross - Social Security - Employment Income Reduction
    """

    def calculate(self, gross_salary: Decimal, context: Dict) -> Decimal:
        """Calculate Spanish tax base with employment income reduction."""
        # First deduct social security
        social_security_total = context.get("social_security_total", Decimal("0"))
        net_income = gross_salary - social_security_total

        # Calculate employment income reduction
        reduction = self._calculate_employment_reduction(net_income)

        # Store for transparency
        context["employment_income_reduction"] = reduction
        context["net_income_before_tax"] = net_income

        # Tax base = Net income - Employment reduction
        return net_income - reduction

    def _calculate_employment_reduction(self, net_income: Decimal) -> Decimal:
        """
        Calculate the Spanish employment income reduction.

        For 2024-2025:
        - Full reduction (€6,498) if net income ≤ €14,047.50
        - Gradual reduction if €14,047.50 < net income < €19,747.50
        - Minimum €2,000 for all employment income
        """
        max_reduction = Decimal("6498")
        min_reduction = Decimal("2000")
        lower_threshold = Decimal("14047.50")
        upper_threshold = Decimal("19747.50")

        if net_income <= lower_threshold:
            # Full reduction
            return max_reduction
        elif net_income >= upper_threshold:
            # Minimum reduction
            return min_reduction
        else:
            # Gradual phase-out
            # reduction = 6498 - ((net_income - 14047.50) × (4498 / 5700))
            phase_out_range = upper_threshold - lower_threshold
            reduction_range = max_reduction - min_reduction
            excess = net_income - lower_threshold

            reduction = max_reduction - (excess * reduction_range / phase_out_range)
            return max(reduction, min_reduction)
