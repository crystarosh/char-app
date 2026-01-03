
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Fix "Human Relations" Sidebar Button ---
# User said "Left column Human Relation is not maroon".
# I suspect there IS a button I missed or it's being rendered conditionally.
# I will search for it.
# If I find `st.sidebar.button(..."人間関係"...)`, I will add `type="primary"`.

p_rel_btn = re.compile(r'st\.sidebar\.button\(\s*f?"[^"]*人間関係[^"]*"\s*,')
if p_rel_btn.search(content):
    print("Found Human Relations button in sidebar. Adding type='primary'.")
    content = p_rel_btn.sub(r'st.sidebar.button("🤝 人間関係", type="primary",', content)
    # The regex replacement above is a bit risky if arguments differ.
    # Let's use simple string replacement if possible, or robust regex.
    # I'll try a common pattern.
    content = content.replace(
        'st.sidebar.button("🤝 人間関係", use_container_width=True)',
        'st.sidebar.button("🤝 人間関係", use_container_width=True, type="primary")'
    )
else:
    print("Did not find explicit 'Human Relations' button string. Searching looser match.")
    # Check if maybe it's "Relation Graph"?
    # If not found, I can't fix it blindly.
    pass

# --- Task 2: Fix Delete vs Update Colors ---
# User: "Delete is Red, Modify is Gray". Focus on making Delete Black (Secondary) and Modify Red (Primary).
# "Modify" likely refers to "Save/Update" button in Register page.
# "Delete" likely refers to "Delete" button in Relation page (or List page).

# 2a. Ensure Register/Update button is Primary
# Logic: `if st.button("新規登録" ...)` or `st.button("更新保存" ...)`
content = re.sub(
    r'st\.button\("新規登録", key="reg_btn", use_container_width=True\)',
    'st.button("新規登録", key="reg_btn", use_container_width=True, type="primary")',
    content
)
content = re.sub(
    r'st\.button\("更新保存", key="reg_btn", use_container_width=True\)',
    'st.button("更新保存", key="reg_btn", use_container_width=True, type="primary")',
    content
)
# Note: If they already have type="primary", this replace might duplicate it or fail if exact match doesn't hit.
# But generally `st.button` without type defaults to secondary.

# 2b. Ensure Delete Button is Secondary (to be styled Black)
# In Render Relation Page: `st.button("削除", key=f"del_rel_{i}")`
# Just ensure it DOES NOT have type="primary"
# I can leave it alone, as default is secondary.

# --- Task 3: CSS Overrides ---

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
    
    /* Profile Blue Text & SNS Bio Matching */
    /* Target "SNS用短文" block or generic blue spans */
    .stMarkdown a {
        color: #4682b4 !important; /* SteelBlue */
        text-decoration: none;
    }
    .stMarkdown strong {
        color: #c5a059 !important; /* Gold */
    }
    /* Specific override for profile "blue" parts if they are simple text */
    span[style*="color:blue"], span[style*="color: blue"] {
        color: #4682b4 !important; 
    }
    /* Override for specific info blocks if user mentioned "SNS short text block" */
    /* Assuming it's in a markdown block with specific styling */
    
    /* Headings (Gold) */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Garamond', 'Times New Roman', serif !important;
        color: #c5a059 !important;
        text-shadow: 1px 1px 2px #000;
    }
    
    /* --- BUTTONS --- */
    /* Secondary Buttons (Delete, etc) -> BLACK/DARK GRAY */
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
    /* Only apply to buttons explicitly marked key="primary" or class-based if available */
    .stButton button[kind="primary"] {
        background-color: #800000 !important;
        border: 1px solid #a52a2a !important;
        color: white !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #a00000 !important;
        box-shadow: 0 0 8px #800000aa;
    }

    /* --- SLIDER (Status Bar) --- */
    /* Dark Blue for floating slider */
    div[data-baseweb="slider"] div {
        background-color: #00008b !important; /* DarkBlue track/thumb */
    }
    div[role="slider"] {
        background-color: #4169e1 !important; /* RoyalBlue thumb */
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
    div[data-testid="stExpander"] > div[role="group"] {
        background-color: #1a1a1a !important;
    }
    div[data-testid="stExpander"] p {
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
    
    /* Alerts */
    .stAlert {
        color: #e0e0e0 !important;
        background-color: #333 !important;
        border: 1px solid #555;
    }
    </style>
'''

# Use regex to find st.markdown containing <style> and replace it
# Escaping parentheses for re.compile
p_css = re.compile(r'st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)', re.DOTALL)

if p_css.search(content):
    content = p_css.sub(f'st.markdown("""{new_css}""", unsafe_allow_html=True)', content)
    print("Replaced CSS block with Final Adjusted Version.")
else:
    print("CSS block not found for replacement.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
