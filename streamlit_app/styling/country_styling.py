"""
Country name styling for the sidebar.
"""

import streamlit as st


def apply_country_styling():
    """Apply styling for country names with emojis and darker background."""
    st.markdown("""
    <style>
    /* Country name styling with darker gray background - ONLY for sidebar */
    .stSidebar .country-name {
        background-color: #4a4a4a;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
        display: block;
        width: 100%;
        margin: 4px 0;
        box-sizing: border-box;
    }
    </style>
    """, unsafe_allow_html=True)
