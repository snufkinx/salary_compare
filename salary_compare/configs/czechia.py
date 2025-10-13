"""Czechia tax regime configurations."""

from decimal import Decimal

from ..models.config import DeductionConfig, TaxBracketConfig, TaxRegimeConfig
from ..models.enums import Country, Currency, DeductionBase, EmploymentType
from ..services.currency import get_currency_converter
from ..strategies import (
    FlatRateDeduction,
    FlatRateExpenseTaxBase,
    PercentageOfTaxBaseDeduction,
    ProgressiveTaxDeduction,
    StandardTaxBase,
)


def create_czechia_salaried_config() -> TaxRegimeConfig:
    """Create configuration for Czechia salaried employee."""

    # Get currency converter for thresholds
    converter = get_currency_converter(from_currency="CZK", to_currency="EUR")

    # Tax brackets
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), converter.convert(Decimal("1867728")), Decimal("0.15")),
        TaxBracketConfig(converter.convert(Decimal("1867728")), Decimal("inf"), Decimal("0.23")),
    ]

    config = TaxRegimeConfig(
        country=Country.CZECHIA,
        employment_type=EmploymentType.SALARIED,
        local_currency=Currency.CZK,
        threshold_currency=Currency.CZK,
        title="Czechia Salaried Employee",
        description="""
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
        """,
    )

    # Tax base = Gross salary
    config.tax_base_strategy = StandardTaxBase()

    # Deduction strategies
    config.deduction_strategies = [
        # Social security and health insurance (on gross)
        FlatRateDeduction(
            DeductionConfig(
                name="Social Security",
                description="Mandatory social security contribution",
                rate=Decimal("0.065"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        FlatRateDeduction(
            DeductionConfig(
                name="Health Insurance",
                description="Mandatory health insurance contribution",
                rate=Decimal("0.045"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Income tax (on gross salary)
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Two-tier income tax",
                rate=Decimal("0"),
                applies_to=DeductionBase.GROSS,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


def create_czechia_freelancer_config() -> TaxRegimeConfig:
    """Create configuration for Czechia freelancer (60/40 rule)."""

    # Get currency converter for thresholds
    converter = get_currency_converter(from_currency="CZK", to_currency="EUR")

    # Tax brackets (same as salaried)
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), converter.convert(Decimal("1867728")), Decimal("0.15")),
        TaxBracketConfig(converter.convert(Decimal("1867728")), Decimal("inf"), Decimal("0.23")),
    ]

    # Taxpayer discount
    taxpayer_discount = converter.convert(Decimal("30840"))

    # Expense cap
    expense_cap = converter.convert(Decimal("2000000"))

    config = TaxRegimeConfig(
        country=Country.CZECHIA,
        employment_type=EmploymentType.FREELANCER,
        local_currency=Currency.CZK,
        threshold_currency=Currency.CZK,
        title="Czechia Freelancer",
        description=f"""
        Czechia Freelancer Tax Regime (60/40 Rule):

        This calculation applies to freelancers in the Czech Republic using the 60/40 tax method.

        Key Features:
        - 60% of gross income considered as business expenses (up to CZK 2,000,000)
        - 40% of gross income is taxable income (for income up to cap)
        - Income above CZK 2,000,000 (~€{expense_cap:,.0f}) is 100% taxable
        - Standard taxpayer discount of €{taxpayer_discount:,.0f} (CZK 30,840)
        - Social security and health insurance calculated on 50% of taxable income

        Tax Calculation:
        - Taxable income: 40% of gross income (up to CZK 2M cap)
        - Income above cap: 100% taxable (no expense deduction)
        - Income tax: 15% on taxable income
        - Standard taxpayer discount: €{taxpayer_discount:,.0f} (CZK 30,840, reduces income tax)

        Mandatory Contributions:
        - Social Security: 29.2% on 50% of taxable income
        - Health Insurance: 13.5% on 50% of taxable income

        Business Expenses:
        - 60% of gross income is automatically considered as business expenses
        - No need to provide receipts for expenses up to this amount
        - Expense deduction capped at CZK 2,000,000 annually

        This method is popular among freelancers as it simplifies tax filing and provides
        significant tax savings compared to the standard tax regime.
        """,
    )

    # Tax base = 40% of gross (with 2M CZK cap)
    config.tax_base_strategy = FlatRateExpenseTaxBase(
        taxable_rate=Decimal("0.40"), expense_cap=expense_cap
    )

    # Deduction strategies
    config.deduction_strategies = [
        # Income tax on taxable income (40% of gross) with discount
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Income tax on 40% of gross income with standard discount",
                rate=Decimal("0"),
                applies_to=DeductionBase.TAXABLE,
            ),
            brackets=tax_brackets,
            discount=taxpayer_discount,
        ),
        # Social security on 50% of taxable income
        PercentageOfTaxBaseDeduction(
            config=DeductionConfig(
                name="Social Security",
                description="Social security contribution on 50% of taxable income",
                rate=Decimal("0.292"),
                applies_to=DeductionBase.TAXABLE,
            ),
            base_multiplier=Decimal("0.50"),
        ),
        # Health insurance on 50% of taxable income
        PercentageOfTaxBaseDeduction(
            config=DeductionConfig(
                name="Health Insurance",
                description="Health insurance contribution on 50% of taxable income",
                rate=Decimal("0.135"),
                applies_to=DeductionBase.TAXABLE,
            ),
            base_multiplier=Decimal("0.50"),
        ),
    ]

    return config


# Export configs
CZECHIA_SALARIED = create_czechia_salaried_config()
CZECHIA_FREELANCER = create_czechia_freelancer_config()
