"""
Detailed breakdown component for individual country results.
"""

import streamlit as st
from salary_compare.registry import TaxRegimeRegistry
from salary_compare.services.currency import CurrencyConverter
from streamlit_app.utils.country_utils import get_country_with_emoji
from translations.translation_manager import get_translation_manager


def render_detailed_breakdowns(results, regime_keys, selected_currency):
    """
    Render detailed breakdowns for each country.
    
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
        converter = CurrencyConverter(from_currency="EUR", to_currency=currency)
        converted = converter.convert(amount)
        symbol = converter.symbol
        return converted, symbol
    
    st.subheader(f"🔍 {t('Detailed Breakdowns')}")
    
    for i, result in enumerate(results):
        country_with_emoji = get_country_with_emoji(result.country, t(result.country))
        with st.expander(f"📊 {country_with_emoji}", expanded=True):
            # Convert amounts to selected currency
            gross_converted, symbol = convert_amount(result.gross_salary, selected_currency)
            net_converted, _ = convert_amount(result.net_salary, selected_currency)
            monthly_converted, _ = convert_amount(result.net_salary/12, selected_currency)
            tax_base_converted, _ = convert_amount(result.tax_base, selected_currency)
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(t("Gross Salary"), f"{symbol}{gross_converted:,.0f}")
            with col2:
                st.metric(t("Net Salary"), f"{symbol}{net_converted:,.0f}")
            with col3:
                st.metric(t("Monthly Net"), f"{symbol}{monthly_converted:,.0f}")
            with col4:
                effective_tax = (1 - float(result.net_salary/result.gross_salary)) * 100
                st.metric(t("Effective Tax"), f"{effective_tax:.1f}%")
            
            # Tax base
            st.markdown(f"**{t('Tax Base')}:** {symbol}{tax_base_converted:,.2f}")
            
            # Deductions breakdown
            st.markdown(f"**{t('Deductions')}:**")
            deduction_data = []
            for deduction in result.deductions:
                # Convert deduction amount to selected currency
                deduction_converted, _ = convert_amount(deduction.amount, selected_currency)
                deduction_data.append({
                    t("Deduction"): t(deduction.name),
                    t("Amount"): f"{symbol}{deduction_converted:,.2f}",
                    t("Rate"): f"{float(deduction.rate)*100:.1f}%",
                    t("Details"): t(deduction.description)
                })
            
            st.table(deduction_data)
            
            # Tax brackets if available
            if hasattr(result, 'income_tax_brackets') and result.income_tax_brackets:
                st.markdown(f"**{t('Income Tax Brackets')}:**")
                bracket_data = []
                for bracket in result.income_tax_brackets:
                    # Convert bracket amounts to selected currency
                    lower_converted, _ = convert_amount(bracket.lower_bound, selected_currency)
                    upper_converted, _ = convert_amount(bracket.upper_bound, selected_currency)
                    taxable_converted, _ = convert_amount(bracket.taxable_amount, selected_currency)
                    tax_converted, _ = convert_amount(bracket.tax_amount, selected_currency)
                    
                    bracket_data.append({
                        t("Bracket"): f"{symbol}{lower_converted:,.0f} - {symbol}{upper_converted:,.0f}",
                        t("Rate"): f"{float(bracket.rate)*100:.1f}%",
                        t("Taxable Amount"): f"{symbol}{taxable_converted:,.2f}",
                        t("Tax Amount"): f"{symbol}{tax_converted:,.2f}"
                    })
                st.table(bracket_data)
