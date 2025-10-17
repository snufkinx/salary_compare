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

# Page configuration
st.set_page_config(
    page_title="Salary Comparison Tool",
    page_icon="🌍",
    layout="wide"
)

# Title
st.title("🌍 Salary Comparison Tool")
st.markdown("Compare net salaries across different countries and employment types")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Salary input
    salary = st.number_input(
        "Gross Salary (€)",
        min_value=1000,
        max_value=1000000,
        value=100000,
        step=1000,
        format="%d"
    )
    
    # Currency selection
    st.markdown("### 💱 Display Currency")
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
        "Choose display currency:",
        options=list(available_currencies.keys()),
        format_func=lambda x: available_currencies[x],
        index=0  # Default to EUR
    )
    
    st.markdown("### Select Tax Regimes")
    
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
    with st.spinner("Calculating salaries..."):
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
    st.subheader("📊 Summary Comparison")
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
            "Country": result.country,
            "Gross Annual": f"{symbol}{gross_converted:,.0f}",
            "Net Annual": f"{symbol}{net_converted:,.0f}",
            "Gross Monthly": f"{symbol}{gross_monthly_converted:,.0f}",
            "Net Monthly": f"{symbol}{net_monthly_converted:,.0f}",
            "Tax %": f"{effective_tax:.1f}%"
        })
    
    # Use st.table for better font control
    st.table(summary_data)
    
    # Comparison chart
    if len(results) > 1:
        st.subheader("📈 Comparison Chart")
        
        # Create tabs for different chart views
        tab1, tab2 = st.tabs(["📊 Country Comparison", "📈 Salary Progression"])
        
        with tab1:
            # Country comparison (existing bars + tax rates)
            countries = [r.country for r in results]
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
                name='Net Salary',
                x=countries,
                y=net_salaries_converted,
                yaxis='y',
                offsetgroup=1,
                marker_color='#2E8B57',
                text=[f"{symbol}{s:,.0f}" for s in net_salaries_converted],
                textposition='auto'
            ))
            
            # Tax rate line
            fig1.add_trace(go.Scatter(
                name='Tax Rate %',
                x=countries,
                y=tax_rates,
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#DC143C', width=3),
                marker=dict(size=8),
                text=[f"{t:.1f}%" for t in tax_rates],
                textposition='top center'
            ))
            
            # Get currency symbol for display
            _, currency_symbol = convert_amount(1, selected_currency)
            
            fig1.update_layout(
                title=f'Country Comparison ({currency_symbol}{salary:,} Gross)',
                xaxis_title='Countries',
                yaxis=dict(title=f'Net Salary ({currency_symbol})', side='left'),
                yaxis2=dict(title='Tax Rate (%)', side='right', overlaying='y'),
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
            _, currency_symbol = convert_amount(1, selected_currency)
            
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
                fig2.add_trace(go.Scatter(
                    name=f'{result.country} {result.employment_type}',
                    x=x_values_converted,
                    y=net_values,
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{result.country} {result.employment_type}</b><br>' +
                                f'Gross: {currency_symbol}%{{x:,.0f}}<br>' +
                                f'Net: {currency_symbol}%{{y:,.0f}}<br>' +
                                '<extra></extra>'
                ))
            
            fig2.update_layout(
                title='Net Salary vs Gross Salary Progression',
                xaxis_title=f'Gross Salary ({currency_symbol})',
                yaxis_title=f'Net Salary ({currency_symbol})',
                hovermode='x unified',
                height=500,
                showlegend=True
            )
            
            # Add current salary point as vertical line
            current_salary_converted, _ = convert_amount(salary, selected_currency)
            fig2.add_vline(
                x=float(current_salary_converted), 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Current: {currency_symbol}{current_salary_converted:,.0f}",
                annotation_position="top"
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed breakdowns
    st.subheader("🔍 Detailed Breakdowns")
    
    for i, result in enumerate(results):
        with st.expander(f"📊 {result.country}", expanded=(i == 0)):
            # Convert amounts to selected currency
            gross_converted, symbol = convert_amount(result.gross_salary, selected_currency)
            net_converted, _ = convert_amount(result.net_salary, selected_currency)
            monthly_converted, _ = convert_amount(result.net_salary/12, selected_currency)
            tax_base_converted, _ = convert_amount(result.tax_base, selected_currency)
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Gross Salary", f"{symbol}{gross_converted:,.0f}")
            with col2:
                st.metric("Net Salary", f"{symbol}{net_converted:,.0f}")
            with col3:
                st.metric("Monthly Net", f"{symbol}{monthly_converted:,.0f}")
            with col4:
                effective_tax = (1 - float(result.net_salary/result.gross_salary)) * 100
                st.metric("Effective Tax", f"{effective_tax:.1f}%")
            
            # Tax base
            st.markdown(f"**Tax Base:** {symbol}{tax_base_converted:,.2f}")
            
            # Deductions breakdown
            st.markdown("**Deductions:**")
            deduction_data = []
            for deduction in result.deductions:
                # Convert deduction amount to selected currency
                deduction_converted, _ = convert_amount(deduction.amount, selected_currency)
                deduction_data.append({
                    "Deduction": deduction.name,
                    "Amount": f"{symbol}{deduction_converted:,.2f}",
                    "Rate": f"{float(deduction.rate)*100:.1f}%",
                    "Details": deduction.description
                })
            
            st.table(deduction_data)
            
            # Tax brackets if available
            if hasattr(result, 'income_tax_brackets') and result.income_tax_brackets:
                st.markdown("**Income Tax Brackets:**")
                bracket_data = []
                for bracket in result.income_tax_brackets:
                    # Convert bracket amounts to selected currency
                    lower_converted, _ = convert_amount(bracket.lower_bound, selected_currency)
                    upper_converted, _ = convert_amount(bracket.upper_bound, selected_currency)
                    taxable_converted, _ = convert_amount(bracket.taxable_amount, selected_currency)
                    tax_converted, _ = convert_amount(bracket.tax_amount, selected_currency)
                    
                    bracket_data.append({
                        "Bracket": f"{symbol}{lower_converted:,.0f} - {symbol}{upper_converted:,.0f}",
                        "Rate": f"{float(bracket.rate)*100:.1f}%",
                        "Taxable Amount": f"{symbol}{taxable_converted:,.2f}",
                        "Tax Amount": f"{symbol}{tax_converted:,.2f}"
                    })
                st.table(bracket_data)

else:
    st.info("👈 Please select at least one tax regime from the sidebar to see calculations.")

# Footer
st.markdown("---")
st.markdown("*Change inputs in the sidebar to see real-time updates*")
