"""
Chart components for salary comparison visualization.
"""

import streamlit as st
import plotly.graph_objects as go
from salary_compare.registry import TaxRegimeRegistry
from salary_compare.services.currency import CurrencyConverter
from streamlit_app.utils.country_utils import get_country_with_emoji
from translations.translation_manager import get_translation_manager


def render_comparison_charts(results, regime_keys, selected_currency, salary):
    """
    Render comparison charts.
    
    Args:
        results: List of calculation results
        regime_keys: List of regime keys corresponding to results
        selected_currency: Selected currency for display
        salary: Original salary amount
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
    
    if len(results) <= 1:
        return
    
    st.subheader(f"📈 {t('Comparison Chart')}")
    
    # Create tabs for different chart views
    tab1, tab2 = st.tabs([f"📊 {t('Country Comparison')}", f"📈 {t('Salary Progression')}"])
    
    with tab1:
        # Country comparison (existing bars + tax rates)
        countries = [get_country_with_emoji(r.country, t(r.country)) for r in results]
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
        # Salary progression chart
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
                    from decimal import Decimal
                    from salary_compare.universal_calculator import UniversalTaxCalculator
                    calc = UniversalTaxCalculator(Decimal(str(gross)), regime)
                    net_result = calc.calculate_net_salary()
                    # Convert net salary to selected currency
                    net_converted, _ = convert_amount(net_result.net_salary, selected_currency)
                    net_values.append(float(net_converted))
                else:
                    net_values.append(0)
            
            # Add line for this country/employment type
            country_name = get_country_with_emoji(result.country, t(result.country))
            employment_name = t(result.employment_type)
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
            margin=dict(r=200, l=50, t=50, b=50)
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
