"""Czechia tax calculators for salaried employees and freelancers."""

from decimal import Decimal

from ..models.employee import Freelancer, SalariedEmployee
from ..models.tax_result import Deduction, TaxBracket, TaxResult
from ..services.currency import get_currency_converter


class SalariedEmployeeCzechia(SalariedEmployee):
    """Czechia salaried employee tax calculator."""

    def __init__(self, gross_salary: Decimal):
        super().__init__(gross_salary, "Czechia")

        # Initialize currency converter (CZK to EUR)
        self.currency_converter = get_currency_converter(from_currency="CZK", to_currency="EUR")

        # 2024 Czechia tax rates (original in CZK, converted to EUR dynamically)
        # Original threshold: CZK 1,867,728
        self.income_tax_threshold = self.currency_converter.convert(Decimal("1867728"))
        self.income_tax_rate_low = Decimal("0.15")  # 15% on income up to threshold
        self.income_tax_rate_high = Decimal("0.23")  # 23% on income above threshold

        # Social security rates (employee portion)
        self.social_security_rate = Decimal("0.065")  # 6.5%
        self.health_insurance_rate = Decimal("0.045")  # 4.5%

    def calculate_net_salary(self) -> TaxResult:
        """Calculate net salary for Czech salaried employee."""
        result = self._create_base_result()

        # Set local currency info from converter
        result.local_currency = "CZK"
        result.local_currency_rate = Decimal("1") / self.currency_converter.rate

        # Calculate social security and health insurance (on gross salary)
        social_security = self.gross_salary * self.social_security_rate
        health_insurance = self.gross_salary * self.health_insurance_rate

        result.add_deduction(
            Deduction(
                name="Social Security",
                amount=social_security,
                rate=self.social_security_rate,
                description="Mandatory social security contribution",
                calculation_details=f"{self.gross_salary:,.0f} × {self.social_security_rate:.1%} = {social_security:,.0f}",
            )
        )

        result.add_deduction(
            Deduction(
                name="Health Insurance",
                amount=health_insurance,
                rate=self.health_insurance_rate,
                description="Mandatory health insurance contribution",
                calculation_details=f"{self.gross_salary:,.0f} × {self.health_insurance_rate:.1%} = {health_insurance:,.0f}",
            )
        )

        # Calculate taxable income (gross salary)
        taxable_income = self.gross_salary
        result.tax_base = taxable_income

        # Calculate income tax using two-tier system
        self._calculate_two_tier_tax(taxable_income, result)

        # Calculate final net salary
        result.net_salary = self.gross_salary - result.total_deductions

        # Add calculation explanations
        result.calculation_explanations = {
            "tax_base": f"Taxable income = Gross salary = {self.gross_salary:,.0f}",
            "income_tax": f"Two-tier income tax: 15% up to €{self.income_tax_threshold:,.0f}, 23% above",
            "social_security": f"Social security contribution at {self.social_security_rate:.1%} on gross salary",
            "health_insurance": f"Health insurance contribution at {self.health_insurance_rate:.1%} on gross salary",
        }

        return result

    def _calculate_two_tier_tax(self, taxable_income: Decimal, result: TaxResult) -> Decimal:
        """Calculate two-tier income tax and populate tax brackets."""
        total_tax = Decimal("0")

        # First bracket: 15% up to threshold
        if taxable_income > 0:
            amount_in_low_bracket = min(taxable_income, self.income_tax_threshold)
            tax_low_bracket = amount_in_low_bracket * self.income_tax_rate_low
            total_tax += tax_low_bracket

            bracket1 = TaxBracket(
                lower_bound=Decimal("0"),
                upper_bound=self.income_tax_threshold,
                rate=self.income_tax_rate_low,
                taxable_amount=amount_in_low_bracket,
                tax_amount=tax_low_bracket,
            )
            result.income_tax_brackets.append(bracket1)

        # Second bracket: 23% above threshold
        if taxable_income > self.income_tax_threshold:
            amount_in_high_bracket = taxable_income - self.income_tax_threshold
            tax_high_bracket = amount_in_high_bracket * self.income_tax_rate_high
            total_tax += tax_high_bracket

            bracket2 = TaxBracket(
                lower_bound=self.income_tax_threshold,
                upper_bound=Decimal("999999999"),
                rate=self.income_tax_rate_high,
                taxable_amount=amount_in_high_bracket,
                tax_amount=tax_high_bracket,
            )
            result.income_tax_brackets.append(bracket2)

        # Add total income tax as deduction
        result.add_deduction(
            Deduction(
                name="Income Tax",
                amount=total_tax,
                rate=total_tax / taxable_income if taxable_income > 0 else Decimal("0"),
                description="Two-tier income tax",
                calculation_details=f"15% on first {min(taxable_income, self.income_tax_threshold):,.0f}, 23% on remainder = {total_tax:,.0f}",
            )
        )

        return total_tax

    def get_description(self) -> str:
        """Get description of Czech salaried employee tax regime."""
        return """
        Czechia Salaried Employee Tax Regime:

        This calculation applies to salaried employees in the Czech Republic.

        Key Features:
        - Two-tier income tax system (15% and 23%)
        - Mandatory social security and health insurance contributions
        - Contributions and taxes calculated on gross salary

        Tax Rates:
        - 15% on income up to €76,798 (CZK 1,867,728)
        - 23% on income above €76,798

        Mandatory Contributions:
        - Social Security: 6.5% of gross salary
        - Health Insurance: 4.5% of gross salary

        Note: These rates apply to the employee portion only. Employers pay additional contributions.
        """


