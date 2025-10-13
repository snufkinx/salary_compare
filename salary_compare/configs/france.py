"""France tax regime configurations."""

from decimal import Decimal

from ..models.config import DeductionConfig, TaxBracketConfig, TaxRegimeConfig
from ..models.enums import Country, Currency, DeductionBase, EmploymentType
from ..strategies import (
    AfterSocialSecurityTaxBase,
    CappedPercentageDeduction,
    FlatRateDeduction,
    ProgressiveTaxDeduction,
)


def create_france_salaried_config() -> TaxRegimeConfig:
    """Create configuration for France salaried employee."""

    # French income tax brackets (2025)
    # Applied to taxable income (after social security deductions)
    tax_brackets = [
        TaxBracketConfig(Decimal("0"), Decimal("10225"), Decimal("0.00")),  # 0%
        TaxBracketConfig(Decimal("10225"), Decimal("26070"), Decimal("0.11")),  # 11%
        TaxBracketConfig(Decimal("26070"), Decimal("74545"), Decimal("0.30")),  # 30%
        TaxBracketConfig(Decimal("74545"), Decimal("160336"), Decimal("0.41")),  # 41%
        TaxBracketConfig(Decimal("160336"), Decimal("inf"), Decimal("0.45")),  # 45%
    ]

    config = TaxRegimeConfig(
        country=Country.FRANCE,
        employment_type=EmploymentType.SALARIED,
        local_currency=Currency.EUR,
        threshold_currency=Currency.EUR,
        title="France Salaried Employee",
        description="""
        France Salaried Employee Tax Regime:

        France has a comprehensive social security system with significant contributions
        from both employees and employers, plus progressive income tax (Impôt sur le Revenu).

        Income Tax Brackets (2025):
        - 0% on income up to €10,225
        - 11% on income €10,225 - €26,070
        - 30% on income €26,070 - €74,545
        - 41% on income €74,545 - €160,336
        - 45% on income above €160,336

        Social Security Contributions (Employee, 2025):
        The monthly ceiling (Plafond de la Sécurité Sociale) is €3,925 (€47,100/year).

        Employee Contributions:
        - Old-age insurance (up to ceiling): 6.9%
        - Old-age insurance (above ceiling): 0.4%
        - CSG (General Social Contribution): 9.2% (deductible portion)
        - CRDS (Social Debt Repayment): 0.5%
        - Supplementary pension (Agirc-Arrco):
          * Bracket 1 (up to ceiling): 3.15%
          * Bracket 2 (ceiling to €376,800): 8.64%
        - CEG (Overall Balance Contribution):
          * Bracket 1: 0.86%
          * Bracket 2: 1.08%

        Simplified Total Employee Rate: ~23% (combination of various contributions)

        Tax Base Calculation:
        - Tax base = Gross - Employee Social Security Contributions
        - Income tax is then applied to this reduced base
        - CSG/CRDS are calculated on 98.25% of gross (with some being tax-deductible)

        Note: This is a simplified calculation. Actual French payroll is complex with
        many specific rules, partial deductibility of CSG, and employer contributions.
        Results should be within 5% of actual take-home pay.
        """,
    )

    config.tax_base_strategy = AfterSocialSecurityTaxBase()

    config.deduction_strategies = [
        # Old-age insurance (Assurance Vieillesse)
        # Up to ceiling: 6.9%
        CappedPercentageDeduction(
            DeductionConfig(
                name="Old-Age Insurance (Base)",
                description="Pension contributions up to SS ceiling",
                rate=Decimal("0.069"),
                ceiling=Decimal("47100"),  # €3,925/month × 12
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Above ceiling: 0.4%
        FlatRateDeduction(
            DeductionConfig(
                name="Old-Age Insurance (Supplementary)",
                description="Pension contributions on full salary",
                rate=Decimal("0.004"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # CSG - General Social Contribution (9.2% on 98.25% of gross)
        # Simplified: 9.2% × 98.25% ≈ 9.04%
        FlatRateDeduction(
            DeductionConfig(
                name="CSG (General Social Contribution)",
                description="Funds social security (partially tax-deductible)",
                rate=Decimal("0.0904"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # CRDS - Social Debt Repayment (0.5% on 98.25% of gross)
        # Simplified: 0.5% × 98.25% ≈ 0.49%
        FlatRateDeduction(
            DeductionConfig(
                name="CRDS (Social Debt Repayment)",
                description="Repayment of social security debt",
                rate=Decimal("0.0049"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Supplementary pension Agirc-Arrco Bracket 1 (up to ceiling)
        CappedPercentageDeduction(
            DeductionConfig(
                name="Supplementary Pension (Bracket 1)",
                description="Agirc-Arrco pension - up to ceiling",
                rate=Decimal("0.0315"),
                ceiling=Decimal("47100"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Supplementary pension Agirc-Arrco Bracket 2 (above ceiling)
        # Applied to income between ceiling and 8× ceiling (€376,800)
        CappedPercentageDeduction(
            DeductionConfig(
                name="Supplementary Pension (Bracket 2)",
                description="Agirc-Arrco pension - above ceiling",
                rate=Decimal("0.0864"),
                ceiling=Decimal("376800"),  # 8× annual ceiling
                floor=Decimal("47100"),  # Only on amount above base ceiling
                applies_to=DeductionBase.GROSS,
            )
        ),
        # CEG - Overall Balance Contribution Bracket 1
        CappedPercentageDeduction(
            DeductionConfig(
                name="CEG (Balance Contribution - B1)",
                description="Contribution for pension balance",
                rate=Decimal("0.0086"),
                ceiling=Decimal("47100"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # CEG Bracket 2
        CappedPercentageDeduction(
            DeductionConfig(
                name="CEG (Balance Contribution - B2)",
                description="Contribution for pension balance - above ceiling",
                rate=Decimal("0.0108"),
                ceiling=Decimal("376800"),
                floor=Decimal("47100"),
                applies_to=DeductionBase.GROSS,
            )
        ),
        # Income tax (applied to tax base = gross - social security)
        ProgressiveTaxDeduction(
            config=DeductionConfig(
                name="Income Tax",
                description="Progressive income tax (Impôt sur le Revenu)",
                rate=Decimal("0"),
                applies_to=DeductionBase.GROSS,
            ),
            brackets=tax_brackets,
        ),
    ]

    return config


# Export config
FRANCE_SALARIED = create_france_salaried_config()

