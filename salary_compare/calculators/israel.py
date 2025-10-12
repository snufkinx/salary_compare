"""Israel tax calculator for salaried employees."""

from decimal import Decimal

from ..models.employee import SalariedEmployee
from ..models.tax_result import Deduction, TaxBracket, TaxResult


class SalariedEmployeeIsrael(SalariedEmployee):
    """Israel salaried employee tax calculator."""

    def __init__(self, gross_salary: Decimal):
        super().__init__(gross_salary, "Israel")

        # 2024 Israel tax brackets (in ILS, will convert to EUR)
        # Based on typical Israeli tax structure
        # Note: Using approximate EUR conversion rate of 1 EUR = 4 ILS
        self.tax_brackets_ils = [
            (0, 83040, 0.10),  # 10% up to ₪83,040 (~€20,760)
            (83040, 119040, 0.14),  # 14% on ₪83,041 - ₪119,040 (~€20,760 - €29,760)
            (119040, 185040, 0.20),  # 20% on ₪119,041 - ₪185,040 (~€29,760 - €46,260)
            (185040, 260040, 0.31),  # 31% on ₪185,041 - ₪260,040 (~€46,260 - €65,010)
            (260040, 560280, 0.35),  # 35% on ₪260,041 - ₪560,280 (~€65,010 - €140,070)
            (560280, 721560, 0.47),  # 47% on ₪560,281 - ₪721,560 (~€140,070 - €180,390)
            (721560, float("inf"), 0.50),  # 50% above ₪721,560 (~€180,390)
        ]

        # Convert to EUR (approximate: 1 EUR = 4 ILS)
        self.eur_to_ils = Decimal("4.0")
        self.tax_brackets_eur = [
            (Decimal(str(lower / 4)), Decimal(str(upper / 4)), Decimal(str(rate)))
            for lower, upper, rate in self.tax_brackets_ils
        ]

        # Pension and savings rates (employee portion)
        # Pension (Gemel Pensia) - mandatory for most employees
        self.pension_rate = Decimal("0.06")  # 6% employee contribution

        # Keren Hishtalmut (Advanced Training Fund) - common benefit
        self.keren_hishtalmut_rate = Decimal("0.025")  # 2.5% employee contribution
        # Tax-advantaged cap: ₪188,544 annually (₪15,712 monthly)
        # Convert to EUR: ₪188,544 / 4 = €47,136
        self.keren_hishtalmut_cap = Decimal("47136")  # Annual cap in EUR

        # National Insurance (Bituach Leumi) - employee portion
        self.national_insurance_rate = Decimal("0.04")  # ~4% (varies by income)

        # Health Tax (Mas Briut) - employee portion
        self.health_tax_rate = Decimal("0.05")  # ~5% (varies by income)

    def calculate_net_salary(self) -> TaxResult:
        """Calculate net salary for Israeli salaried employee."""
        result = self._create_base_result()

        # Calculate National Insurance (Bituach Leumi)
        national_insurance = self.gross_salary * self.national_insurance_rate
        result.add_deduction(
            Deduction(
                name="National Insurance",
                amount=national_insurance,
                rate=self.national_insurance_rate,
                description="Mandatory national insurance contribution (Bituach Leumi)",
                calculation_details=f"{self.gross_salary:,.0f} × {self.national_insurance_rate:.1%} = {national_insurance:,.0f}",
            )
        )

        # Calculate Health Tax (Mas Briut)
        health_tax = self.gross_salary * self.health_tax_rate
        result.add_deduction(
            Deduction(
                name="Health Tax",
                amount=health_tax,
                rate=self.health_tax_rate,
                description="Mandatory health tax contribution (Mas Briut)",
                calculation_details=f"{self.gross_salary:,.0f} × {self.health_tax_rate:.1%} = {health_tax:,.0f}",
            )
        )

        # Calculate Pension contribution
        pension = self.gross_salary * self.pension_rate
        result.add_deduction(
            Deduction(
                name="Pension",
                amount=pension,
                rate=self.pension_rate,
                description="Pension fund contribution (Gemel Pensia)",
                calculation_details=f"{self.gross_salary:,.0f} × {self.pension_rate:.1%} = {pension:,.0f}",
            )
        )

        # Calculate Keren Hishtalmut contribution (capped for tax advantages)
        # Cap is ₪188,544 annually (~€47,136)
        keren_base = min(self.gross_salary, self.keren_hishtalmut_cap)
        keren_hishtalmut = keren_base * self.keren_hishtalmut_rate
        
        cap_note = f" (capped at €{self.keren_hishtalmut_cap:,.0f})" if self.gross_salary > self.keren_hishtalmut_cap else ""
        result.add_deduction(
            Deduction(
                name="Keren Hishtalmut",
                amount=keren_hishtalmut,
                rate=self.keren_hishtalmut_rate,
                description="Advanced training fund contribution (Keren Hishtalmut)",
                calculation_details=f"{keren_base:,.0f} × {self.keren_hishtalmut_rate:.1%} = {keren_hishtalmut:,.0f}{cap_note}",
            )
        )

        # Calculate taxable income (gross salary for income tax purposes)
        taxable_income = self.gross_salary
        result.tax_base = taxable_income

        # Calculate progressive income tax
        income_tax = self._calculate_progressive_tax(taxable_income, result)

        # Calculate final net salary
        result.net_salary = self.gross_salary - result.total_deductions

        # Add calculation explanations
        result.calculation_explanations = {
            "tax_base": f"Taxable income = Gross salary = {self.gross_salary:,.0f}",
            "income_tax": "Progressive income tax using Israeli tax brackets",
            "national_insurance": f"National insurance at {self.national_insurance_rate:.1%} on gross salary",
            "health_tax": f"Health tax at {self.health_tax_rate:.1%} on gross salary",
            "pension": f"Pension contribution at {self.pension_rate:.1%} on gross salary",
            "keren_hishtalmut": f"Keren Hishtalmut at {self.keren_hishtalmut_rate:.1%} on gross salary",
        }

        return result

    def _calculate_progressive_tax(self, taxable_income: Decimal, result: TaxResult) -> Decimal:
        """Calculate progressive income tax and populate tax brackets."""
        total_tax = Decimal("0")
        remaining_income = taxable_income

        for lower, upper, rate in self.tax_brackets_eur:
            if remaining_income <= 0:
                break

            # Calculate taxable amount in this bracket
            bracket_lower = lower
            bracket_upper = upper if upper != Decimal("inf") else taxable_income
            taxable_in_bracket = min(remaining_income, bracket_upper - bracket_lower)

            if taxable_in_bracket > 0:
                tax_in_bracket = taxable_in_bracket * rate
                total_tax += tax_in_bracket

                # Add bracket to result
                bracket = TaxBracket(
                    lower_bound=bracket_lower,
                    upper_bound=bracket_upper,
                    rate=rate,
                    taxable_amount=taxable_in_bracket,
                    tax_amount=tax_in_bracket,
                )
                result.income_tax_brackets.append(bracket)

                remaining_income -= taxable_in_bracket

        # Add total income tax as deduction
        result.add_deduction(
            Deduction(
                name="Income Tax",
                amount=total_tax,
                rate=total_tax / taxable_income if taxable_income > 0 else Decimal("0"),
                description="Progressive income tax",
                calculation_details=f"Total tax from all applicable brackets = {total_tax:,.0f}",
            )
        )

        return total_tax

    def get_description(self) -> str:
        """Get description of Israeli tax regime."""
        return """
        Israeli Salaried Employee Tax Regime:

        This calculation applies to salaried employees in Israel.

        Key Features:
        - Progressive income tax with 7 tax brackets (10% to 50%)
        - Mandatory National Insurance (Bituach Leumi)
        - Mandatory Health Tax (Mas Briut)
        - Pension fund contributions (Gemel Pensia)
        - Advanced training fund (Keren Hishtalmut)

        Tax Brackets (2024, approximate EUR values):
        - 10% on income up to €20,760 (₪83,040)
        - 14% on income €20,761 - €29,760 (₪83,041 - ₪119,040)
        - 20% on income €29,761 - €46,260 (₪119,041 - ₪185,040)
        - 31% on income €46,261 - €65,010 (₪185,041 - ₪260,040)
        - 35% on income €65,011 - €140,070 (₪260,041 - ₪560,280)
        - 47% on income €140,071 - €180,390 (₪560,281 - ₪721,560)
        - 50% on income above €180,390 (₪721,560+)

        Mandatory Contributions (Employee Portion):
        - National Insurance: ~4% of gross salary
        - Health Tax: ~5% of gross salary
        - Pension: 6% of gross salary
        - Keren Hishtalmut: 2.5% of gross salary (capped at €47,136 / ₪188,544 annually)

        Note: 
        - Employers also contribute to pension (6.5%) and Keren Hishtalmut (7.5%)
        - Keren Hishtalmut contributions above the cap are subject to income tax
        - These calculations use approximate EUR/ILS conversion (1 EUR = 4 ILS)
        """
