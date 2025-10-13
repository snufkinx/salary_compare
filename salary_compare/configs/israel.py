"""Israel tax regime configurations."""

from decimal import Decimal

from ..models.config import DeductionConfig, TaxBracketConfig, TaxRegimeConfig
from ..models.enums import Country, Currency, DeductionBase, EmploymentType
from ..services.currency import get_currency_converter
from ..strategies import (
    CappedPercentageDeduction,
    FlatRateDeduction,
    ProgressiveTaxDeduction,
    StandardTaxBase,
)


def create_israel_salaried_config() -> TaxRegimeConfig:
    """Create configuration for Israeli salaried employee."""

    # Get currency converter
    converter = get_currency_converter(from_currency="ILS", to_currency="EUR")

    # Tax brackets (converted from ILS to EUR)
    tax_brackets_ils = [
        (0, 83040, 0.10),
        (83040, 119040, 0.14),
        (119040, 185040, 0.20),
        (185040, 260040, 0.31),
        (260040, 560280, 0.35),
        (560280, 721560, 0.47),
        (721560, float("inf"), 0.50),
    ]

    tax_brackets = []
    for lower, upper, rate in tax_brackets_ils:
        lower_eur = converter.convert(Decimal(str(lower)))
        upper_eur = (
            converter.convert(Decimal(str(upper))) if upper != float("inf") else Decimal("inf")
        )
        tax_brackets.append(TaxBracketConfig(lower_eur, upper_eur, Decimal(str(rate))))

    # Keren Hishtalmut cap
    keren_cap = converter.convert(Decimal("188544"))

    config = TaxRegimeConfig(
        country=Country.ISRAEL,
        employment_type=EmploymentType.SALARIED,
        local_currency=Currency.ILS,
        threshold_currency=Currency.ILS,
        title="Israel Salaried Employee",
        description=f"""
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
        - Keren Hishtalmut: 2.5% of gross salary (capped at €{keren_cap:,.0f} / ₪188,544 annually)

        Note:
        - Employers also contribute to pension (6.5%) and Keren Hishtalmut (7.5%)
        - Keren Hishtalmut contributions above the cap are subject to income tax
        - These calculations use approximate EUR/ILS conversion (1 EUR = 4 ILS)
        """,
    )

    # Tax base = Gross salary
    config.tax_base_strategy = StandardTaxBase()

    # Deduction strategies
    config.deduction_strategies = [
        # Mandatory contributions (on gross)
        FlatRateDeduction(
            DeductionConfig(
                name="National Insurance",
                description="Mandatory national insurance contribution (Bituach Leumi)",
                rate=Decimal("0.04"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        FlatRateDeduction(
            DeductionConfig(
                name="Health Tax",
                description="Mandatory health tax contribution (Mas Briut)",
                rate=Decimal("0.05"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        FlatRateDeduction(
            DeductionConfig(
                name="Pension",
                description="Pension fund contribution (Gemel Pensia)",
                rate=Decimal("0.06"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Keren Hishtalmut with cap
        CappedPercentageDeduction(
            DeductionConfig(
                name="Keren Hishtalmut",
                description="Advanced training fund contribution (Keren Hishtalmut)",
                rate=Decimal("0.025"),
                ceiling=keren_cap,
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Income tax (on gross salary)
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Progressive income tax",
                rate=Decimal("0"),
                applies_to=DeductionBase.GROSS,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


# Export configs
ISRAEL_SALARIED = create_israel_salaried_config()
