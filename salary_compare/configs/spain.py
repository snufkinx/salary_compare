"""Spain tax regime configurations."""

from decimal import Decimal

from ..models.config import DeductionConfig, TaxBracketConfig, TaxRegimeConfig
from ..models.enums import Country, Currency, DeductionBase, EmploymentType
from ..strategies import FlatRateDeduction, ProgressiveTaxDeduction, StandardTaxBase


def create_madrid_salaried_config() -> TaxRegimeConfig:
    """Create configuration for Madrid salaried employee."""

    # Spanish tax brackets (state + Madrid regional rates combined)
    # State brackets + Madrid applies lower regional rates
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), Decimal("12450"), Decimal("0.19")),  # 19%
        TaxBracketConfig(Decimal("12450"), Decimal("20200"), Decimal("0.24")),  # 24%
        TaxBracketConfig(Decimal("20200"), Decimal("35200"), Decimal("0.30")),  # 30%
        TaxBracketConfig(Decimal("35200"), Decimal("60000"), Decimal("0.37")),  # 37%
        TaxBracketConfig(Decimal("60000"), Decimal("300000"), Decimal("0.45")),  # 45%
        TaxBracketConfig(Decimal("300000"), Decimal("inf"), Decimal("0.47")),  # 47%
    ]

    config = TaxRegimeConfig(
        country=Country.SPAIN,
        employment_type=EmploymentType.SALARIED,
        local_currency=Currency.EUR,
        threshold_currency=Currency.EUR,
        region="Madrid",
        description="""
        Madrid Salaried Employee Tax Regime (Spain):

        This calculation applies to salaried employees working in the Community of Madrid.

        Key Features:
        - Progressive income tax (IRPF) combining state and regional rates
        - Madrid has some of the lowest regional tax rates in Spain
        - Social Security contributions capped at certain limits
        - Standard deductions and allowances apply

        Tax Brackets (2024, State + Madrid Regional):
        - 19% on income up to €12,450
        - 24% on income €12,450 - €20,200
        - 30% on income €20,200 - €35,200
        - 37% on income €35,200 - €60,000
        - 45% on income €60,000 - €300,000
        - 47% on income above €300,000

        Social Security Contributions (Employee, 2024):
        - General regime: ~6.35% of gross salary
        - Unemployment insurance: ~1.55%
        - Vocational training: ~0.10%
        - Total: ~6.35% (capped at contribution bases)

        Note: Madrid is known for competitive tax rates compared to other Spanish regions.
        """,
    )

    config.tax_base_strategy = StandardTaxBase()

    config.deduction_strategies = [
        # Social security (simplified as single deduction)
        FlatRateDeduction(
            DeductionConfig(
                name="Social Security",
                description="Social security contributions (employee portion)",
                rate=Decimal("0.0635"),
                ceiling=Decimal("53400"),  # Approximate ceiling
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Income tax
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Progressive income tax (IRPF)",
                rate=Decimal("0"),
                applies_to=DeductionBase.GROSS,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


def create_barcelona_salaried_config() -> TaxRegimeConfig:
    """Create configuration for Barcelona (Catalonia) salaried employee."""

    # Catalonia applies higher regional rates than Madrid
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), Decimal("12450"), Decimal("0.19")),
        TaxBracketConfig(Decimal("12450"), Decimal("20200"), Decimal("0.24")),
        TaxBracketConfig(Decimal("20200"), Decimal("35200"), Decimal("0.315")),  # 31.5% (higher)
        TaxBracketConfig(Decimal("35200"), Decimal("60000"), Decimal("0.385")),  # 38.5% (higher)
        TaxBracketConfig(Decimal("60000"), Decimal("300000"), Decimal("0.46")),  # 46% (higher)
        TaxBracketConfig(Decimal("300000"), Decimal("inf"), Decimal("0.48")),  # 48%
    ]

    config = TaxRegimeConfig(
        country=Country.SPAIN,
        employment_type=EmploymentType.SALARIED,
        local_currency=Currency.EUR,
        threshold_currency=Currency.EUR,
        region="Barcelona",
        description="""
        Barcelona Salaried Employee Tax Regime (Spain - Catalonia):

        This calculation applies to salaried employees working in Catalonia (Barcelona).

        Key Features:
        - Progressive income tax (IRPF) with Catalonia regional rates
        - Catalonia applies higher regional rates than Madrid
        - Social Security contributions same as other regions
        - Solidarity surcharge on high incomes

        Tax Brackets (2024, State + Catalonia Regional):
        - 19% on income up to €12,450
        - 24% on income €12,450 - €20,200
        - 31.5% on income €20,200 - €35,200
        - 38.5% on income €35,200 - €60,000
        - 46% on income €60,000 - €300,000
        - 48% on income above €300,000

        Social Security Contributions (Employee, 2024):
        - General regime: ~6.35% of gross salary (capped)

        Note: Catalonia has higher regional tax rates than Madrid, resulting in higher overall taxation.
        """,
    )

    config.tax_base_strategy = StandardTaxBase()

    config.deduction_strategies = [
        FlatRateDeduction(
            DeductionConfig(
                name="Social Security",
                description="Social security contributions (employee portion)",
                rate=Decimal("0.0635"),
                ceiling=Decimal("53400"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Progressive income tax (IRPF) with Catalonia rates",
                rate=Decimal("0"),
                applies_to=DeductionBase.GROSS,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


def create_valencia_salaried_config() -> TaxRegimeConfig:
    """Create configuration for Valencia salaried employee."""

    # Valencia (Valencian Community) has moderate regional rates
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), Decimal("12450"), Decimal("0.19")),
        TaxBracketConfig(Decimal("12450"), Decimal("20200"), Decimal("0.24")),
        TaxBracketConfig(Decimal("20200"), Decimal("35200"), Decimal("0.305")),  # 30.5%
        TaxBracketConfig(Decimal("35200"), Decimal("60000"), Decimal("0.375")),  # 37.5%
        TaxBracketConfig(Decimal("60000"), Decimal("300000"), Decimal("0.455")),  # 45.5%
        TaxBracketConfig(Decimal("300000"), Decimal("inf"), Decimal("0.475")),  # 47.5%
    ]

    config = TaxRegimeConfig(
        country=Country.SPAIN,
        employment_type=EmploymentType.SALARIED,
        local_currency=Currency.EUR,
        threshold_currency=Currency.EUR,
        region="Valencia",
        description="""
        Valencia Salaried Employee Tax Regime (Spain - Valencian Community):

        This calculation applies to salaried employees working in the Valencian Community (Valencia).

        Key Features:
        - Progressive income tax (IRPF) with Valencia regional rates
        - Valencia has moderate regional rates (between Madrid and Catalonia)
        - Social Security contributions same as other regions

        Tax Brackets (2024, State + Valencia Regional):
        - 19% on income up to €12,450
        - 24% on income €12,450 - €20,200
        - 30.5% on income €20,200 - €35,200
        - 37.5% on income €35,200 - €60,000
        - 45.5% on income €60,000 - €300,000
        - 47.5% on income above €300,000

        Social Security Contributions (Employee, 2024):
        - General regime: ~6.35% of gross salary (capped)

        Note: Valencia offers moderate taxation, positioned between Madrid (lowest) and Catalonia (highest).
        """,
    )

    config.tax_base_strategy = StandardTaxBase()

    config.deduction_strategies = [
        FlatRateDeduction(
            DeductionConfig(
                name="Social Security",
                description="Social security contributions (employee portion)",
                rate=Decimal("0.0635"),
                ceiling=Decimal("53400"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Progressive income tax (IRPF) with Valencia rates",
                rate=Decimal("0"),
                applies_to=DeductionBase.GROSS,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


# Export configs
MADRID_SALARIED = create_madrid_salaried_config()
BARCELONA_SALARIED = create_barcelona_salaried_config()
VALENCIA_SALARIED = create_valencia_salaried_config()
