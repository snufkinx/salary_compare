#!/usr/bin/env python3
"""
Example of how to integrate translations into the Streamlit app.
This shows the pattern for adding i18n support.
"""

import streamlit as st
from decimal import Decimal
from salary_compare.registry import TaxRegimeRegistry
from salary_compare.universal_calculator import UniversalTaxCalculator
from translations.i18n import set_language, _, get_translation_manager

# Page configuration
st.set_page_config(
    page_title="Salary Comparison Tool",
    page_icon="🌍",
    layout="wide"
)

# Language selection (this would go in sidebar)
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Language selector
    available_languages = get_translation_manager().get_available_languages()
    selected_language = st.selectbox(
        "🌍 Language / Idioma / Langue",
        options=list(available_languages.keys()),
        format_func=lambda x: available_languages[x],
        index=0
    )
    
    # Set the language
    set_language(selected_language)

# Title (now using translations)
st.title(f"🌍 {_('app_title')}")
st.markdown(_('app_description'))

# Sidebar for inputs
with st.sidebar:
    st.header(f"⚙️ {_('configuration')}")
    
    # Salary input
    salary = st.number_input(
        _('gross_salary'),
        min_value=1000,
        max_value=1000000,
        value=100000,
        step=1000,
        format="%d"
    )
    
    st.markdown(f"### {_('select_tax_regimes')}")
    
    # Get available regimes and group by country
    available_regimes = TaxRegimeRegistry.get_keys()
    regimes_by_country = {}
    
    for regime_key in available_regimes:
        regime = TaxRegimeRegistry.get(regime_key)
        country = regime.country.value
        if country not in regimes_by_country:
            regimes_by_country[country] = []
        regimes_by_country[country].append((regime_key, regime.title))
    
    # Create checkboxes grouped by country
    selected_regimes = []
    for country, regimes in regimes_by_country.items():
        st.markdown(f"**{country}**")
        for regime_key, title in regimes:
            if st.checkbox(title, key=regime_key):
                selected_regimes.append(regime_key)

# Main content
if selected_regimes:
    # Calculate results
    results_with_keys = []
    with st.spinner(_('calculating_salaries')):
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
    
    # Summary comparison table
    st.subheader(f"📊 {_('summary_comparison')}")
    summary_data = []
    for result in results:
        effective_tax = (1 - float(result.net_salary/result.gross_salary)) * 100
        
        summary_data.append({
            _('country'): result.country,
            _('gross_annual'): f"€{result.gross_salary:,.0f}",
            _('net_annual'): f"€{result.net_salary:,.0f}",
            _('gross_monthly'): f"€{result.gross_salary/12:,.0f}",
            _('net_monthly'): f"€{result.net_salary/12:,.0f}",
            _('tax_percentage'): f"{effective_tax:.1f}%"
        })
    
    st.table(summary_data)
    
    # Detailed breakdowns
    st.subheader(f"🔍 {_('detailed_breakdowns')}")
    
    for i, result in enumerate(results):
        with st.expander(f"📊 {result.country}", expanded=True):
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(_('gross_salary_metric'), f"€{result.gross_salary:,.0f}")
            with col2:
                st.metric(_('net_salary_metric'), f"€{result.net_salary:,.0f}")
            with col3:
                st.metric(_('monthly_net_metric'), f"€{result.net_salary/12:,.0f}")
            with col4:
                effective_tax = (1 - float(result.net_salary/result.gross_salary)) * 100
                st.metric(_('effective_tax_metric'), f"{effective_tax:.1f}%")
            
            # Tax base
            st.markdown(f"**{_('tax_base')}:** €{result.tax_base:,.2f}")
            
            # Deductions breakdown
            st.markdown(f"**{_('deductions')}:**")
            deduction_data = []
            for deduction in result.deductions:
                deduction_data.append({
                    _('deduction'): deduction.name,
                    _('amount'): f"€{deduction.amount:,.2f}",
                    _('rate'): f"{float(deduction.rate)*100:.1f}%",
                    _('details'): deduction.description
                })
            
            st.table(deduction_data)

else:
    st.info(f"👈 {_('please_select_regimes')}")

# Footer
st.markdown("---")
st.markdown(f"*{_('change_inputs')}*")
