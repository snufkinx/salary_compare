#!/usr/bin/env python3
"""
Salary Comparison Tool - Refactored Streamlit App
Clean, modular interface for comparing net salaries across countries.
"""

import streamlit as st
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.summary_table import render_summary_table
from streamlit_app.components.charts import render_comparison_charts
from streamlit_app.components.detailed_breakdown import render_detailed_breakdowns
from streamlit_app.styling.rtl_support import apply_rtl_support
from streamlit_app.styling.country_styling import apply_country_styling
from streamlit_app.utils.calculations import calculate_salaries
from translations.translation_manager import get_translation_manager


def initialize_session_state():
    """Initialize session state variables."""
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = 'en'
    if 'selected_regimes' not in st.session_state:
        st.session_state.selected_regimes = []


def streamlit_app():
    """Streamlit application logic."""
    # Page configuration
    st.set_page_config(
        page_title="Salary Comparison Tool",
        page_icon="🌍",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get user inputs
    selected_regimes, salary, selected_currency = render_sidebar()
    
    # Apply styling
    apply_rtl_support()
    apply_country_styling()
    
    # Title
    def t(message: str) -> str:
        """Get translated message."""
        return get_translation_manager()._(message)
    
    st.title(f"🌍 {t('Salary Comparison Tool')}")
    st.markdown(t("Compare net salaries across different countries and employment types"))
    
    # Main content
    if selected_regimes:
        # Calculate results
        results, regime_keys = calculate_salaries(selected_regimes, salary)
        
        # Render components
        render_summary_table(results, regime_keys, selected_currency)
        render_comparison_charts(results, regime_keys, selected_currency, salary)
        render_detailed_breakdowns(results, regime_keys, selected_currency)
    else:
        st.info(f"👈 {t('Please select at least one tax regime from the sidebar to see calculations.')}")
    
    # Footer
    st.markdown("---")
    st.markdown(f"*{t('Change inputs in the sidebar to see real-time updates')}*")


def main():
    """Script entry point - runs the Streamlit app."""
    import subprocess
    import sys
    import os
    
    print("🚀 Starting Salary Comparison Tool...")
    print("📱 Opening in your default browser...")
    print("🌍 Available languages: English, Русский, עברית, العربية")
    print("💡 Tip: Use Ctrl+C to stop the app")
    print("-" * 50)
    
    try:
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(current_dir, "main.py")
        
        # Run the streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            app_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install dependencies:")
        print("   poetry install")
        sys.exit(1)


if __name__ == "__main__":
    streamlit_app()
