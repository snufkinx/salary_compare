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
        title="Romania Freelancer",
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

        Tax Calculation (Full Picture):
        - Microenterprise tax: 1% of gross revenue
        - Dividend distribution tax: 8% when extracting profits to owner
        - Health insurance: ~€700/year (mandatory minimum)
        - Social security: ~€4,000/year (optional but recommended for pension)

        Total Effective Tax Rate:
        - Microenterprise: 1%
        - Dividend tax: 8%
        - Health insurance: ~0.7%
        - Social security: ~4%
        - **Total: ~13.7% all-in** (on €100k)

        This calculation includes:
        ✓ 1% microenterprise tax
        ✓ 8% dividend tax (when extracting money)
        ✓ Mandatory health insurance
        ✓ Recommended social security contributions

        Note: Even with all costs included, this remains one of Europe's most
        competitive tax regimes for IT professionals and consultants.
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
        # Dividend distribution tax (8% when extracting profits)
        # Applied to profit after micro tax
        FlatRateDeduction(
            DeductionConfig(
                name="Dividend Tax (8%)",
                description="8% tax on dividend distribution (when extracting profits)",
                rate=Decimal("0.08"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Minimal health insurance (mandatory fixed amount)
        FlatRateDeduction(
            DeductionConfig(
                name="Health Insurance",
                description="Mandatory health insurance (minimum basis ~€720/year)",
                rate=Decimal("0.007"),  # ~€700/year fixed cost represented as percentage
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Optional but recommended social security
        FlatRateDeduction(
            DeductionConfig(
                name="Social Security (Optional)",
                description="Optional social security for pension rights (~€4,000/year recommended)",
                rate=Decimal("0.04"),  # ~4% representing €4,000/year
                applies_to=DeductionBase.GROSS,
            )
        ),
    ]

    return config


# Export configs
ROMANIA_FREELANCER_MICRO = create_romania_freelancer_micro_config()
