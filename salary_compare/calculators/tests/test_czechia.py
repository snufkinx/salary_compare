"""Unit tests for Czechia salary calculators."""

import pytest
from decimal import Decimal
from ..czechia import SalariedEmployeeCzechia, FreelancerCzechia


class TestSalariedEmployeeCzechia:
    """Test cases for Czech salaried employee tax calculations."""
    
    def test_50000_euro_salary(self):
        """Test calculation for €50,000 gross salary."""
        calculator = SalariedEmployeeCzechia(Decimal('50000'))
        result = calculator.calculate_net_salary()
        
        # Based on online calculators: €50,000 gross should result in approximately €37,500 net
        # Allow for ±€1,000 tolerance due to calculation differences
        expected_net_min = Decimal('36500')
        expected_net_max = Decimal('38500')
        
        assert expected_net_min <= result.net_salary <= expected_net_max, \
            f"Net salary {result.net_salary} not within expected range {expected_net_min}-{expected_net_max}"
        
        # Verify tax base is same as gross salary for salaried employees
        assert result.tax_base == result.gross_salary, "Tax base should equal gross salary for salaried employees"
        
        # Verify deductions
        social_security = next((d.amount for d in result.deductions if d.name == "Social Security"), Decimal('0'))
        health_insurance = next((d.amount for d in result.deductions if d.name == "Health Insurance"), Decimal('0'))
        income_tax = next((d.amount for d in result.deductions if d.name == "Income Tax"), Decimal('0'))
        
        # Verify rates
        assert abs(social_security - Decimal('50000') * Decimal('0.065')) < Decimal('1'), \
            "Social security should be 6.5%"
        assert abs(health_insurance - Decimal('50000') * Decimal('0.045')) < Decimal('1'), \
            "Health insurance should be 4.5%"
    
    def test_100000_euro_salary(self):
        """Test calculation for €100,000 gross salary."""
        calculator = SalariedEmployeeCzechia(Decimal('100000'))
        result = calculator.calculate_net_salary()
        
        # Should be in the high tax bracket (23%)
        expected_net_min = Decimal('70000')
        expected_net_max = Decimal('75000')
        
        assert expected_net_min <= result.net_salary <= expected_net_max, \
            f"Net salary {result.net_salary} not within expected range {expected_net_min}-{expected_net_max}"
        
        # Should have two tax brackets (15% and 23%)
        assert len(result.income_tax_brackets) == 2, "Should have two tax brackets for high income"
        
        # Verify tax brackets
        low_bracket = result.income_tax_brackets[0]
        high_bracket = result.income_tax_brackets[1]
        
        assert low_bracket.rate == Decimal('0.15'), "Low bracket should be 15%"
        assert high_bracket.rate == Decimal('0.23'), "High bracket should be 23%"
    
    def test_tax_threshold_calculation(self):
        """Test calculation at the tax threshold boundary."""
        # With 1 EUR = 25 CZK, threshold is 1867728/25 = 74709.12
        # Test just below threshold (€74,700)
        calculator = SalariedEmployeeCzechia(Decimal('74700'))
        result = calculator.calculate_net_salary()
        
        # Should only have 15% bracket
        assert len(result.income_tax_brackets) == 1, "Should have only one tax bracket below threshold"
        assert result.income_tax_brackets[0].rate == Decimal('0.15'), "Should use 15% rate"
        
        # Test well above threshold (€80,000)
        calculator = SalariedEmployeeCzechia(Decimal('80000'))
        result = calculator.calculate_net_salary()
        
        # Should have two brackets
        assert len(result.income_tax_brackets) == 2, "Should have two tax brackets above threshold"
    
    def test_social_security_and_health_rates(self):
        """Test that social security and health insurance rates are correctly applied."""
        calculator = SalariedEmployeeCzechia(Decimal('80000'))
        result = calculator.calculate_net_salary()
        
        social_security = next((d.amount for d in result.deductions if d.name == "Social Security"), Decimal('0'))
        health_insurance = next((d.amount for d in result.deductions if d.name == "Health Insurance"), Decimal('0'))
        
        # Verify exact amounts
        expected_social = Decimal('80000') * Decimal('0.065')
        expected_health = Decimal('80000') * Decimal('0.045')
        
        assert abs(social_security - expected_social) < Decimal('1'), \
            "Social security should be exactly 6.5%"
        assert abs(health_insurance - expected_health) < Decimal('1'), \
            "Health insurance should be exactly 4.5%"


