"""Romania tax regime configurations."""

from decimal import Decimal

from ..models.config import DeductionConfig, TaxRegimeConfig
from ..models.enums import Country, Currency, DeductionBase, EmploymentType
from ..services.currency import get_currency_converter
from ..strategies import FlatRateDeduction, StandardTaxBase


def create_romania_freelancer_micro_config() -> TaxRegimeConfig:
    """Create configuration for Romanian freelancer using microenterprise regime."""

    # Get currency converter
    converter = get_currency_converter(from_currency="RON", to_currency="EUR")

    # Convert RON thresholds to EUR
    # Standard income threshold for micro: ~RON 500,000 (~€100k)
    threshold_eur = converter.convert(Decimal("500000"))

    config = TaxRegimeConfig(
        country=Country.ROMANIA,
        employment_type=EmploymentType.FREELANCER,
        local_currency=Currency.RON,
        threshold_currency=Currency.RON,
        description=f"""
        Romania Freelancer Tax Regime (Microenterprise - 1% Revenue Tax):

        This applies to IT freelancers and consultants operating as microenterprises (SRL-D).

        IMPORTANT: This is one of Europe's most tax-advantageous regimes for IT professionals.

        Key Features:
        - **1% flat tax on REVENUE** (not profit) - extremely low!
        - No income tax, no VAT (under threshold)
        - Minimal accounting requirements
        - Popular among IT contractors and consultants

        Eligibility Requirements:
        - Annual revenue under €{threshold_eur:,.0f} (RON 500,000)
        - At least 1 employee OR revenue under €12,500 (RON 60,000)
        - Certain business activities qualify (IT, consulting, etc.)

        Tax Calculation:
        - Microenterprise tax: 1% of gross revenue
        - Dividend distribution tax: 8% when profits are distributed to owner
        - Social security: Optional for owners (recommended: ~€300-500/month)
        - Health insurance: ~10% on minimum wage (~€60/month)

        This calculation shows ONLY the 1% revenue tax. Additional costs when extracting money:
        - 8% dividend tax applies when distributing profits
        - Owner can choose to pay social security (~€3,600-6,000/year)

        Note: This is the ideal regime for high-earning IT freelancers in Romania.
        Total effective rate including dividends and social: ~12-15% (still very competitive!)
        """,
    )

    config.tax_base_strategy = StandardTaxBase()

    config.deduction_strategies = [
        # Microenterprise revenue tax (1%)
        FlatRateDeduction(
            DeductionConfig(
                name="Microenterprise Tax",
                description="1% tax on gross revenue (microenterprise regime)",
                rate=Decimal("0.01"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Minimal social security (showing as optional/minimum)
        FlatRateDeduction(
            DeductionConfig(
                name="Minimum Health Insurance",
                description="Mandatory health insurance on minimum wage basis",
                rate=Decimal("0.006"),  # ~0.6% representing fixed €60/month on €100k
                applies_to=DeductionBase.GROSS,
            )
        ),
    ]

    return config


# Export configs
ROMANIA_FREELANCER_MICRO = create_romania_freelancer_micro_config()
