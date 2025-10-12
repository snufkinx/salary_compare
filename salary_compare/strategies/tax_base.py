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
