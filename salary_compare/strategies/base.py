"""Base strategy classes for tax calculations."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict

from ..models.tax_result import Deduction


class TaxBaseStrategy(ABC):
    """Base class for tax base calculation strategies."""

    @abstractmethod
    def calculate(self, gross_salary: Decimal, context: Dict) -> Decimal:
        """
        Calculate the tax base from gross salary.

        Args:
            gross_salary: The gross salary amount
            context: Shared context dict for passing data between strategies

        Returns:
            The calculated tax base
        """
        pass


class DeductionStrategy(ABC):
    """Base class for deduction calculation strategies."""

    @abstractmethod
    def calculate(self, base_amount: Decimal, context: Dict) -> Deduction:
        """
        Calculate a deduction.

        Args:
            base_amount: The base amount to calculate deduction on
            context: Shared context dict for passing data between strategies

        Returns:
            The calculated deduction
        """
        pass

    @abstractmethod
    def get_base_amount(self, gross_salary: Decimal, tax_base: Decimal, context: Dict) -> Decimal:
        """
        Get the base amount for this deduction based on its applies_to configuration.

        Args:
            gross_salary: The gross salary
            tax_base: The calculated tax base
            context: Shared context dict

        Returns:
            The base amount for calculation
        """
        pass
