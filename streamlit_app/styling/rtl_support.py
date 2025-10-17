"""
RTL (Right-to-Left) styling support for Hebrew and Arabic languages.
"""

import streamlit as st


def apply_rtl_support():
    """Apply RTL styling for Hebrew and Arabic languages."""
    if st.session_state.selected_language in ['he', 'ar']:
        st.markdown("""
        <style>
        /* RTL support for Hebrew and Arabic - removed main container RTL to preserve layout */
        
        /* RTL layout: Move sidebar to right side for RTL languages */
        .stApp {
            direction: rtl;
        }
        
        .stApp .main {
            direction: ltr;
        }
        
        /* Force sidebar to right side */
        .stSidebar {
            position: fixed !important;
            right: 0 !important;
            left: auto !important;
        }
        
        /* Adjust main content for RTL sidebar */
        .main {
            margin-right: 21rem !important;
            margin-left: 0 !important;
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
        
        /* RTL for form labels and input labels */
        .stSelectbox label,
        .stNumberInput label,
        .stTextInput label,
        .stTextArea label,
        .stDateInput label,
        .stTimeInput label,
        .stFileUploader label {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for form label text specifically */
        .stSelectbox label p,
        .stNumberInput label p,
        .stTextInput label p,
        .stTextArea label p,
        .stDateInput label p,
        .stTimeInput label p,
        .stFileUploader label p {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* RTL for form label spans */
        .stSelectbox label span,
        .stNumberInput label span,
        .stTextInput label span,
        .stTextArea label span,
        .stDateInput label span,
        .stTimeInput label span,
        .stFileUploader label span {
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
            width: 100%;
        }
        
        /* RTL for tabs */
        .stTabs > div > div > div {
            direction: rtl;
        }
        
        /* RTL for columns */
        .stColumns > div {
            direction: rtl;
        }
        
        /* Fix RTL sidebar country name alignment */
        .stSidebar .country-name {
            text-align: right !important;
            direction: rtl !important;
            width: 100% !important;
            margin: 4px 0 !important;
            padding: 8px 12px !important;
            box-sizing: border-box !important;
        }
        
        /* Fix RTL checkbox spacing */
        .stSidebar .stCheckbox > label {
            direction: rtl !important;
            text-align: right !important;
        }
        
        .stSidebar .stCheckbox > label > div {
            direction: rtl !important;
            text-align: right !important;
            margin-right: 8px !important;
        }
        
        .stSidebar .stCheckbox > label > div > p {
            direction: rtl !important;
            text-align: right !important;
            margin-right: 8px !important;
        }
        </style>
        """, unsafe_allow_html=True)