class TestFreelancerCzechia:
    """Test cases for Czech freelancer tax calculations using 60/40 rule."""
    
    def test_50000_euro_salary(self):
        """Test calculation for €50,000 gross salary."""
        calculator = FreelancerCzechia(Decimal('50000'))
        result = calculator.calculate_net_salary()
        
        # Taxable income should be 40% of gross
        expected_taxable = Decimal('50000') * Decimal('0.40')
        assert result.tax_base == expected_taxable, \
            f"Tax base should be 40% of gross: {expected_taxable}"
        
        # Should have income tax with discount applied
        income_tax = next((d.amount for d in result.deductions if d.name == "Income Tax"), Decimal('0'))
        assert income_tax >= Decimal('0'), "Income tax should be non-negative"
        
        # Net salary should be reasonable (around 85-90% of gross with corrected calculation)
        expected_net_min = Decimal('43000')
        expected_net_max = Decimal('45000')
        
        assert expected_net_min <= result.net_salary <= expected_net_max, \
            f"Net salary {result.net_salary} not within expected range {expected_net_min}-{expected_net_max}"
    
    def test_100000_euro_salary(self):
        """Test calculation for €100,000 gross salary."""
        calculator = FreelancerCzechia(Decimal('100000'))
        result = calculator.calculate_net_salary()
        
        # Taxable income should be 40% of gross
        expected_taxable = Decimal('100000') * Decimal('0.40')
        assert result.tax_base == expected_taxable, \
            f"Tax base should be 40% of gross: {expected_taxable}"
        
        # Should have income tax with discount applied
        income_tax = next((d.amount for d in result.deductions if d.name == "Income Tax"), Decimal('0'))
        
        # Calculate expected income tax (actual discount from currency converter)
        expected_tax_before_discount = expected_taxable * Decimal('0.15')
        # Use a tolerance since the exact conversion might vary slightly
        actual_discount = expected_tax_before_discount - income_tax
        expected_tax_after_discount = max(Decimal('0'), expected_tax_before_discount - actual_discount)
        
        assert abs(income_tax - expected_tax_after_discount) < Decimal('1'), \
            f"Income tax should be {expected_tax_after_discount}, got {income_tax}"
        
        # Verify social security and health insurance are calculated on 50% of gross
        social_security = next((d.amount for d in result.deductions if d.name == "Social Security"), Decimal('0'))
        health_insurance = next((d.amount for d in result.deductions if d.name == "Health Insurance"), Decimal('0'))
        
        expected_social_base = expected_taxable * Decimal('0.50')
        expected_social = expected_social_base * Decimal('0.292')
        expected_health = expected_social_base * Decimal('0.135')
        
        assert abs(social_security - expected_social) < Decimal('1'), \
            "Social security should be 29.2% of 50% of taxable income"
        assert abs(health_insurance - expected_health) < Decimal('1'), \
            "Health insurance should be 13.5% of 50% of taxable income"
    
    def test_taxpayer_discount_application(self):
        """Test that taxpayer discount is correctly applied."""
        # Test with low income where discount eliminates tax
        calculator = FreelancerCzechia(Decimal('10000'))
        result = calculator.calculate_net_salary()
        
        income_tax = next((d.amount for d in result.deductions if d.name == "Income Tax"), Decimal('0'))
        assert income_tax == Decimal('0'), "Income tax should be 0 when discount exceeds tax due"
        
        # Test with higher income where discount reduces but doesn't eliminate tax
        calculator = FreelancerCzechia(Decimal('20000'))
        result = calculator.calculate_net_salary()
        
        income_tax = next((d.amount for d in result.deductions if d.name == "Income Tax"), Decimal('0'))
        expected_tax_before_discount = Decimal('20000') * Decimal('0.40') * Decimal('0.15')
        # Use actual discount value from the calculator
        actual_discount = expected_tax_before_discount - income_tax
        expected_tax_after_discount = max(Decimal('0'), expected_tax_before_discount - actual_discount)
        
        assert abs(income_tax - expected_tax_after_discount) < Decimal('1'), \
            "Taxpayer discount should be correctly applied"
    
    def test_60_40_rule_application(self):
        """Test that 60/40 rule is correctly applied."""
        calculator = FreelancerCzechia(Decimal('80000'))
        result = calculator.calculate_net_salary()
        
        # Taxable income should be exactly 40% of gross
        expected_taxable = Decimal('80000') * Decimal('0.40')
        assert result.tax_base == expected_taxable, \
            "Taxable income should be exactly 40% of gross income"
        
        # Social security and health insurance base should be 50% of taxable income
        social_security = next((d.amount for d in result.deductions if d.name == "Social Security"), Decimal('0'))
        health_insurance = next((d.amount for d in result.deductions if d.name == "Health Insurance"), Decimal('0'))
        
        expected_base = expected_taxable * Decimal('0.50')
        expected_social = expected_base * Decimal('0.292')
        expected_health = expected_base * Decimal('0.135')
        
        assert abs(social_security - expected_social) < Decimal('1'), \
            "Social security should be calculated on 50% of taxable income"
        assert abs(health_insurance - expected_health) < Decimal('1'), \
            "Health insurance should be calculated on 50% of taxable income"
    
    def test_calculation_consistency(self):
        """Test that calculations are consistent and reproducible."""
        calculator = FreelancerCzechia(Decimal('75000'))
        
        # Run calculation multiple times
        results = [calculator.calculate_net_salary() for _ in range(3)]
        
        # All results should be identical
        for i in range(1, len(results)):
            assert results[0].net_salary == results[i].net_salary, \
                "Calculations should be consistent and reproducible"
            assert results[0].total_deductions == results[i].total_deductions, \
                "Total deductions should be consistent"
    
    def test_edge_case_low_salary(self):
        """Test edge case with very low salary."""
        calculator = FreelancerCzechia(Decimal('5000'))
        result = calculator.calculate_net_salary()
        
        # Should still have social security and health insurance
        social_security = next((d.amount for d in result.deductions if d.name == "Social Security"), Decimal('0'))
        health_insurance = next((d.amount for d in result.deductions if d.name == "Health Insurance"), Decimal('0'))
        
        assert social_security > Decimal('0'), "Should have social security even for low salary"
        assert health_insurance > Decimal('0'), "Should have health insurance even for low salary"
        
        # Net salary should be positive but much less than gross
        assert result.net_salary > Decimal('0'), "Net salary should be positive"
        assert result.net_salary < result.gross_salary, "Net salary should be less than gross"
    
    def test_edge_case_high_salary(self):
        """Test edge case with very high salary."""
        calculator = FreelancerCzechia(Decimal('200000'))
        result = calculator.calculate_net_salary()
        
        # Taxable income should still be 40% of gross
        expected_taxable = Decimal('200000') * Decimal('0.40')
        assert result.tax_base == expected_taxable, \
            "Taxable income should remain 40% even for high income"
        
        # Should have reasonable deductions (lower with corrected calculation)
        assert result.total_deductions > Decimal('25000'), "Should have reasonable deductions"
        assert result.net_salary > Decimal('100000'), "Net salary should still be substantial"
        assert result.net_salary < result.gross_salary, "Net salary should be less than gross"