class FreelancerCzechia(Freelancer):
    """Czechia freelancer tax calculator using 60/40 rule."""

    def __init__(self, gross_salary: Decimal):
        super().__init__(gross_salary, "Czechia")

        # Initialize currency converter (CZK to EUR)
        self.currency_converter = get_currency_converter(from_currency="CZK", to_currency="EUR")

        # 60/40 rule: 60% expenses, 40% taxable income
        self.expense_rate = Decimal("0.60")
        self.taxable_rate = Decimal("0.40")

        # Cap for flat-rate expenses: CZK 2,000,000
        # Income above this cap is 100% taxable (no expense deduction)
        self.expense_cap_czk = Decimal("2000000")
        self.expense_cap_eur = self.currency_converter.convert(self.expense_cap_czk)

        # Tax rates on taxable income (40% of gross)
        # Same threshold as salaried employees: CZK 1,867,728
        self.income_tax_threshold = self.currency_converter.convert(Decimal("1867728"))
        self.income_tax_rate_low = Decimal("0.15")  # 15% on taxable income up to threshold
        self.income_tax_rate_high = Decimal("0.23")  # 23% on taxable income above threshold

        # Social security and health insurance calculated on 50% of taxable income (40% of gross)
        self.social_base_rate = Decimal("0.50")  # 50% of taxable income as base
        self.social_security_rate = Decimal("0.292")  # 29.2%
        self.health_insurance_rate = Decimal("0.135")  # 13.5%

        # Standard taxpayer discount (original: CZK 30,840, converted to EUR dynamically)
        self.taxpayer_discount = self.currency_converter.convert(Decimal("30840"))

    def _calculate_taxable_income(self, gross_salary: Decimal) -> tuple[Decimal, Decimal]:
        """
        Calculate taxable income with expense cap.

        Returns:
            tuple: (taxable_income, deductible_expenses)
        """
        if gross_salary <= self.expense_cap_eur:
            # Below cap: apply 60/40 rule
            deductible_expenses = gross_salary * self.expense_rate
            taxable_income = gross_salary * self.taxable_rate
        else:
            # Above cap: 60/40 rule applies only up to cap, rest is 100% taxable
            # Income up to cap: 40% taxable
            taxable_up_to_cap = self.expense_cap_eur * self.taxable_rate
            # Income above cap: 100% taxable
            income_above_cap = gross_salary - self.expense_cap_eur
            taxable_income = taxable_up_to_cap + income_above_cap
            # Deductible expenses only on income up to cap
            deductible_expenses = self.expense_cap_eur * self.expense_rate

        return taxable_income, deductible_expenses

    def calculate_net_salary(self) -> TaxResult:
        """Calculate net salary for Czech freelancer using 60/40 rule with expense cap."""
        result = self._create_base_result()

        # Set local currency info from converter
        result.local_currency = "CZK"
        result.local_currency_rate = Decimal("1") / self.currency_converter.rate

        # Calculate taxable income using 60/40 rule (with cap at 2M CZK)
        taxable_income, deductible_expenses = self._calculate_taxable_income(self.gross_salary)
        result.tax_base = taxable_income

        # Calculate income tax on taxable income (always 15% for freelancers under threshold)
        # For simplicity, freelancers typically stay in the 15% bracket
        income_tax_before_discount = taxable_income * self.income_tax_rate_low
        income_tax = max(Decimal("0"), income_tax_before_discount - self.taxpayer_discount)

        result.add_deduction(
            Deduction(
                name="Income Tax",
                amount=income_tax,
                rate=income_tax / taxable_income if taxable_income > 0 else Decimal("0"),
                description="Income tax on 40% of gross income with standard discount",
                calculation_details=f"Taxable income: {taxable_income:,.0f}, Tax: {income_tax_before_discount:,.0f}, Discount: {self.taxpayer_discount:,.0f}, Final tax: {income_tax:,.0f}",
            )
        )

        # Calculate social security (29.2% on 50% of taxable income)
        social_base = taxable_income * self.social_base_rate
        social_security = social_base * self.social_security_rate

        result.add_deduction(
            Deduction(
                name="Social Security",
                amount=social_security,
                rate=self.social_security_rate,
                description="Social security contribution on 50% of taxable income",
                calculation_details=f"Base: {taxable_income:,.0f} × {self.social_base_rate:.1%} = {social_base:,.0f}, Social security: {social_base:,.0f} × {self.social_security_rate:.1%} = {social_security:,.0f}",
            )
        )

        # Calculate health insurance (13.5% on 50% of gross income)
        health_insurance = social_base * self.health_insurance_rate

        result.add_deduction(
            Deduction(
                name="Health Insurance",
                amount=health_insurance,
                rate=self.health_insurance_rate,
                description="Health insurance contribution on 50% of taxable income",
                calculation_details=f"Base: {social_base:,.0f}, Health insurance: {social_base:,.0f} × {self.health_insurance_rate:.1%} = {health_insurance:,.0f}",
            )
        )

        # Add tax bracket information (same brackets as salaried, but applied to 40% of gross)
        # Note: The discount is applied to the total tax, not per bracket
        if taxable_income > 0:
            # First bracket: 15% up to threshold
            amount_in_low_bracket = min(taxable_income, self.income_tax_threshold)
            if amount_in_low_bracket > 0:
                tax_from_low_bracket = amount_in_low_bracket * self.income_tax_rate_low

                bracket1 = TaxBracket(
                    lower_bound=Decimal("0"),
                    upper_bound=self.income_tax_threshold,
                    rate=self.income_tax_rate_low,
                    taxable_amount=amount_in_low_bracket,
                    tax_amount=tax_from_low_bracket,
                )
                result.income_tax_brackets.append(bracket1)

            # Second bracket: 23% above threshold (if applicable)
            if taxable_income > self.income_tax_threshold:
                amount_in_high_bracket = taxable_income - self.income_tax_threshold
                tax_from_high_bracket = amount_in_high_bracket * self.income_tax_rate_high

                bracket2 = TaxBracket(
                    lower_bound=self.income_tax_threshold,
                    upper_bound=Decimal("999999999"),
                    rate=self.income_tax_rate_high,
                    taxable_amount=amount_in_high_bracket,
                    tax_amount=tax_from_high_bracket,
                )
                result.income_tax_brackets.append(bracket2)

        # Calculate final net salary
        result.net_salary = self.gross_salary - result.total_deductions

        # Add calculation explanations
        if self.gross_salary <= self.expense_cap_eur:
            expense_explanation = (
                f"60% of gross income ({deductible_expenses:,.0f}) considered as business expenses"
            )
            tax_base_explanation = f"Taxable income = Gross salary × 40% = {self.gross_salary:,.0f} × {self.taxable_rate:.1%} = {taxable_income:,.0f}"
        else:
            cap_czk = self.expense_cap_czk
            income_above_cap = self.gross_salary - self.expense_cap_eur
            expense_explanation = f"60% expense deduction capped at €{self.expense_cap_eur:,.0f} (CZK {cap_czk:,.0f}). Income above cap (€{income_above_cap:,.0f}) is 100% taxable"
            tax_base_explanation = f"Taxable income = (€{self.expense_cap_eur:,.0f} × 40%) + €{income_above_cap:,.0f} = {taxable_income:,.0f}"

        result.calculation_explanations = {
            "tax_base": tax_base_explanation,
            "income_tax": f"15% tax on taxable income with standard taxpayer discount of €{self.taxpayer_discount:,.0f}",
            "social_security": f"29.2% on 50% of taxable income = {taxable_income:,.0f} × {self.social_base_rate:.1%} × {self.social_security_rate:.1%}",
            "health_insurance": f"13.5% on 50% of taxable income = {taxable_income:,.0f} × {self.social_base_rate:.1%} × {self.health_insurance_rate:.1%}",
            "expenses": expense_explanation,
        }

        return result

    def get_description(self) -> str:
        """Get description of Czech freelancer tax regime."""
        return f"""
        Czechia Freelancer Tax Regime (60/40 Rule):

        This calculation applies to freelancers in the Czech Republic using the 60/40 tax method.

        Key Features:
        - 60% of gross income considered as business expenses (up to CZK 2,000,000)
        - 40% of gross income is taxable income (for income up to cap)
        - Income above CZK 2,000,000 (~€{self.expense_cap_eur:,.0f}) is 100% taxable
        - Standard taxpayer discount of €1,268 (CZK 30,840)
        - Social security and health insurance calculated on 50% of taxable income

        Tax Calculation:
        - Taxable income: 40% of gross income (up to CZK 2M cap)
        - Income above cap: 100% taxable (no expense deduction)
        - Income tax: 15% on taxable income
        - Standard taxpayer discount: €1,268 (CZK 30,840, reduces income tax)

        Mandatory Contributions:
        - Social Security: 29.2% on 50% of taxable income
        - Health Insurance: 13.5% on 50% of taxable income

        Business Expenses:
        - 60% of gross income is automatically considered as business expenses
        - No need to provide receipts for expenses up to this amount
        - Expense deduction capped at CZK 2,000,000 annually

        This method is popular among freelancers as it simplifies tax filing and provides
        significant tax savings compared to the standard tax regime.
        """
