
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# COMPLETE GOTHIC DARK MODE CSS
# This includes the basic theme AND the specific fixes for Delete button, Blue text, etc.
master_css = r'''
    st.markdown("""
    <style>
    /* === GOTHIC VICTORIAN DARK MODE (RESCUE MASTER) === */
    
    /* 1. Global Background & Font */
    .stApp {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        font-family: 'Times New Roman', serif;
    }
    
    /* 2. Header & Sidebar */
    header[data-testid="stHeader"] {
        background-color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333;
    }
    
    /* 3. Inputs (Text, Number, Select) -> Dark BG / White Text */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #2c2c2c !important;
        color: #f0f0f0 !important;
        border: 1px solid #555 !important;
        border-radius: 4px;
        font-family: 'Times New Roman', serif;
    }
    ul[data-baseweb="menu"] {
        background-color: #2c2c2c !important;
        color: #f0f0f0 !important;
    }
    
    /* 4. Text Elements & Labels */
    label, .stMarkdown p, .stMarkdown span, .stMarkdown div, .stCaption, .stText p {
        color: #a9a9a9 !important;
        font-family: 'Times New Roman', serif;
    }
    
    /* 5. Headings -> Gold */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Garamond', 'Times New Roman', serif !important;
        color: #c5a059 !important;
        text-shadow: 1px 1px 2px #000;
        border-bottom: 1px solid #444; /* Subtle separator for headers */
        padding-bottom: 5px;
    }
    .stMarkdown strong {
        color: #c5a059 !important;
    }
    
    /* 6. Links -> SteelBlue */
    .stMarkdown a {
        color: #4682b4 !important;
        text-decoration: none;
    }
    
    /* 7. Buttons */
    /* DEFAULT (Secondary/Delete/Cancel) -> BLACK */
    /* Target generic button classes and specific overrides */
    div.stButton > button {
        background-color: #000000 !important;
        color: #cccccc !important;
        border: 1px solid #333 !important;
        border-radius: 4px;
        font-family: 'Times New Roman', serif;
    }
    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
        border-color: #555 !important;
    }
    
    /* PRIMARY (Register, Sidebar) -> MAROON */
    /* Explicitly target kind="primary" */
    div.stButton > button[kind="primary"] {
        background-color: #800000 !important;
        color: white !important;
        border: 1px solid #a52a2a !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #a00000 !important;
        box-shadow: 0 0 8px #800000aa;
    }
    /* Explicit check for buttons that might lose 'kind' attribute mapping in some contexts? 
       No, Streamlit renders data-testid="stButton" -> button -> kind="primary" reliably. */

    /* 8. Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #d3d3d3 !important;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #4682b4 !important;
        border-bottom-color: #4682b4 !important;
    }
    
    /* 9. Expander */
    .streamlit-expanderHeader {
        background-color: #222222 !important;
        color: #c5a059 !important;
        border: 1px solid #444;
        border-radius: 4px;
    }
    details[open] .streamlit-expanderHeader {
        background-color: #222222 !important; 
    }
    div[data-testid="stExpander"] {
        background-color: #1a1a1a !important;
        border: 1px solid #444 !important;
        color: #e0e0e0 !important;
    }
    .streamlit-expanderContent {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    /* 10. Table / DataFrame */
    div[data-testid="stDataFrame"] {
        background-color: #2c2c2c !important;
        border: 1px solid #696969;
    }
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        background-color: #2c2c2c !important;
        color: #e0e0e0 !important;
    }
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background-color: #444444 !important;
        color: #ffffff !important;
    }
    
    /* 11. Alerts / Info Boxes (Background Dark, Text Gray) */
    .stAlert {
        background-color: #2c2c2c !important;
        color: #e0e0e0 !important;
        border: 1px solid #555;
    }
    
    /* 12. Custom HTML Divs (for our manual injection) */
    /* These are inline styles mostly, but good to have fallback */
    
    </style>
    """, unsafe_allow_html=True)
'''

# Strategy:
# 1. Clean existing styles just in case (to avoid double injection).
content = re.sub(
    r'st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)',
    '',
    content,
    flags=re.DOTALL
)

# 2. Inject CSS immediately after `def main():` line.
# This ensures it runs every rerun.
if "def main():" in content:
    # Indent the injected code by 4 spaces
    indented_css = "\n    " + master_css.strip().replace("\n", "\n    ") + "\n"
    content = content.replace("def main():", "def main():" + indented_css)
    print("Injected RESCUE CSS into main().")
else:
    print("ERROR: def main(): not found. Appending to end.")
    content += "\n" + master_css

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
