
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Update Button Types ---

# 1a. Navigation Buttons in Sidebar ("📂 キャラクター一覧", "➕ 新規登録")
# Change default (secondary) to "primary" so they become Maroon?
# OR leave them secondary and accepted they are dark?
# User said "Left column buttons became black (lol)".
# If I make secondary buttons Black (for Delete), sidebar nav becomes Black.
# If I change nav buttons to Primary, they become Maroon.
# Let's try changing Nav Buttons to Primary.
content = content.replace(
    'st.sidebar.button("📂 キャラクター一覧", use_container_width=True)',
    'st.sidebar.button("📂 キャラクター一覧", use_container_width=True, type="primary")'
)
content = content.replace(
    'st.sidebar.button("➕ 新規登録", use_container_width=True)',
    'st.sidebar.button("➕ 新規登録", use_container_width=True, type="primary")'
)

# 1b. Delete Buttons in Relations
# Ensure they are secondary (default).
# Look for `st.button("削除", key=...)`.
# If they have `type="primary"`, remove it.
# Code view (305-350ish) showed `st.button("削除", key=f"del_rel_{i}")`.
# This defaults to secondary. So they are ALREADY secondary.
# So if I style secondary buttons as Black, Delete buttons become Black.
# AND Sidebar buttons became Black (before I changed them to Primary just now).
# This aligns with the plan.

# Note: Image Deletes are checkboxes. They are handled separately.

print("Updated Sidebar Buttons to Primary (Maroon). Delete remains Secondary (Black).")


# --- Task 2: Advanced CSS Injection ---

# We need to replace the CSS block again with refined selectors.
# Table Fix strategy: Overwrite glide-data-grid colors if possible, or force table cells.

new_css = r'''
    <style>
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
        color: #f0f0f0 !important;
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
    label, .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: #a9a9a9 !important;
        font-family: 'Times New Roman', serif;
    }
    
    /* Profile Blue Text (Brighter Blue) */
    /* Targeting links and specific spans used for displaying values */
    .stMarkdown a {
        color: #4682b4 !important; /* SteelBlue */
        text-decoration: none;
    }
    .stMarkdown strong {
        color: #c5a059 !important; /* Gold for strong text? or Blue? */
    }
    /* Override blue spans from rendering code if any */
    span[style*="color:blue"], span[style*="color: blue"] {
        color: #4682b4 !important; 
    }

    /* Headings (Gold) */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Garamond', 'Times New Roman', serif !important;
        color: #c5a059 !important;
        text-shadow: 1px 1px 2px #000;
    }
    
    /* --- BUTTONS --- */
    /* Secondary Buttons (Delete, etc) -> BLACK/DARK GRAY */
    /* Also affects sidebar if not primary */
    .stButton button {
        background-color: #1a1a1a !important; /* Dark Gray/Black */
        color: #aaaaaa !important;
        border: 1px solid #333 !important;
        font-family: 'Times New Roman', serif;
        border-radius: 4px;
    }
    .stButton button:hover {
        background-color: #000000 !important; /* Pitch Black on hover */
        border-color: #555 !important;
        color: #ffffff !important;
    }
    
    /* Primary Button (Register, Sidebar Nav) -> MAROON */
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
    /* Fix white background when opened */
    .streamlit-expanderHeader {
        background-color: #222 !important;
        color: #c5a059 !important;
        border-radius: 4px;
    }
    div[data-testid="stExpander"] {
        background-color: #1a1a1a !important;
        border: 1px solid #444 !important;
        color: #e0e0e0 !important;
    }
    /* Content within expander */
    div[data-testid="stExpander"] > div[role="group"] {
        background-color: #1a1a1a !important;
    }
    div[data-testid="stExpander"] p {
        color: #e0e0e0 !important; /* Ensure text inside is visible */
    }
    
    /* --- TABLE / DATAFRAME --- */
    /* Target common dataframe classes */
    div[data-testid="stDataFrame"] {
        background-color: #2c2c2c !important;
        border: 1px solid #696969;
    }
    
    /* Cells */
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        background-color: #2c2c2c !important;
        color: #e0e0e0 !important;
    }
    /* Headers - Fix Mint Color */
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background-color: #444444 !important;
        color: #ffffff !important;
    }
    
    /* Legacy Table (if used) */
    .stTable td, .stTable th {
        background-color: #2c2c2c !important;
        color: #e0e0e0 !important;
        border-bottom: 1px solid #444 !important;
    }
    
    /* Alerts */
    .stAlert {
        color: #e0e0e0 !important;
        background-color: #333 !important;
        border: 1px solid #555;
    }
    </style>
'''

# Use regex to replace the existing <style> block
# The block starts with <style> and ends with </style> inside st.markdown call.
# It's safer to target the `st.markdown("""...<style>` part.
# I will find the block using regex.
# Corrected Regex: Escaped closing parenthesis in st.markdown call
p_css = re.compile(r'st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)', re.DOTALL)

if p_css.search(content):
    content = p_css.sub(f'st.markdown("""{new_css}""", unsafe_allow_html=True)', content)
    print("Replaced CSS block with Advanced Version.")
else:
    print("CSS block not found for replacement.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
