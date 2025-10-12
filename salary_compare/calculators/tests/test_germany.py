"""Unit tests for Germany salary calculator."""

from decimal import Decimal

from ..germany import SalariedEmployeeGermany


class TestSalariedEmployeeGermany:
    """Test cases for German salaried employee tax calculations."""

    def test_50000_euro_salary(self):
        """Test calculation for €50,000 gross salary."""
        calculator = SalariedEmployeeGermany(Decimal("50000"))
        result = calculator.calculate_net_salary()

        # With discrete brackets: €50,000 gross → ~€30,000 net
        # Allow tolerance due to calculation differences
        expected_net_min = Decimal("29000")
        expected_net_max = Decimal("31000")

        assert (
            expected_net_min <= result.net_salary <= expected_net_max
        ), f"Net salary {result.net_salary} not within expected range {expected_net_min}-{expected_net_max}"

        # Verify tax base calculation (gross - social security)
        assert result.tax_base < result.gross_salary, "Tax base should be less than gross salary"
        assert result.tax_base > Decimal(
            "35000"
        ), "Tax base should be reasonable after social security deductions"

        # Verify total deductions
        total_deductions = result.gross_salary - result.net_salary
        assert total_deductions > Decimal("19000"), "Total deductions should be substantial"
        assert total_deductions < Decimal("22000"), "Total deductions should not be excessive"

    def test_100000_euro_salary(self):
        """Test calculation for €100,000 gross salary."""
        calculator = SalariedEmployeeGermany(Decimal("100000"))
        result = calculator.calculate_net_salary()

        # With discrete brackets: €100,000 gross → ~€55,000 net
        # Approximate calculation using marginal rate brackets
        expected_net_min = Decimal("54000")
        expected_net_max = Decimal("57000")

        assert (
            expected_net_min <= result.net_salary <= expected_net_max
        ), f"Net salary {result.net_salary} not within expected range {expected_net_min}-{expected_net_max}"

        # Verify progressive tax calculation (only one bracket shown due to formula)
        assert len(result.income_tax_brackets) >= 1, "Should have at least one tax bracket"

        # Verify social security contributions (with ceilings applied)
        social_security_total = sum(
            deduction.amount for deduction in result.deductions if "Insurance" in deduction.name
        )
        assert social_security_total > Decimal("16000"), "Social security should be substantial"
        assert social_security_total < Decimal("18000"), "Social security should be capped"

    def test_tax_free_allowance(self):
        """Test that tax-free allowance is properly applied."""
        calculator = SalariedEmployeeGermany(Decimal("12096"))  # Exactly tax-free allowance
        result = calculator.calculate_net_salary()

        # Should have no income tax but still have social security
        income_tax = next(
            (d.amount for d in result.deductions if d.name == "Income Tax"), Decimal("0")
        )
        assert income_tax == Decimal("0"), "No income tax should be due at tax-free allowance level"

        # Should still have social security contributions
        social_security_total = sum(
            deduction.amount for deduction in result.deductions if "Insurance" in deduction.name
        )
        assert social_security_total > Decimal(
            "0"
        ), "Should still have social security contributions"

    def test_progressive_tax_brackets(self):
        """Test that progressive tax brackets are correctly applied."""
        calculator = SalariedEmployeeGermany(Decimal("150000"))
        result = calculator.calculate_net_salary()

        # With German formula, only one bracket is shown (the applicable zone)
        assert len(result.income_tax_brackets) >= 1, "Should have at least one tax bracket"

        # Verify bracket calculations
        total_bracket_tax = sum(bracket.tax_amount for bracket in result.income_tax_brackets)
        income_tax = next(
            (d.amount for d in result.deductions if d.name == "Income Tax"), Decimal("0")
        )

        assert abs(total_bracket_tax - income_tax) < Decimal(
            "1"
        ), "Sum of bracket taxes should equal total income tax"

    def test_solidarity_surcharge(self):
        """Test solidarity surcharge calculation."""
        calculator = SalariedEmployeeGermany(
            Decimal("80000")
        )  # High enough to trigger solidarity surcharge
        result = calculator.calculate_net_salary()

        solidarity_surcharge = next(
            (d.amount for d in result.deductions if d.name == "Solidarity Surcharge"), Decimal("0")
        )

        # Should have solidarity surcharge for high income
        assert solidarity_surcharge > Decimal(
            "0"
        ), "Should have solidarity surcharge for high income"

        # Verify rate (5.5% of income tax)
        income_tax = next(
            (d.amount for d in result.deductions if d.name == "Income Tax"), Decimal("0")
        )
        expected_solidarity = income_tax * Decimal("0.055")
        assert abs(solidarity_surcharge - expected_solidarity) < Decimal(
            "1"
        ), "Solidarity surcharge should be 5.5% of income tax"

    def test_social_security_rates(self):
        """Test that social security rates are correctly applied with ceilings."""
        calculator = SalariedEmployeeGermany(Decimal("100000"))
        result = calculator.calculate_net_salary()

        # Check individual social security contributions
        pension_insurance = next(
            (d.amount for d in result.deductions if d.name == "Pension Insurance"), Decimal("0")
        )
        health_insurance = next(
            (d.amount for d in result.deductions if d.name == "Health Insurance"), Decimal("0")
        )
        unemployment_insurance = next(
            (d.amount for d in result.deductions if d.name == "Unemployment Insurance"),
            Decimal("0"),
        )
        long_term_care_insurance = next(
            (d.amount for d in result.deductions if d.name == "Long_Term_Care Insurance"),
            Decimal("0"),
        )

        # Verify rates with ceilings applied
        # Pension: 9.3% of €96,000 (ceiling) = €8,928
        assert abs(pension_insurance - Decimal("8928")) < Decimal(
            "1"
        ), f"Pension insurance should be €8,928 (capped), got {pension_insurance}"
        # Health: 9.1% of €62,100 (ceiling) = €5,651.10
        assert abs(health_insurance - Decimal("5651.10")) < Decimal(
            "1"
        ), f"Health insurance should be €5,651.10 (capped), got {health_insurance}"
        # Unemployment: 1.3% of €96,000 (ceiling) = €1,248
        assert abs(unemployment_insurance - Decimal("1248")) < Decimal(
            "1"
        ), f"Unemployment insurance should be €1,248 (capped), got {unemployment_insurance}"
        # Long-term care: 2.0% of €62,100 (ceiling) = €1,242
        assert abs(long_term_care_insurance - Decimal("1242")) < Decimal(
            "1"
        ), f"Long-term care insurance should be €1,242 (capped), got {long_term_care_insurance}"

    def test_calculation_consistency(self):
        """Test that calculations are consistent and reproducible."""
        calculator = SalariedEmployeeGermany(Decimal("75000"))

        # Run calculation multiple times
        results = [calculator.calculate_net_salary() for _ in range(3)]

        # All results should be identical
        for i in range(1, len(results)):
            assert (
                results[0].net_salary == results[i].net_salary
            ), "Calculations should be consistent and reproducible"
            assert (
                results[0].total_deductions == results[i].total_deductions
            ), "Total deductions should be consistent"

    def test_edge_case_low_salary(self):
        """Test edge case with very low salary."""
        calculator = SalariedEmployeeGermany(Decimal("10000"))
        result = calculator.calculate_net_salary()

        # Should still have social security contributions
        social_security_total = sum(
            deduction.amount for deduction in result.deductions if "Insurance" in deduction.name
        )
        assert social_security_total > Decimal(
            "0"
        ), "Should have social security even for low salary"

        # Net salary should be positive but much less than gross
        assert result.net_salary > Decimal("0"), "Net salary should be positive"
        assert result.net_salary < result.gross_salary, "Net salary should be less than gross"

    def test_edge_case_very_high_salary(self):
        """Test edge case with very high salary."""
        calculator = SalariedEmployeeGermany(Decimal("400000"))
        result = calculator.calculate_net_salary()

        # Should have income in zone 4 (45% marginal rate)
        # Effective rate will be lower than marginal rate
        assert len(result.income_tax_brackets) > 0, "Should have tax brackets"
        assert result.tax_base > Decimal("277825"), "Should exceed zone 4 threshold"

        # Should have solidarity surcharge
        solidarity_surcharge = next(
            (d.amount for d in result.deductions if d.name == "Solidarity Surcharge"), Decimal("0")
        )
        assert solidarity_surcharge > Decimal(
            "0"
        ), "Should have solidarity surcharge for very high income"
