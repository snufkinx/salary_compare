#!/usr/bin/env python3
"""
Salary Comparison Tool - Streamlit App
Interactive web interface for comparing net salaries across countries.
"""

import streamlit as st
import plotly.graph_objects as go
from decimal import Decimal
from salary_compare.registry import TaxRegimeRegistry
from salary_compare.universal_calculator import UniversalTaxCalculator
from salary_compare.services.currency import CurrencyConverter
from translations.translation_manager import set_language, get_translation_manager

# Page configuration
st.set_page_config(
    page_title="Salary Comparison Tool",
    page_icon="🌍",
    layout="wide"
)

# RTL support for Hebrew
def apply_rtl_support():
    """Apply RTL styling for Hebrew language."""
    if st.session_state.selected_language == 'he':
        st.markdown("""
        <style>
        /* RTL support for Hebrew */
        .main .block-container {
            direction: rtl;
            text-align: right;
        }
        
        /* RTL for sidebar */
        .css-1d391kg {
            direction: rtl;
        }
        
        /* RTL for tables */
        .stTable {
            direction: rtl;
        }
        
        /* RTL for table cells - ensure text aligns right within cells */
        .stTable td, .stTable th {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for table data specifically */
        .stTable tbody td {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for table headers */
        .stTable thead th {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for section headers (h1, h2, h3, etc.) */
        h1, h2, h3, h4, h5, h6 {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for subheaders and markdown headers */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for expanders */
        .streamlit-expander {
            direction: rtl !important;
        }
        
        /* RTL for expander headers */
        .streamlit-expanderHeader {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for expander header content */
        .streamlit-expanderHeader > div {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for expander header text */
        .streamlit-expanderHeader p {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for expander header span elements */
        .streamlit-expanderHeader span {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for expander header button elements */
        .streamlit-expanderHeader button {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for all elements within expander header */
        .streamlit-expanderHeader * {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* More specific targeting for expander header content */
        .streamlit-expanderHeader .streamlit-expanderHeaderContent {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* Target expander header text more specifically */
        .streamlit-expanderHeader .streamlit-expanderHeaderContent p,
        .streamlit-expanderHeader .streamlit-expanderHeaderContent div,
        .streamlit-expanderHeader .streamlit-expanderHeaderContent span {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* Force RTL for all text elements */
        .streamlit-expanderHeader p,
        .streamlit-expanderHeader div,
        .streamlit-expanderHeader span,
        .streamlit-expanderHeader strong,
        .streamlit-expanderHeader em {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for table headers within expanders */
        .streamlit-expanderContent table th {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for table headers in detailed breakdowns */
        .streamlit-expanderContent .stTable th {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for all table elements within expanders */
        .streamlit-expanderContent table {
            direction: rtl !important;
        }
        
        /* RTL for table cells within expanders */
        .streamlit-expanderContent table td {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* More specific targeting for all table elements */
        .streamlit-expanderContent .stTable th,
        .streamlit-expanderContent .stTable td,
        .streamlit-expanderContent .stTable thead th,
        .streamlit-expanderContent .stTable tbody td {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* Force RTL for all content within expanders */
        .streamlit-expanderContent * {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* Specific targeting for table headers in detailed breakdowns */
        .streamlit-expanderContent h1,
        .streamlit-expanderContent h2,
        .streamlit-expanderContent h3,
        .streamlit-expanderContent h4,
        .streamlit-expanderContent h5,
        .streamlit-expanderContent h6 {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for expander content */
        .streamlit-expanderContent {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for sidebar - move to right side */
        .css-1d391kg {
            order: 2 !important;
        }
        
        /* RTL for main content - move to left side */
        .main .block-container {
            order: 1 !important;
        }
        
        /* RTL for sidebar positioning */
        .stSidebar {
            order: 2 !important;
        }
        
        /* RTL for main content positioning */
        .main {
            order: 1 !important;
        }
        
        /* RTL for metrics */
        .metric-container {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for metric labels and values */
        .metric-label, .metric-value {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for st.metric components */
        .stMetric {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for st.metric label and value */
        .stMetric > div {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for selectbox and other inputs */
        .stSelectbox > div > div {
            direction: rtl;
            text-align: right;
        }
        
        /* RTL for number input */
        .stNumberInput > div > div > input {
            direction: rtl;
            text-align: right;
        }
        
        /* RTL for checkboxes */
        .stCheckbox > label {
            direction: rtl;
            text-align: right;
        }
        
        /* RTL for tabs */
        .stTabs > div > div > div {
            direction: rtl;
        }
        
        /* RTL for columns */
        .stColumns > div {
            direction: rtl;
        }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state for language and selected regimes
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'
if 'selected_regimes' not in st.session_state:
    st.session_state.selected_regimes = []

# Sidebar for inputs - MUST be first to set language before any content
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Language selector
    available_languages = get_translation_manager().get_available_languages()
    selected_language = st.selectbox(
        "🌍 Language",
        options=list(available_languages.keys()),
        format_func=lambda x: available_languages[x],
        index=list(available_languages.keys()).index(st.session_state.selected_language) if st.session_state.selected_language in available_languages else 0
    )
    
    # Update session state and set language
    if selected_language != st.session_state.selected_language:
        st.session_state.selected_language = selected_language
        st.rerun()
    
    set_language(selected_language)

# Apply RTL support for Hebrew
apply_rtl_support()

# Create a local translation function
def t(message: str) -> str:
    """Get translated message."""
    return get_translation_manager()._(message)

# Title
st.title(f"🌍 {t('Salary Comparison Tool')}")
st.markdown(t("Compare net salaries across different countries and employment types"))

# Sidebar for inputs
with st.sidebar:
    # Salary input
    salary = st.number_input(
        t("Gross Salary (€)"),
        min_value=1000,
        max_value=1000000,
        value=100000,
        step=1000,
        format="%d"
    )
    
    # Currency selection
    st.markdown(f"### 💱 {t('Display Currency')}")
    available_currencies = {
        "EUR": "€ Euro",
        "USD": "$ US Dollar", 
        "GBP": "£ British Pound",
        "CZK": "Kč Czech Koruna",
        "ILS": "₪ Israeli Shekel",
        "RON": "lei Romanian Leu",
        "BGN": "лв Bulgarian Lev"
    }
    
    selected_currency = st.selectbox(
        t("Choose display currency:"),
        options=list(available_currencies.keys()),
        format_func=lambda x: available_currencies[x],
        index=0  # Default to EUR
    )
    
    st.markdown(f"### {t('Select Tax Regimes')}")
    
    # Get available regimes and group by country
    available_regimes = TaxRegimeRegistry.get_keys()
    regimes_by_country = {}
    
    for regime_key in available_regimes:
        regime = TaxRegimeRegistry.get(regime_key)
        country = regime.country.value
        if country not in regimes_by_country:
            regimes_by_country[country] = []
        regimes_by_country[country].append((regime_key, t(regime.title)))
    
    # Create checkboxes grouped by country
    selected_regimes = []
    for country, regimes in regimes_by_country.items():
        st.markdown(f"**{t(country)}**")
        for regime_key, title in regimes:
            # Use session state to preserve selections across language changes
            is_selected = regime_key in st.session_state.selected_regimes
            if st.checkbox(title, value=is_selected, key=regime_key):
                if regime_key not in st.session_state.selected_regimes:
                    st.session_state.selected_regimes.append(regime_key)
                selected_regimes.append(regime_key)
            else:
                if regime_key in st.session_state.selected_regimes:
                    st.session_state.selected_regimes.remove(regime_key)
    
    # Update selected_regimes from session state
    selected_regimes = st.session_state.selected_regimes.copy()

# Currency conversion helper
def convert_amount(amount, currency):
    """Convert amount to selected currency."""
    converter = CurrencyConverter(from_currency="EUR", to_currency=currency)
    converted = converter.convert(Decimal(str(amount)))
    symbol = converter.symbol
    return converted, symbol

# Main content
if selected_regimes:
    # Calculate results
    results_with_keys = []
    with st.spinner(t("Calculating salaries...")):
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
    st.subheader(f"📊 {t('Summary Comparison')}")
    summary_data = []
    for result in results:
        effective_tax = (1 - float(result.net_salary/result.gross_salary)) * 100
        
        # Convert amounts to selected currency
        gross_converted, symbol = convert_amount(result.gross_salary, selected_currency)
        net_converted, _ = convert_amount(result.net_salary, selected_currency)
        gross_monthly_converted, _ = convert_amount(result.gross_salary/12, selected_currency)
        net_monthly_converted, _ = convert_amount(result.net_salary/12, selected_currency)
        tax_base_converted, _ = convert_amount(result.tax_base, selected_currency)
        
        summary_data.append({
            t("Country"): t(result.country),
            t("Gross Annual"): f"{symbol}{gross_converted:,.0f}",
            t("Net Annual"): f"{symbol}{net_converted:,.0f}",
            t("Gross Monthly"): f"{symbol}{gross_monthly_converted:,.0f}",
            t("Net Monthly"): f"{symbol}{net_monthly_converted:,.0f}",
            t("Tax %"): f"{effective_tax:.1f}%"
        })
    
    # Use st.table for better font control
    st.table(summary_data)
    
    # Comparison chart
    if len(results) > 1:
        st.subheader(f"📈 {t('Comparison Chart')}")
        
        # Create tabs for different chart views
        tab1, tab2 = st.tabs([f"📊 {t('Country Comparison')}", f"📈 {t('Salary Progression')}"])
        
        with tab1:
            # Country comparison (existing bars + tax rates)
            countries = [t(r.country) for r in results]
            net_salaries = [float(r.net_salary) for r in results]
            tax_rates = [(1 - float(r.net_salary/r.gross_salary))*100 for r in results]
            
            # Convert net salaries to selected currency
            net_salaries_converted = []
            for net_salary in net_salaries:
                converted, symbol = convert_amount(net_salary, selected_currency)
                net_salaries_converted.append(float(converted))
            
            fig1 = go.Figure()
            
            # Net salary bars
            fig1.add_trace(go.Bar(
                name=t('Net Salary'),
                x=countries,
                y=net_salaries_converted,
                yaxis='y',
                offsetgroup=1,
                marker_color='#2E8B57',
                text=[f"{symbol}{s:,.0f}" for s in net_salaries_converted],
                textposition='auto',
                hovertemplate=f'<b>%{{x}}</b><br>{t("Net Salary")}: {symbol}%{{y:,.0f}}<br><extra></extra>'
            ))
            
            # Tax rate line
            fig1.add_trace(go.Scatter(
                name=t('Tax Rate %'),
                x=countries,
                y=tax_rates,
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#DC143C', width=3),
                marker=dict(size=8),
                text=[f"{t:.1f}%" for t in tax_rates],
                textposition='top center',
                hovertemplate=f'<b>%{{x}}</b><br>{t("Tax Rate %")}: %{{y:.1f}}%<br><extra></extra>'
            ))
            
            # Get currency symbol for display
            _, symbol = convert_amount(1, selected_currency)
            
            fig1.update_layout(
                title=f"{t('Country Comparison')} ({symbol}{salary:,} {t('Gross Salary')})",
                xaxis_title=t('Countries'),
                yaxis=dict(title=f"{t('Net Salary')} ({symbol})", side='left'),
                yaxis2=dict(title=f"{t('Tax Rate %')} (%)", side='right', overlaying='y'),
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            # Salary progression chart (like HTML report)
            # Generate data points for different gross salaries
            max_gross = float(salary)
            x_values = list(range(0, int(max_gross * 2) + 10000, 10000))
            
            # Convert x_values to selected currency
            x_values_converted = []
            for gross in x_values:
                converted, _ = convert_amount(gross, selected_currency)
                x_values_converted.append(float(converted))
            
            fig2 = go.Figure()
            
            # Colors for different countries
            colors = ['#667eea', '#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40']
            
            # Get currency symbol for display
            _, symbol = convert_amount(1, selected_currency)
            
            for i, result in enumerate(results):
                # Calculate net salary for each gross salary point
                regime = TaxRegimeRegistry.get(regime_keys[i])
                net_values = []
                
                for gross in x_values:
                    if gross > 0:
                        calc = UniversalTaxCalculator(Decimal(str(gross)), regime)
                        net_result = calc.calculate_net_salary()
                        # Convert net salary to selected currency
                        net_converted, _ = convert_amount(net_result.net_salary, selected_currency)
                        net_values.append(float(net_converted))
                    else:
                        net_values.append(0)
                
                # Add line for this country/employment type
                country_name = t(result.country)
                employment_name = t(result.employment_type)
                # Create a simple legend name to avoid any translation issues
                legend_name = f'{country_name} - {employment_name}'
                
                fig2.add_trace(go.Scatter(
                    name=legend_name,
                    x=x_values_converted,
                    y=net_values,
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{country_name} {employment_name}</b><br>' +
                                f'{t("Gross:")} {symbol}%{{x:,.0f}}<br>' +
                                f'{t("Net:")} {symbol}%{{y:,.0f}}<br>' +
                                '<extra></extra>'
                ))
            
            fig2.update_layout(
                title=t('Net Salary vs Gross Salary Progression'),
                xaxis_title=f"{t('Gross Salary')} ({symbol})",
                yaxis_title=f"{t('Net Salary')} ({symbol})",
                hovermode='x unified',
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.01
                ),
                margin=dict(r=200, l=50, t=50, b=50)  # Better margins for layout
            )
            
            # Add current salary point as vertical line
            current_salary_converted, _ = convert_amount(salary, selected_currency)
            fig2.add_vline(
                x=float(current_salary_converted), 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Current: {symbol}{current_salary_converted:,.0f}",
                annotation_position="top"
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed breakdowns
    st.subheader(f"🔍 {t('Detailed Breakdowns')}")
    
    for i, result in enumerate(results):
        with st.expander(f"📊 {t(result.country)}", expanded=True):
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

else:
    st.info(f"👈 {t('Please select at least one tax regime from the sidebar to see calculations.')}")

# Footer
st.markdown("---")
st.markdown(f"*{t('Change inputs in the sidebar to see real-time updates')}*")
