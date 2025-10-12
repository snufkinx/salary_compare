"""German tax formula calculator (2024)."""

from decimal import Decimal
from typing import List, Tuple

from ..models.tax_result import TaxBracket


class GermanTaxFormula:
    """
    German income tax formula calculator for 2024.

    Implements the official German progressive tax formula (Einkommensteuergesetz).
    The formula uses different calculations for different income zones.
    """

    def __init__(self):
        """Initialize German tax formula with 2024 parameters."""
        # Tax-free allowance (Grundfreibetrag)
        self.tax_free_allowance = 12096.0

        # Zone boundaries
        self.zone2_end = 68480.0  # End of progressive zone 2
        self.zone3_end = 277825.0  # End of linear zone 3

    def calculate_tax(self, taxable_income: Decimal) -> Tuple[Decimal, List[TaxBracket]]:
        """
        Calculate income tax and generate tax brackets.

        Args:
            taxable_income: The taxable income amount

        Returns:
            Tuple of (total_tax, list of tax brackets)
        """
        y = float(taxable_income)
        brackets = []

        if y <= self.tax_free_allowance:
            # Zone 1: Tax-free allowance
            total_tax = Decimal("0")
            brackets.append(
                TaxBracket(
                    lower_bound=Decimal("0"),
                    upper_bound=Decimal(str(self.tax_free_allowance)),
                    rate=Decimal("0"),
                    taxable_amount=taxable_income,
                    tax_amount=Decimal("0"),
                )
            )

        elif y <= self.zone2_end:
            # Zone 2: Progressive formula (14% to ~24%)
            total_tax = self._calculate_zone2_tax(y)
            effective_rate = (
                total_tax / (taxable_income - Decimal(str(self.tax_free_allowance)))
                if taxable_income > Decimal(str(self.tax_free_allowance))
                else Decimal("0")
            )

            brackets.append(
                TaxBracket(
                    lower_bound=Decimal(str(self.tax_free_allowance)),
                    upper_bound=Decimal(str(round(y, 2))),
                    rate=effective_rate,
                    taxable_amount=taxable_income - Decimal(str(self.tax_free_allowance)),
                    tax_amount=total_tax,
                )
            )

        elif y <= self.zone3_end:
            # Zone 3: Linear formula (42%)
            total_tax = self._calculate_zone3_tax(y)
            effective_rate = (
                total_tax / (taxable_income - Decimal(str(self.tax_free_allowance)))
                if taxable_income > Decimal(str(self.tax_free_allowance))
                else Decimal("0")
            )

            brackets.append(
                TaxBracket(
                    lower_bound=Decimal(str(self.tax_free_allowance)),
                    upper_bound=Decimal(str(round(y, 2))),
                    rate=effective_rate,
                    taxable_amount=taxable_income - Decimal(str(self.tax_free_allowance)),
                    tax_amount=total_tax,
                )
            )

        else:
            # Zone 4: Top rate 45%
            total_tax = self._calculate_zone4_tax(y)
            effective_rate = (
                total_tax / (taxable_income - Decimal(str(self.tax_free_allowance)))
                if taxable_income > Decimal(str(self.tax_free_allowance))
                else Decimal("0")
            )

            brackets.append(
                TaxBracket(
                    lower_bound=Decimal(str(self.tax_free_allowance)),
                    upper_bound=Decimal(str(round(y, 2))),
                    rate=effective_rate,
                    taxable_amount=taxable_income - Decimal(str(self.tax_free_allowance)),
                    tax_amount=total_tax,
                )
            )

        return total_tax, brackets

    def _calculate_zone2_tax(self, income: float) -> Decimal:
        """
        Calculate tax for zone 2 (€12,097 - €68,480).

        Uses progressive formula: (922.98 * z + 1400) * z
        where z = (income - 12096) / 10000
        """
        z = (income - self.tax_free_allowance) / 10000
        tax = (922.98 * z + 1400) * z
        return Decimal(str(round(tax, 2)))

    def _calculate_zone3_tax(self, income: float) -> Decimal:
        """
        Calculate tax for zone 3 (€68,481 - €277,825).

        Uses linear formula: 0.42 * income - 10208.78
        """
        tax = 0.42 * income - 10208.78
        return Decimal(str(round(tax, 2)))

    def _calculate_zone4_tax(self, income: float) -> Decimal:
        """
        Calculate tax for zone 4 (€277,826+).

        Uses linear formula: 0.45 * income - constant
        """
        # Calculate tax for zone 3 at boundary
        tax_at_zone3_end = 0.42 * self.zone3_end - 10208.78

        # Zone 4 uses 45% on the amount above zone 3
        amount_in_zone4 = income - self.zone3_end
        tax_in_zone4 = amount_in_zone4 * 0.45

        total_tax = tax_at_zone3_end + tax_in_zone4
        return Decimal(str(round(total_tax, 2)))
