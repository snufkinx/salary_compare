"""Bulgaria tax regime configurations."""

from decimal import Decimal

from ..models.config import DeductionConfig, TaxBracketConfig, TaxRegimeConfig
from ..models.enums import Country, Currency, DeductionBase, EmploymentType
from ..services.currency import get_currency_converter
from ..strategies import FlatRateDeduction, ProgressiveTaxDeduction, StandardTaxBase


def create_bulgaria_freelancer_config() -> TaxRegimeConfig:
    """Create configuration for Bulgarian self-employed (Едноличен търговец - ET)."""

    # Get currency converter
    converter = get_currency_converter(from_currency="BGN", to_currency="EUR")

    # Bulgaria has a flat 10% income tax
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), Decimal("inf"), Decimal("0.10")),  # 10% flat
    ]

    config = TaxRegimeConfig(
        country=Country.BULGARIA,
        employment_type=EmploymentType.FREELANCER,
        local_currency=Currency.BGN,
        threshold_currency=Currency.BGN,
        title="Bulgaria Freelancer",
        description="""
        Bulgaria Freelancer Tax Regime (Self-Employed - Едноличен търговец):

        This applies to freelancers registered as sole traders (ET) in Bulgaria.

        IMPORTANT: Bulgaria has one of the EU's lowest and simplest tax systems.

        Key Features:
        - **10% flat income tax** on net profit (after expenses)
        - Simple, predictable taxation
        - EU member with access to European markets
        - Can deduct business expenses from revenue

        Tax Structure:
        - Income tax: 10% flat rate on taxable profit
        - Social security: ~19.8% on self-declared income (min ~€300, max ~€3,000/month)
        - Health insurance: ~8% on self-declared income (min ~€50/month)

        Total effective rate (approximate):
        - On €100,000 gross: ~40% (10% income + ~30% social/health on declared income)
        - Freelancers can optimize by declaring minimum social security base

        Calculation shown:
        - This shows 10% income tax + social security at ~25% effective rate
        - Assumes freelancer declares ~€50k for social security (common strategy)

        Benefits:
        - Flat 10% income tax (lowest in EU)
        - Predictable taxation
        - Low cost of living
        - Strategic location for EU market access
        - Bulgarian lev (BGN) pegged to EUR (1.95583 BGN = 1 EUR)

        Note: This regime is popular among digital nomads and EU remote workers.
        """,
    )

    config.tax_base_strategy = StandardTaxBase()

    config.deduction_strategies = [
        # Social security (on declared income basis, simplified)
        FlatRateDeduction(
            DeductionConfig(
                name="Social Security",
                description="Social security contributions (self-declared income basis)",
                rate=Decimal("0.198"),  # 19.8%
                ceiling=converter.convert(Decimal("72000")),  # ~€36k annual ceiling
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Health insurance
        FlatRateDeduction(
            DeductionConfig(
                name="Health Insurance",
                description="Health insurance contributions (self-declared income basis)",
                rate=Decimal("0.08"),  # 8%
                ceiling=converter.convert(Decimal("72000")),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Income tax (10% flat)
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Flat 10% income tax on profit",
                rate=Decimal("0"),
                applies_to=DeductionBase.GROSS,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


# Export configs
BULGARIA_FREELANCER = create_bulgaria_freelancer_config()
