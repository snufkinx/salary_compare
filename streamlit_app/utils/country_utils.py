"""
Country and emoji utility functions.
"""

import streamlit as st
from streamlit_app.config.constants import COUNTRY_EMOJIS


def get_country_with_emoji(country_name: str, translated_name: str = None) -> str:
    """Get country name with emoji."""
    # Use the original country name for emoji lookup
    emoji = COUNTRY_EMOJIS.get(country_name, "🌍")
    # Use translated name if provided, otherwise use original
    display_name = translated_name if translated_name else country_name
    
    # For RTL languages (Hebrew and Arabic), put emoji on the right side
    if st.session_state.selected_language in ['he', 'ar']:
        return f"{display_name} {emoji}"
    else:
        return f"{emoji} {display_name}"
