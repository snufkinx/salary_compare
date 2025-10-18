"""
Country and emoji utility functions.
"""

import streamlit as st
from streamlit_app.config.constants import COUNTRY_EMOJIS


def get_country_with_emoji(country_name: str, translated_name: str = None) -> str:
    """Get country name with emoji."""
    # Extract country name from regime title if it contains employment type
    # e.g., "Germany Salaried Employee" -> "Germany"
    country_key = country_name
    
    # First, try to find a country name in the title
    for country in COUNTRY_EMOJIS.keys():
        if country in country_name:
            country_key = country
            break
    
    # If no country found, check for Spanish regions
    if country_key == country_name:  # No country found yet
        spanish_regions = ['Madrid', 'Barcelona', 'Valencia']
        for region in spanish_regions:
            if region in country_name:
                country_key = 'Spain'
                break
    
    # Use the extracted country name for emoji lookup
    emoji = COUNTRY_EMOJIS.get(country_key, "🌍")
    # Use translated name if provided, otherwise use original
    display_name = translated_name if translated_name else country_name
    
    # For RTL languages (Hebrew and Arabic), put emoji on the right side
    if st.session_state.selected_language in ['he', 'ar']:
        return f"{display_name} {emoji}"
    else:
        return f"{emoji} {display_name}"
