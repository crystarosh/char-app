
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Remove ALL <style> blocks (Purge) ---
# We will then re-inject ONE master block at the end (or top of main).
# This ensures no duplicates.
# BUT, we must preserve content OUTSIDE the style tags.
# Logic: Find `st.markdown("""<style>...</style>""", unsafe_allow_html=True)`
# And replace with NOTHING.

# Regex must be robust.
# Pattern: st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)
# Flags: DOTALL
content = re.sub(
    r'st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)',
    '',
    content,
    flags=re.DOTALL
)
print("Purged ALL CSS blocks.")

# --- Task 2: Inject MASTER CSS in main() ---
# Find a good anchor. `st.set_page_config` is best.
# If `st.set_page_config` exists, append CSS after it.
new_css = r'''
    st.markdown("""
    <style>
    /* MASTER CSS - GOTHIC DARK MODE (ULTRA FINAL) */
    
    /* Global App Background */
    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Times New Roman', serif;
    }
    
    /* Header (Top Bar) - Hide/Blend */
    header[data-testid="stHeader"] {
        background-color: #1a1a1a !important;
    }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333;
    }
    
    /* Inputs: Dark Background, White Text */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #2c2c2c !important;
        color: #f0f0f0 !important; /* Bright Gray/White Input Text */
        border: 1px solid #555 !important;
        border-radius: 4px;
        font-family: 'Times New Roman', serif;
    }
    /* Selectbox Dropdown Menu */
    ul[data-baseweb="menu"] {
        background-color: #2c2c2c !important;
        color: #f0f0f0 !important;
    }
    
    /* Input Labels & General Text */
    label, .stMarkdown p, .stMarkdown span, .stMarkdown div, .stCaption {
        color: #a9a9a9 !important;
        font-family: 'Times New Roman', serif;
    }
    
    /* ERROR / INFO / SUCCESS Messages Overrides */
    /* Ensure st.info (used for Bio/Memo) text is readable (Bright Gray, NOT Blue) */
    .stInfo, .stSuccess, .stWarning, .stError {
        background-color: #2c2c2c !important;
        color: #e0e0e0 !important; /* Force Text to Bright Gray */
        border: 1px solid #555;
    }
    .stInfo p, .stSuccess p, .stWarning p, .stError p {
        color: #e0e0e0 !important;
    }
    
    /* Profile Blue Text & SNS Bio Matching */
    /* User said "Internal font... changed back to Blue. Make it Bright Gray". */
    /* Assuming they mean st.info text or input text. Covered above. */
    /* If they mean specifically the "Profile Text" link-like things: */
    /* "Profile text... still blue" (Previous). "SNS short text... Bright Gray" (Current). */
    /* I will make general text Gray. And specific 'blue' spans Gray too if requested. */
    /* But earlier they wanted "Profile text" (Name?) to be SteelBlue? */
    /* Let's keep Links SteelBlue, but Bio Text Bright Gray. */
    .stMarkdown a {
        color: #4682b4 !important; /* SteelBlue Links */
        text-decoration: none;
    }
    .stMarkdown strong {
        color: #c5a059 !important; /* Gold Bold */
    }
    
    /* Headings (Gold) */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Garamond', 'Times New Roman', serif !important;
        color: #c5a059 !important;
        text-shadow: 1px 1px 2px #000;
    }
    
    /* --- BUTTONS --- */
    /* Secondary Buttons (Delete, etc) -> BLACK/DARK GRAY */
    /* We explicitly target buttons that are NOT primary */
    .stButton button:not([kind="primary"]) {
        background-color: #1a1a1a !important; /* Dark Gray/Black */
        color: #aaaaaa !important;
        border: 1px solid #333 !important;
        font-family: 'Times New Roman', serif;
        border-radius: 4px;
    }
    .stButton button:not([kind="primary"]):hover {
        background-color: #000000 !important; /* Pitch Black on hover */
        border-color: #555 !important;
        color: #ffffff !important;
    }
    
    /* Primary Button (Register, Sidebar Nav) -> MAROON */
    /* Use specific selector + !important */
    .stButton button[kind="primary"] {
        background-color: #800000 !important;
        border: 1px solid #a52a2a !important;
        color: white !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #a00000 !important;
        box-shadow: 0 0 8px #800000aa;
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab"] {
        color: #d3d3d3 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #4682b4 !important;
        border-bottom-color: #4682b4 !important;
    }
    
    /* --- EXPANDER --- */
    /* Force Background on Details Summary and Content */
    /* KEY FIX: Target the summary directly for open state */
    .streamlit-expanderHeader {
        background-color: #222 !important;
        color: #c5a059 !important;
        border-radius: 4px;
    }
    details[open] .streamlit-expanderHeader {
        background-color: #222 !important; 
    }
    /* Hover state? */
    .streamlit-expanderHeader:hover {
        background-color: #333 !important;
    }
    
    div[data-testid="stExpander"] {
        background-color: #1a1a1a !important;
        border: 1px solid #444 !important;
        color: #e0e0e0 !important;
    }
    div[data-testid="stExpander"] > div[role="group"] {
        background-color: #1a1a1a !important;
    }
    /* Ensure no white background from inherited styles */
    .streamlit-expanderContent {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    /* --- TABLE / DATAFRAME --- */
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
    </style>
    """, unsafe_allow_html=True)
'''

if 'st.set_page_config' in content:
    # Insert after set_page_config line
    # Find the end of the line containing st.set_page_config
    match = re.search(r'st\.set_page_config\(.*?\)', content, re.DOTALL)
    if match:
        end_pos = match.end()
        # Insert newline and css
        content = content[:end_pos] + "\n" + new_css + content[end_pos:]
        print("Injected Master CSS after set_page_config.")
    else:
        # Fallback if regex misses (maybe strict formatting)
        content = content.replace("layout='wide')", "layout='wide')\n" + new_css)
else:
    # Insert at top of main
    content = content.replace("def main():", "def main():\n" + new_css)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
