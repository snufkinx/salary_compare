"""Germany tax regime configurations."""

from decimal import Decimal

from ..models.config import DeductionConfig, TaxBracketConfig, TaxRegimeConfig
from ..models.enums import Country, Currency, DeductionBase, EmploymentType
from ..strategies import (
    AfterSocialSecurityTaxBase,
    ConditionalDeduction,
    FlatRateDeduction,
    ProgressiveTaxDeduction,
)


def create_germany_salaried_config() -> TaxRegimeConfig:
    """Create configuration for German salaried employee."""

    # Tax brackets (discrete, in 10k increments)
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), Decimal("12096"), Decimal("0.00")),
        TaxBracketConfig(Decimal("12096"), Decimal("22096"), Decimal("0.24")),
        TaxBracketConfig(Decimal("22096"), Decimal("32096"), Decimal("0.32")),
        TaxBracketConfig(Decimal("32096"), Decimal("42096"), Decimal("0.37")),
        TaxBracketConfig(Decimal("42096"), Decimal("52096"), Decimal("0.40")),
        TaxBracketConfig(Decimal("52096"), Decimal("62096"), Decimal("0.41")),
        TaxBracketConfig(Decimal("62096"), Decimal("68480"), Decimal("0.42")),
        TaxBracketConfig(Decimal("68480"), Decimal("277825"), Decimal("0.42")),
        TaxBracketConfig(Decimal("277825"), Decimal("inf"), Decimal("0.45")),
    ]

    config = TaxRegimeConfig(
        country=Country.GERMANY,
        employment_type=EmploymentType.SALARIED,
        local_currency=Currency.EUR,
        threshold_currency=Currency.EUR,
        description="""
        German Salaried Employee Tax Regime (Tax Class 1):

        This calculation applies to single employees without children in Germany.

        Key Features:
        - Progressive income tax with tax-free allowance of €12,096
        - Mandatory social security contributions (pension, health, unemployment, long-term care)
        - Solidarity surcharge (5.5%) on income tax above €1,000
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
        """,
    )

    # Tax base = Gross - Social Security
    config.tax_base_strategy = AfterSocialSecurityTaxBase()

    # Deduction strategies (in order of application)
    config.deduction_strategies = [
        # Social security contributions (on gross, before tax base)
        FlatRateDeduction(
            DeductionConfig(
                name="Pension Insurance",
                description="Mandatory pension insurance contribution",
                rate=Decimal("0.093"),
                ceiling=Decimal("96000"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        FlatRateDeduction(
            DeductionConfig(
                name="Health Insurance",
                description="Mandatory health insurance contribution",
                rate=Decimal("0.091"),
                ceiling=Decimal("62100"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        FlatRateDeduction(
            DeductionConfig(
                name="Unemployment Insurance",
                description="Mandatory unemployment insurance contribution",
                rate=Decimal("0.013"),
                ceiling=Decimal("96000"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        FlatRateDeduction(
            DeductionConfig(
                name="Long_Term_Care Insurance",
                description="Mandatory long_term_care insurance contribution",
                rate=Decimal("0.02"),
                ceiling=Decimal("62100"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Income tax (on taxable income = gross - social security)
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Progressive income tax",
                rate=Decimal("0"),  # Not used for progressive
                applies_to=DeductionBase.TAXABLE,
            ),
            brackets=tax_brackets,
        ),
        # Solidarity surcharge (on income tax, if above threshold)
        ConditionalDeduction(
            config=DeductionConfig(
                name="Solidarity Surcharge",
                description="Solidarity surcharge on income tax",
                rate=Decimal("0.055"),
                applies_to=DeductionBase.INCOME_TAX,
            ),
            condition=lambda ctx: ctx.get("income_tax_amount", Decimal("0")) > Decimal("1000"),
        ),
    ]

    return config


# Export default config
GERMANY_SALARIED = create_germany_salaried_config()
