"""CSV output formatter."""

import csv
from typing import List, Optional
from ..models.tax_result import TaxResult


class CSVOutput:
    """CSV output formatter."""
    
    def render_single(self, result: TaxResult, output_file: Optional[str] = None):
        """Render single calculation result to CSV."""
        filename = output_file or "salary_calculation.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header information
            writer.writerow(['Salary Calculation Report'])
            writer.writerow(['Country', result.country])
            writer.writerow(['Employment Type', result.employment_type])
            writer.writerow(['Gross Salary', f"{result.gross_salary:.2f}"])
            writer.writerow(['Tax Base', f"{result.tax_base:.2f}"])
            writer.writerow(['Net Salary', f"{result.net_salary:.2f}"])
            writer.writerow(['Total Deductions', f"{result.total_deductions:.2f}"])
            writer.writerow([])  # Empty row
            
            # Detailed breakdown
            writer.writerow(['Detailed Breakdown'])
            writer.writerow(['Deduction Type', 'Amount', 'Rate (%)', 'Description', 'Calculation Details'])
            
            for deduction in result.deductions:
                writer.writerow([
                    deduction.name,
                    f"{deduction.amount:.2f}",
                    f"{deduction.rate * 100:.1f}",
                    deduction.description,
                    deduction.calculation_details
                ])
            
            # Tax brackets if available
            if result.income_tax_brackets:
                writer.writerow([])  # Empty row
                writer.writerow(['Income Tax Brackets'])
                writer.writerow(['Lower Bound', 'Upper Bound', 'Rate (%)', 'Taxable Amount', 'Tax Amount'])
                
                for bracket in result.income_tax_brackets:
                    writer.writerow([
                        f"{bracket.lower_bound:.2f}",
                        f"{bracket.upper_bound:.2f}",
                        f"{bracket.rate * 100:.1f}",
                        f"{bracket.taxable_amount:.2f}",
                        f"{bracket.tax_amount:.2f}"
                    ])
        
        print(f"CSV report saved to: {filename}")
    
    def render_comparison(self, results: List[TaxResult], output_file: Optional[str] = None):
        """Render comparison of multiple calculations to CSV."""
        filename = output_file or "salary_comparison.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Comparison summary
            writer.writerow(['Salary Comparison Report'])
            writer.writerow([])  # Empty row
            writer.writerow(['Country/Type', 'Gross Salary', 'Tax Base', 'Total Deductions', 'Net Salary', 'Net %'])
            
            for result in results:
                net_percentage = (result.net_salary / result.gross_salary) * 100 if result.gross_salary > 0 else 0
                writer.writerow([
                    f"{result.country} {result.employment_type}",
                    f"{result.gross_salary:.2f}",
                    f"{result.tax_base:.2f}",
                    f"{result.total_deductions:.2f}",
                    f"{result.net_salary:.2f}",
                    f"{net_percentage:.1f}"
                ])
            
            # Detailed breakdown for each result
            for i, result in enumerate(results):
                writer.writerow([])  # Empty row
                writer.writerow([f'Detailed Breakdown {i+1}: {result.country} {result.employment_type}'])
                writer.writerow(['Deduction Type', 'Amount', 'Rate (%)', 'Description', 'Calculation Details'])
                
                for deduction in result.deductions:
                    writer.writerow([
                        deduction.name,
                        f"{deduction.amount:.2f}",
                        f"{deduction.rate * 100:.1f}",
                        deduction.description,
                        deduction.calculation_details
                    ])
        
        print(f"CSV comparison report saved to: {filename}")
