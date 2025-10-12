"""Germany tax calculator for salaried employees."""

from decimal import Decimal

from ..models.employee import SalariedEmployee
from ..models.tax_result import Deduction, TaxBracket, TaxResult


class SalariedEmployeeGermany(SalariedEmployee):
    """Germany salaried employee tax calculator (Tax Class 1)."""

    def __init__(self, gross_salary: Decimal, tax_class: int = 1):
        super().__init__(gross_salary, "Germany")
        self.tax_class = tax_class

        # Tax-free allowance
        self.tax_free_allowance = Decimal("12096")

        # Progressive tax brackets (simplified, in 10k increments)
        # Based on 2024 German tax formula with higher marginal rates
        self.tax_brackets = [
            (0, 12096, 0.00),  # 0% up to tax-free allowance
            (12096, 22096, 0.24),  # ~24% marginal rate
            (22096, 32096, 0.32),  # ~32% marginal rate
            (32096, 42096, 0.37),  # ~37% marginal rate
            (42096, 52096, 0.40),  # ~40% marginal rate
            (52096, 62096, 0.41),  # ~41% marginal rate
            (62096, 68480, 0.42),  # ~42% marginal rate (approaching flat 42%)
            (68480, 277825, 0.42),  # 42% flat rate
            (277825, float("inf"), 0.45),  # 45% top rate
        ]

        # Solidarity surcharge threshold
        self.solidarity_surcharge_threshold = Decimal("1000")

        # Social security rates (employee portion) and ceilings for 2024
        self.social_security_rates = {
            "pension": {
                "rate": Decimal("0.093"),  # 9.3% pension insurance
                "ceiling": Decimal("96000"),  # Annual ceiling (West Germany 2024)
            },
            "health": {
                "rate": Decimal(
                    "0.091"
                ),  # 7.3% base + 1.6% average additional = 8.9% (using 9.1% for accuracy)
                "ceiling": Decimal("62100"),  # Annual ceiling (2024)
            },
            "unemployment": {
                "rate": Decimal("0.013"),  # 1.3% unemployment insurance (2024)
                "ceiling": Decimal("96000"),  # Annual ceiling (West Germany 2024)
            },
            "long_term_care": {
                "rate": Decimal(
                    "0.02"
                ),  # 2.0% long-term care insurance (1.7% base + 0.3% for childless over 23)
                "ceiling": Decimal("62100"),  # Annual ceiling (2024)
            },
        }

        # Solidarity surcharge rate
        self.solidarity_rate = Decimal("0.055")  # 5.5%

    def calculate_net_salary(self) -> TaxResult:
        """Calculate net salary for German salaried employee."""
        result = self._create_base_result()

        # Calculate social security contributions (with ceilings)
        total_social_security = Decimal("0")
        for name, config in self.social_security_rates.items():
            rate = config["rate"]
            ceiling = config["ceiling"]
            # Apply ceiling
            contribution_base = min(self.gross_salary, ceiling)
            amount = contribution_base * rate

            result.add_deduction(
                Deduction(
                    name=f"{name.title()} Insurance",
                    amount=amount,
                    rate=rate,
                    description=f"Mandatory {name} insurance contribution",
                    calculation_details=f"{contribution_base:,.0f} × {rate:.1%} = {amount:,.0f}"
                    + (f" (capped at €{ceiling:,.0f})" if self.gross_salary > ceiling else ""),
                )
            )
            total_social_security += amount

        # Calculate taxable income (gross - social security)
        taxable_income = self.gross_salary - total_social_security
        result.tax_base = taxable_income

        # Calculate progressive income tax using brackets
        income_tax = self._calculate_progressive_tax(taxable_income, result)

        # Add income tax as deduction
        result.add_deduction(
            Deduction(
                name="Income Tax",
                amount=income_tax,
                rate=income_tax / taxable_income if taxable_income > 0 else Decimal("0"),
                description="Progressive income tax",
                calculation_details=f"Total tax from all applicable brackets = {income_tax:,.0f}",
            )
        )

        # Calculate solidarity surcharge
        solidarity_surcharge = Decimal("0")
        if income_tax > self.solidarity_surcharge_threshold:
            solidarity_surcharge = income_tax * self.solidarity_rate
            result.add_deduction(
                Deduction(
                    name="Solidarity Surcharge",
                    amount=solidarity_surcharge,
                    rate=self.solidarity_rate,
                    description="Solidarity surcharge on income tax",
                    calculation_details=f"{income_tax:,.0f} × {self.solidarity_rate:.1%} = {solidarity_surcharge:,.0f}",
                )
            )

        # Calculate final net salary
        result.net_salary = self.gross_salary - result.total_deductions

        # Add calculation explanations
        result.calculation_explanations = {
            "tax_base": f"Taxable income = Gross salary - Social security contributions = {self.gross_salary:,.0f} - {total_social_security:,.0f} = {taxable_income:,.0f}",
            "income_tax": "Progressive income tax calculated on taxable income using German tax brackets",
            "social_security": "Social security contributions calculated on gross salary at statutory rates",
            "solidarity_surcharge": f"5.5% surcharge on income tax above {self.solidarity_surcharge_threshold:,.0f}",
        }

        return result

    def _calculate_progressive_tax(self, taxable_income: Decimal, result: TaxResult) -> Decimal:
        """Calculate progressive income tax and populate tax brackets."""
        total_tax = Decimal("0")
        remaining_income = taxable_income

        for lower, upper, rate in self.tax_brackets:
            if remaining_income <= 0:
                break

            lower_bound = Decimal(str(lower))
            upper_bound = Decimal(str(upper)) if upper != float("inf") else taxable_income
            bracket_rate = Decimal(str(rate))

            # Calculate taxable amount in this bracket
            taxable_in_bracket = min(remaining_income, upper_bound - lower_bound)

            if taxable_in_bracket > 0:
                tax_in_bracket = taxable_in_bracket * bracket_rate
                total_tax += tax_in_bracket

                # Add bracket to result
                bracket = TaxBracket(
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    rate=bracket_rate,
                    taxable_amount=taxable_in_bracket,
                    tax_amount=tax_in_bracket,
                )
                result.income_tax_brackets.append(bracket)

                remaining_income -= taxable_in_bracket

        return total_tax

    def get_description(self) -> str:
        """Get description of German tax regime."""
        return """
        German Salaried Employee Tax Regime (Tax Class 1):

        This calculation applies to single employees without children in Germany.

        Key Features:
        - Progressive income tax with tax-free allowance of €12,096
        - Mandatory social security contributions (pension, health, unemployment, long-term care)
        - Solidarity surcharge (5.5%) on income tax above €19,450
        - Social security contributions are deducted from gross salary before income tax calculation

        Tax Brackets (2024/2025, approximate marginal rates in 10k increments):
        - 0% on income up to €12,096 (tax-free allowance)
        - 24% on income €12,096 - €22,096
        - 32% on income €22,096 - €32,096
        - 37% on income €32,096 - €42,096
        - 40% on income €42,096 - €52,096
        - 41% on income €52,096 - €62,096
        - 42% on income €62,096 - €68,480
        - 42% on income €68,480 - €277,825
        - 45% on income above €277,825

        Social Security Rates (Employee Portion, 2024):
        - Pension Insurance: 9.3% (capped at €96,000)
        - Health Insurance: ~9.1% (7.3% base + ~1.8% average additional, capped at €62,100)
        - Unemployment Insurance: 1.3% (capped at €96,000)
        - Long-term Care Insurance: 2.0% (1.7% base + 0.3% childless surcharge, capped at €62,100)

        Note: Calculations use annual tax formula. Monthly calculations may differ slightly due to rounding.
        """
