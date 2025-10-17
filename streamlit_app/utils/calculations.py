"""
Salary calculation utilities.
"""

from decimal import Decimal
from salary_compare.registry import TaxRegimeRegistry
from salary_compare.universal_calculator import UniversalTaxCalculator


def calculate_salaries(selected_regimes, salary):
    """
    Calculate salaries for selected tax regimes.
    
    Args:
        selected_regimes: List of selected regime keys
        salary: Gross salary amount
        
    Returns:
        Tuple of (results, regime_keys) sorted by net salary
    """
    results_with_keys = []
    
    for regime_key in selected_regimes:
        regime = TaxRegimeRegistry.get(regime_key)
        calc = UniversalTaxCalculator(Decimal(str(salary)), regime)
        result = calc.calculate_net_salary()
        results_with_keys.append((result, regime_key))
    
    # Sort by net salary (highest first)
    results_with_keys.sort(key=lambda x: x[0].net_salary, reverse=True)
    
    # Extract sorted results and regime keys
    results = [item[0] for item in results_with_keys]
    regime_keys = [item[1] for item in results_with_keys]
    
    return results, regime_keys
