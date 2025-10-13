"""Portugal tax regime configurations."""

from decimal import Decimal

from ..models.config import DeductionConfig, TaxBracketConfig, TaxRegimeConfig
from ..models.enums import Country, Currency, DeductionBase, EmploymentType
from ..strategies import (
    FlatRateDeduction,
    PercentageOfTaxBaseDeduction,
    ProgressiveTaxDeduction,
    StandardTaxBase,
)


def create_portugal_salaried_config() -> TaxRegimeConfig:
    """Create configuration for Portuguese salaried employee."""

    # Portuguese IRS tax brackets (2024)
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), Decimal("7703"), Decimal("0.1325")),  # 13.25%
        TaxBracketConfig(Decimal("7703"), Decimal("11623"), Decimal("0.18")),  # 18%
        TaxBracketConfig(Decimal("11623"), Decimal("16472"), Decimal("0.23")),  # 23%
        TaxBracketConfig(Decimal("16472"), Decimal("21321"), Decimal("0.26")),  # 26%
        TaxBracketConfig(Decimal("21321"), Decimal("27146"), Decimal("0.3275")),  # 32.75%
        TaxBracketConfig(Decimal("27146"), Decimal("39791"), Decimal("0.37")),  # 37%
        TaxBracketConfig(Decimal("39791"), Decimal("51997"), Decimal("0.435")),  # 43.5%
        TaxBracketConfig(Decimal("51997"), Decimal("81199"), Decimal("0.45")),  # 45%
        TaxBracketConfig(Decimal("81199"), Decimal("inf"), Decimal("0.48")),  # 48%
    ]

    config = TaxRegimeConfig(
        country=Country.PORTUGAL,
        employment_type=EmploymentType.SALARIED,
        local_currency=Currency.EUR,
        threshold_currency=Currency.EUR,
        title="Portugal Salaried Employee",
        description="""
        Portugal Salaried Employee Tax Regime (Standard IRS):

        This calculation applies to salaried employees in Portugal under the standard tax regime.

        Key Features:
        - Progressive income tax (IRS) with 9 tax brackets
        - Social Security contributions (TSU)
        - No special tax schemes (NHR) applied - standard regime only

        Tax Brackets (IRS 2024):
        - 13.25% on income up to €7,703
        - 18% on income €7,703 - €11,623
        - 23% on income €11,623 - €16,472
        - 26% on income €16,472 - €21,321
        - 32.75% on income €21,321 - €27,146
        - 37% on income €27,146 - €39,791
        - 43.5% on income €39,791 - €51,997
        - 45% on income €51,997 - €81,199
        - 48% on income above €81,199

        Social Security (TSU - Employee Portion, 2024):
        - 11% of gross salary (employee contribution)
        - Employer pays additional 23.75%

        Note: Portugal has relatively high progressive taxation compared to Eastern European countries,
        but offers good quality of life, EU membership, and access to Atlantic markets.
        """,
    )

    config.tax_base_strategy = StandardTaxBase()

    config.deduction_strategies = [
        # Social security (TSU)
        FlatRateDeduction(
            DeductionConfig(
                name="Social Security (TSU)",
                description="Social security contributions (employee portion)",
                rate=Decimal("0.11"),  # 11%
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Income tax (IRS)
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax (IRS)",
                description="Progressive income tax",
                rate=Decimal("0"),
                applies_to=DeductionBase.GROSS,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


def create_portugal_freelancer_config() -> TaxRegimeConfig:
    """Create configuration for Portuguese freelancer (simplified regime)."""

    # Portuguese freelancer simplified regime
    # Can deduct 75% of income as deemed expenses for certain activities (IT, consulting)
    # So effective taxable income = 25% of gross

    # IRS tax brackets (same as salaried)
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), Decimal("7703"), Decimal("0.1325")),
        TaxBracketConfig(Decimal("7703"), Decimal("11623"), Decimal("0.18")),
        TaxBracketConfig(Decimal("11623"), Decimal("16472"), Decimal("0.23")),
        TaxBracketConfig(Decimal("16472"), Decimal("21321"), Decimal("0.26")),
        TaxBracketConfig(Decimal("21321"), Decimal("27146"), Decimal("0.3275")),
        TaxBracketConfig(Decimal("27146"), Decimal("39791"), Decimal("0.37")),
        TaxBracketConfig(Decimal("39791"), Decimal("51997"), Decimal("0.435")),
        TaxBracketConfig(Decimal("51997"), Decimal("81199"), Decimal("0.45")),
        TaxBracketConfig(Decimal("81199"), Decimal("inf"), Decimal("0.48")),
    ]

    config = TaxRegimeConfig(
        country=Country.PORTUGAL,
        employment_type=EmploymentType.FREELANCER,
        local_currency=Currency.EUR,
        threshold_currency=Currency.EUR,
        title="Portugal Freelancer",
        description="""
        Portugal Freelancer Tax Regime (Simplified Regime - Recibos Verdes):

        This applies to freelancers under the simplified tax regime (not NHR or special schemes).

        IMPORTANT: This calculation uses coefficient 0.75 for SERVICES (IT, consulting, liberal professions).
        - Services/Liberal professions: 75% deemed expenses → 25% taxable
        - Commercial activities would have: 25% deemed expenses → 75% taxable
        - Industrial activities would have: 50% deemed expenses → 50% taxable

        Key Features (for IT/Consulting/Services):
        - 75% deemed expenses automatically deducted
        - Only 25% of income is subject to IRS (income tax)
        - Progressive IRS tax applied to 25% taxable portion
        - Social security at 21.4% on 70% of gross income

        Tax Calculation (Simplified Regime for IT/Consulting):
        - Deemed expenses: 75% of income (automatic deduction)
        - Taxable income: 25% of gross income
        - IRS tax: Applied progressively on 25% of income
        - Social security: 21.4% on 70% of income (70% = social security base)

        Example for €100,000:
        - Taxable for IRS: €25,000 (25% of €100k)
        - Social security base: €70,000 (70% of €100k)
        - Social security contribution: €70,000 × 21.4% = €14,980

        Social Security (Freelancer, 2024):
        - 21.4% on 70% of gross income
        - This provides pension, healthcare, and unemployment coverage

        Note: The simplified regime with 75% deemed expenses is very favorable for
        service providers (IT, consulting, design, etc.). Different activities have
        different deemed expense percentages (25%, 50%, or 75%).
        """,
    )

    # For Portuguese freelancers, we'll use a custom tax base strategy
    # Tax base for IRS = 25% of gross (after 75% deemed expenses)
    from ..strategies.tax_base import FlatRateExpenseTaxBase

    config.tax_base_strategy = FlatRateExpenseTaxBase(
        taxable_rate=Decimal("0.25"),  # 25% taxable (75% expenses)
        expense_cap=Decimal("999999999"),  # No cap
    )

    config.deduction_strategies = [
        # Social security on 70% of gross
        PercentageOfTaxBaseDeduction(
            config=DeductionConfig(
                name="Social Security",
                description="Social security on 70% of gross income (freelancer rate)",
                rate=Decimal("0.214"),  # 21.4%
                applies_to=DeductionBase.GROSS,
            ),
            base_multiplier=Decimal("0.70"),  # 70% of gross
        ),
        # Income tax on 25% of gross (after 75% deemed expenses)
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax (IRS)",
                description="Progressive income tax on 25% of income (75% deemed expenses)",
                rate=Decimal("0"),
                applies_to=DeductionBase.TAXABLE,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


# Export configs
PORTUGAL_SALARIED = create_portugal_salaried_config()
PORTUGAL_FREELANCER = create_portugal_freelancer_config()
