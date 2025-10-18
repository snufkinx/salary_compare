"""
Country name styling for the sidebar.
"""

import streamlit as st


def apply_country_styling():
    """Apply adaptive styling for country names with emojis and background that works in both light and dark themes."""
    st.markdown("""
    <style>
    /* Country name styling with adaptive background - ONLY for sidebar */
    .stSidebar .country-name {
        /* Light theme colors */
        background-color: #e8e8e8;
        color: #262730;
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
        display: block;
        width: 100%;
        margin: 4px 0;
        box-sizing: border-box;
        border: 1px solid #d0d0d0;
    }
    
    /* Dark theme colors - when Streamlit is in dark mode */
    @media (prefers-color-scheme: dark) {
        .stSidebar .country-name {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #505050;
        }
    }
    
    /* Alternative approach using Streamlit's CSS variables if available */
    .stSidebar .country-name {
        background-color: var(--background-color-secondary, #e8e8e8);
        color: var(--text-color, #262730);
        border: 1px solid var(--border-color, #d0d0d0);
    }
    </style>
    """, unsafe_allow_html=True)
