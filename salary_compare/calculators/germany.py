"""Germany tax calculator for salaried employees."""

from decimal import Decimal
from typing import List
from ..models.employee import SalariedEmployee
from ..models.tax_result import TaxResult, Deduction, TaxBracket


class SalariedEmployeeGermany(SalariedEmployee):
    """Germany salaried employee tax calculator (Tax Class 1)."""
    
    def __init__(self, gross_salary: Decimal, tax_class: int = 1):
        super().__init__(gross_salary, "Germany")
        self.tax_class = tax_class
        
        # 2024/2025 Germany tax rates and thresholds
        self.tax_free_allowance = Decimal('12096')  # Grundfreibetrag
        self.solidarity_surcharge_threshold = Decimal('1000')  # Solidaritätszuschlag threshold (on income tax)
        
        # Progressive tax brackets (2024/2025)
        self.tax_brackets = [
            (Decimal('0'), Decimal('12096'), Decimal('0.00')),      # Tax-free allowance
            (Decimal('12097'), Decimal('68480'), Decimal('0.14')),  # 14% bracket
            (Decimal('68481'), Decimal('277825'), Decimal('0.42')), # 42% bracket
            (Decimal('277826'), Decimal('999999999'), Decimal('0.45')) # 45% bracket
        ]
        
        # Social security rates (employee portion) and ceilings for 2024
        self.social_security_rates = {
            'pension': {
                'rate': Decimal('0.093'),           # 9.3% pension insurance
                'ceiling': Decimal('96000')         # Annual ceiling (West Germany 2024)
            },
            'health': {
                'rate': Decimal('0.091'),           # 7.3% base + 1.6% average additional = 8.9% (using 9.1% for accuracy)
                'ceiling': Decimal('62100')         # Annual ceiling (2024)
            },
            'unemployment': {
                'rate': Decimal('0.013'),           # 1.3% unemployment insurance (2024)
                'ceiling': Decimal('96000')         # Annual ceiling (West Germany 2024)
            },
            'long_term_care': {
                'rate': Decimal('0.02'),            # 2.0% long-term care insurance (1.7% base + 0.3% for childless over 23)
                'ceiling': Decimal('62100')         # Annual ceiling (2024)
            }
        }
        
        # Solidarity surcharge rate
        self.solidarity_rate = Decimal('0.055')  # 5.5%
    
    def calculate_net_salary(self) -> TaxResult:
        """Calculate net salary for German salaried employee."""
        result = self._create_base_result()
        
        # Calculate social security contributions (with ceilings)
        total_social_security = Decimal('0')
        for name, config in self.social_security_rates.items():
            rate = config['rate']
            ceiling = config['ceiling']
            # Apply ceiling
            contribution_base = min(self.gross_salary, ceiling)
            amount = contribution_base * rate
            
            result.add_deduction(Deduction(
                name=f"{name.title()} Insurance",
                amount=amount,
                rate=rate,
                description=f"Mandatory {name} insurance contribution",
                calculation_details=f"{contribution_base:,.0f} × {rate:.1%} = {amount:,.0f}" + 
                                  (f" (capped at €{ceiling:,.0f})" if self.gross_salary > ceiling else "")
            ))
            total_social_security += amount
        
        # Calculate taxable income (gross - social security)
        taxable_income = self.gross_salary - total_social_security
        result.tax_base = taxable_income
        
        # Calculate income tax using progressive brackets
        income_tax = self._calculate_progressive_tax(taxable_income, result)
        
        # Calculate solidarity surcharge
        solidarity_surcharge = Decimal('0')
        if income_tax > self.solidarity_surcharge_threshold:
            solidarity_surcharge = income_tax * self.solidarity_rate
            result.add_deduction(Deduction(
                name="Solidarity Surcharge",
                amount=solidarity_surcharge,
                rate=self.solidarity_rate,
                description="Solidarity surcharge on income tax",
                calculation_details=f"{income_tax:,.0f} × {self.solidarity_rate:.1%} = {solidarity_surcharge:,.0f}"
            ))
        
        # Calculate final net salary
        result.net_salary = self.gross_salary - result.total_deductions
        
        # Add calculation explanations
        result.calculation_explanations = {
            "tax_base": f"Taxable income = Gross salary - Social security contributions = {self.gross_salary:,.0f} - {total_social_security:,.0f} = {taxable_income:,.0f}",
            "income_tax": f"Progressive income tax calculated on taxable income using German tax brackets",
            "social_security": f"Social security contributions calculated on gross salary at statutory rates",
            "solidarity_surcharge": f"5.5% surcharge on income tax above {self.solidarity_surcharge_threshold:,.0f}"
        }
        
        return result
    
    def _calculate_progressive_tax(self, taxable_income: Decimal, result: TaxResult) -> Decimal:
        """Calculate progressive income tax using German tax formula (2024/2025)."""
        # Convert to float for calculation, then back to Decimal
        y = float(taxable_income)
        total_tax = Decimal('0')
        
        # German tax formula for 2024/2025
        # We'll show all brackets up to the income level for consistency
        if y <= 12096:
            # Zone 1: Tax-free allowance
            total_tax = Decimal('0')
            result.income_tax_brackets.append(TaxBracket(
                lower_bound=Decimal('0'),
                upper_bound=Decimal('12096'),
                rate=Decimal('0'),
                taxable_amount=taxable_income,
                tax_amount=Decimal('0')
            ))
        elif y <= 68480:
            # Zone 2: Progressive formula (14% to ~24%)
            z = (y - 12096) / 10000
            tax = (922.98 * z + 1400) * z
            total_tax = Decimal(str(round(tax, 2)))
            
            # Show bracket with progressive rate range
            result.income_tax_brackets.append(TaxBracket(
                lower_bound=Decimal('12097'),
                upper_bound=Decimal('68480'),
                rate=Decimal('0.14'),  # Starting rate (progressive to ~24%)
                taxable_amount=taxable_income - Decimal('12096'),
                tax_amount=total_tax
            ))
        elif y <= 277825:
            # Zone 3: Progressive formula (~24% to 42%)
            # Calculate tax for zone 2 first
            z2 = (68480 - 12096) / 10000
            tax_zone2 = (922.98 * z2 + 1400) * z2
            
            # Calculate tax for zone 3
            z3 = (y - 68480) / 10000
            tax_zone3 = (181.19 * z3 + 2397) * z3 + 15694.52
            total_tax = Decimal(str(round(tax_zone3, 2)))
            
            # Show zone 2 bracket
            result.income_tax_brackets.append(TaxBracket(
                lower_bound=Decimal('12097'),
                upper_bound=Decimal('68480'),
                rate=Decimal('0.14'),  # Starting rate
                taxable_amount=Decimal('68480') - Decimal('12096'),
                tax_amount=Decimal(str(round(tax_zone2, 2)))
            ))
            
            # Show zone 3 bracket
            result.income_tax_brackets.append(TaxBracket(
                lower_bound=Decimal('68481'),
                upper_bound=Decimal('277825'),
                rate=Decimal('0.42'),  # Top rate of zone
                taxable_amount=taxable_income - Decimal('68480'),
                tax_amount=total_tax - Decimal(str(round(tax_zone2, 2)))
            ))
        else:
            # Zone 4: Top rate 45%
            # Calculate tax for zones 2 and 3
            z2 = (68480 - 12096) / 10000
            tax_zone2 = (922.98 * z2 + 1400) * z2
            
            z3 = (277825 - 68480) / 10000
            tax_zone3 = (181.19 * z3 + 2397) * z3 + 15694.52
            
            # Calculate total tax
            tax = 0.45 * y - 8394.14
            total_tax = Decimal(str(round(tax, 2)))
            
            # Show zone 2 bracket
            result.income_tax_brackets.append(TaxBracket(
                lower_bound=Decimal('12097'),
                upper_bound=Decimal('68480'),
                rate=Decimal('0.14'),
                taxable_amount=Decimal('68480') - Decimal('12096'),
                tax_amount=Decimal(str(round(tax_zone2, 2)))
            ))
            
            # Show zone 3 bracket
            result.income_tax_brackets.append(TaxBracket(
                lower_bound=Decimal('68481'),
                upper_bound=Decimal('277825'),
                rate=Decimal('0.42'),
                taxable_amount=Decimal('277825') - Decimal('68480'),
                tax_amount=Decimal(str(round(tax_zone3 - tax_zone2, 2)))
            ))
            
            # Show zone 4 bracket
            result.income_tax_brackets.append(TaxBracket(
                lower_bound=Decimal('277826'),
                upper_bound=Decimal('999999999'),
                rate=Decimal('0.45'),
                taxable_amount=taxable_income - Decimal('277825'),
                tax_amount=total_tax - Decimal(str(round(tax_zone3, 2)))
            ))
        
        # Add total income tax as deduction
        result.add_deduction(Deduction(
            name="Income Tax",
            amount=total_tax,
            rate=total_tax / taxable_income if taxable_income > 0 else Decimal('0'),
            description="Progressive income tax",
            calculation_details=f"German tax formula applied: {total_tax:,.0f} €"
        ))
        
        return total_tax
    
    def get_description(self) -> str:
        """Get description of German tax regime."""
        return """
        German Salaried Employee Tax Regime (Tax Class 1):
        
        This calculation applies to single employees without children in Germany.
        
        Key Features:
        - Progressive income tax with tax-free allowance of €12,096
        - Mandatory social security contributions (pension, health, unemployment, long-term care)
        - Solidarity surcharge (5.5%) on income tax above €19,450
        - Social security contributions are deducted from gross salary before income tax calculation
        
        Tax Brackets (2024/2025):
        - 0% on income up to €12,096 (tax-free allowance)
        - 14% on income €12,097 - €68,480
        - 42% on income €68,481 - €277,825
        - 45% on income above €277,826
        
        Social Security Rates (Employee Portion, 2024):
        - Pension Insurance: 9.3% (capped at €96,000)
        - Health Insurance: ~9.1% (7.3% base + ~1.8% average additional, capped at €62,100)
        - Unemployment Insurance: 1.3% (capped at €96,000)
        - Long-term Care Insurance: 2.0% (1.7% base + 0.3% childless surcharge, capped at €62,100)
        
        Note: Calculations use annual tax formula. Monthly calculations may differ slightly due to rounding.
        """
