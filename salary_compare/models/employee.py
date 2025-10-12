"""Employee base classes and interfaces."""

from abc import ABC, abstractmethod
from decimal import Decimal

from .tax_result import TaxResult


class Employee(ABC):
    """Base class for all employee types."""

    def __init__(self, gross_salary: Decimal, country: str):
        self.gross_salary = Decimal(str(gross_salary))
        self.country = country
        self.employment_type = self.__class__.__name__

    @abstractmethod
    def calculate_net_salary(self) -> TaxResult:
        """Calculate net salary with detailed breakdown."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of the tax regime."""
        pass

    def _create_base_result(self) -> TaxResult:
        """Create base tax result with common fields."""
        return TaxResult(
            gross_salary=self.gross_salary,
            tax_base=self.gross_salary,  # Default to gross, can be overridden
            net_salary=self.gross_salary,
            total_deductions=Decimal("0"),
            country=self.country,
            employment_type=self.employment_type,
            description=self.get_description(),
        )


class SalariedEmployee(Employee):
    """Base class for salaried employees."""

    def __init__(self, gross_salary: Decimal, country: str):
        super().__init__(gross_salary, country)
        self.employment_type = "Salaried Employee"


class Freelancer(Employee):
    """Base class for freelancers."""

    def __init__(self, gross_salary: Decimal, country: str):
        super().__init__(gross_salary, country)
        self.employment_type = "Freelancer"
