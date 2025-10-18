"""
Sidebar component for language selection, salary input, and tax regime selection.
"""

import streamlit as st
from salary_compare.registry import TaxRegimeRegistry
from translations.translation_manager import set_language, get_translation_manager
from streamlit_app.config.constants import AVAILABLE_CURRENCIES
from streamlit_app.utils.country_utils import get_country_with_emoji


def render_sidebar():
    """
    Render the sidebar with all input controls.
    
    Returns:
        Tuple of (selected_regimes, salary, selected_currency)
    """
    with st.sidebar:
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
        
        # Create a local translation function
        def t(message: str) -> str:
            """Get translated message."""
            # Avoid passing empty strings to gettext as it returns metadata
            if not message or not message.strip():
                return message
            return get_translation_manager()._(message)
        
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
        selected_currency = st.selectbox(
            t("Choose display currency:"),
            options=list(AVAILABLE_CURRENCIES.keys()),
            format_func=lambda x: AVAILABLE_CURRENCIES[x],
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
            country_with_emoji = get_country_with_emoji(country, t(country))
            st.markdown(f'<span class="country-name">{country_with_emoji}</span>', unsafe_allow_html=True)
            for regime_key, title in regimes:
                # Use session state to preserve selections across language changes
                is_selected = regime_key in st.session_state.selected_regimes
                if st.checkbox(title, value=is_selected, key=regime_key, width="stretch"):
                    if regime_key not in st.session_state.selected_regimes:
                        st.session_state.selected_regimes.append(regime_key)
                    selected_regimes.append(regime_key)
                else:
                    if regime_key in st.session_state.selected_regimes:
                        st.session_state.selected_regimes.remove(regime_key)
        
        # Update selected_regimes from session state
        selected_regimes = st.session_state.selected_regimes.copy()
        
        return selected_regimes, salary, selected_currency
