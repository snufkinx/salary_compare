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
        
        summary_data.append({
            "Country": result.country,
            "Gross": f"€{result.gross_salary:,.0f}",
            "Net": f"€{result.net_salary:,.0f}",
            "Monthly": f"€{result.net_salary/12:,.0f}",
            "Tax %": f"{effective_tax:.1f}%"
        })
    
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
            
            fig1 = go.Figure()
            
            # Net salary bars
            fig1.add_trace(go.Bar(
                name='Net Salary',
                x=countries,
                y=net_salaries,
                yaxis='y',
                offsetgroup=1,
                marker_color='#2E8B57',
                text=[f"€{s:,.0f}" for s in net_salaries],
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
            
            fig1.update_layout(
                title=f'Country Comparison (€{salary:,} Gross)',
                xaxis_title='Countries',
                yaxis=dict(title='Net Salary (€)', side='left'),
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
            
            fig2 = go.Figure()
            
            # Colors for different countries
            colors = ['#667eea', '#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40']
            
            for i, result in enumerate(results):
                # Calculate net salary for each gross salary point
                regime = TaxRegimeRegistry.get(regime_keys[i])
                net_values = []
                
                for gross in x_values:
                    if gross > 0:
                        calc = UniversalTaxCalculator(Decimal(str(gross)), regime)
                        net_result = calc.calculate_net_salary()
                        net_values.append(float(net_result.net_salary))
                    else:
                        net_values.append(0)
                
                # Add line for this country/employment type
                fig2.add_trace(go.Scatter(
                    name=f'{result.country} {result.employment_type}',
                    x=x_values,
                    y=net_values,
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{result.country} {result.employment_type}</b><br>' +
                                'Gross: €%{x:,.0f}<br>' +
                                'Net: €%{y:,.0f}<br>' +
                                '<extra></extra>'
                ))
            
            fig2.update_layout(
                title='Net Salary vs Gross Salary Progression',
                xaxis_title='Gross Salary (€)',
                yaxis_title='Net Salary (€)',
                hovermode='x unified',
                height=500,
                showlegend=True
            )
            
            # Add current salary point as vertical line
            fig2.add_vline(
                x=float(salary), 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Current: €{salary:,}",
                annotation_position="top"
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed breakdowns
    st.subheader("🔍 Detailed Breakdowns")
    
    for i, result in enumerate(results):
        with st.expander(f"📊 {result.country}", expanded=(i == 0)):
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Gross Salary", f"€{result.gross_salary:,.0f}")
            with col2:
                st.metric("Net Salary", f"€{result.net_salary:,.0f}")
            with col3:
                st.metric("Monthly Net", f"€{result.net_salary/12:,.0f}")
            with col4:
                effective_tax = (1 - float(result.net_salary/result.gross_salary)) * 100
                st.metric("Effective Tax", f"{effective_tax:.1f}%")
            
            # Tax base
            st.markdown(f"**Tax Base:** €{result.tax_base:,.2f}")
            
            # Deductions breakdown
            st.markdown("**Deductions:**")
            deduction_data = []
            for deduction in result.deductions:
                deduction_data.append({
                    "Deduction": deduction.name,
                    "Amount": f"€{deduction.amount:,.2f}",
                    "Rate": f"{float(deduction.rate)*100:.1f}%",
                    "Details": deduction.description
                })
            
            st.table(deduction_data)
            
            # Tax brackets if available
            if hasattr(result, 'income_tax_brackets') and result.income_tax_brackets:
                st.markdown("**Income Tax Brackets:**")
                bracket_data = []
                for bracket in result.income_tax_brackets:
                    bracket_data.append({
                        "Bracket": f"€{bracket.lower_bound:,.0f} - €{bracket.upper_bound:,.0f}",
                        "Rate": f"{float(bracket.rate)*100:.1f}%",
                        "Taxable Amount": f"€{bracket.taxable_amount:,.2f}",
                        "Tax Amount": f"€{bracket.tax_amount:,.2f}"
                    })
                st.table(bracket_data)

else:
    st.info("👈 Please select at least one tax regime from the sidebar to see calculations.")

# Footer
st.markdown("---")
st.markdown("*Change inputs in the sidebar to see real-time updates*")
