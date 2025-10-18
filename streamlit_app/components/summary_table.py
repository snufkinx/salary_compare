"""
Summary comparison table component.
"""

import streamlit as st
from salary_compare.registry import TaxRegimeRegistry
from salary_compare.services.currency import CurrencyConverter
from streamlit_app.utils.country_utils import get_country_with_emoji
from translations.translation_manager import get_translation_manager


def render_summary_table(results, regime_keys, selected_currency):
    """
    Render the summary comparison table.
    
    Args:
        results: List of calculation results
        regime_keys: List of regime keys corresponding to results
        selected_currency: Selected currency for display
    """
    def t(message: str) -> str:
        """Get translated message."""
        return get_translation_manager()._(message)
    
    def convert_amount(amount, currency):
        """Convert amount to selected currency."""
        from decimal import Decimal
        converter = CurrencyConverter(from_currency="EUR", to_currency=currency)
        converted = converter.convert(Decimal(str(amount)))
        symbol = converter.symbol
        return float(converted), symbol
    
    st.subheader(f"📊 {t('Summary Comparison')}")
    summary_data = []
    
    for i, result in enumerate(results):
        effective_tax = (1 - float(result.net_salary/result.gross_salary)) * 100
        
        # Convert amounts to selected currency
        gross_converted, symbol = convert_amount(result.gross_salary, selected_currency)
        net_converted, _ = convert_amount(result.net_salary, selected_currency)
        gross_monthly_converted, _ = convert_amount(result.gross_salary/12, selected_currency)
        net_monthly_converted, _ = convert_amount(result.net_salary/12, selected_currency)
        
        # Get the regime to extract the actual country name
        regime = TaxRegimeRegistry.get(regime_keys[i])
        country_name = regime.country.value
        country_with_emoji = get_country_with_emoji(country_name, t(country_name))
        
        summary_data.append({
            t("Country"): country_with_emoji,
            t("Tax Regime"): t(regime.title),
            t("Gross Annual"): f"{symbol}{gross_converted:,.0f}",
            t("Net Annual"): f"{symbol}{net_converted:,.0f}",
            t("Gross Monthly"): f"{symbol}{gross_monthly_converted:,.0f}",
            t("Net Monthly"): f"{symbol}{net_monthly_converted:,.0f}",
            t("Tax %"): f"{effective_tax:.1f}%"
        })
    
    # Display the table
    if summary_data:
        st.table(summary_data)
