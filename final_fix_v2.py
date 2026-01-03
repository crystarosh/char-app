
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Remove DUPLICATE CSS block in render_detail_page ---
# The duplicate block starts with `st.markdown("""` followed by `<style>` and `.stApp`.
# It ends with `""", unsafe_allow_html=True)`
# It is located inside `render_detail_page`, likely indented.
# I will use a regex that matches the block specfically if it appears AFTER the first instance.

# Find all matches
matches = list(re.finditer(r'st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)', content, re.DOTALL))

if len(matches) > 1:
    print(f"Found {len(matches)} CSS blocks. Removing all but the first (Global).")
    # Identify the Global block (usually the last one added? Or first in main?)
    # `main` is at the end of file usually. `render_detail` is in middle.
    # The Global one I added is in `main()`, which is near the bottom.
    # The DUPLICATE one is in `render_detail_page`, which is in the middle.
    # So the SECOND one in file order is the Global one (if main is at bottom).
    # Wait, `render_detail_page` comes BEFORE `main`.
    # So the FIRST match is the DUPLICATE (bad one).
    # The SECOND match is the GLOBAL (good one).
    
    # Let's verify positions.
    # `render_detail_page` is defined early. `main` calls it.
    # So Match 1 = Duplicate. Match 2 = Global.
    
    # We want to REMOVE Match 1.
    
    bad_match = matches[0]
    # Replace with empty string or comment
    # Careful with slicing
    start, end = bad_match.span()
    content = content[:start] + '# [Duplicate CSS Removed]' + content[end:]
    
else:
    print("Found only 1 or 0 CSS blocks. Assuming single global block is present.")

# --- Task 2: Fix "SNS Short Text" Blue Color ---
# User says "SNS用短文" is blue.
# I suspect it's rendered using `st.markdown` with some default styling or `st.info`.
# Or it's a link?
# Searching for "SNS" didn't yield result?
# Let's try searching for the string "SNS" again in the logic.
# If I can't find it, the user might be referring to "Memo" or "Bio" which I can target via CSS.
# Global CSS already forces `.stMarkdown a` to SteelBlue.

# --- Task 3: Fix Update Button Type (Again) ---
# Ensure "登録 / 更新" uses type="primary"
content = content.replace(
    'st.button("登録 / 更新", type="primary")', 
    'st.button("登録 / 更新", type="primary")' 
)
# If it was secondary (no type), replace it.
content = content.replace(
    'st.button("登録 / 更新")', 
    'st.button("登録 / 更新", type="primary")'
)

# --- Task 4: Ensure Global CSS has Final Fixes ---
# The logic above removed the *first* block.
# Now I need to ensure the *remaining* block (Global) has the fix for Expander and Blue Text.
# I will just replacing the *remaining* CSS block with the Master CSS.

new_css = r'''
    <style>
    /* MASTER CSS - GOTHIC DARK MODE */
    
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
    label, .stMarkdown p, .stMarkdown span, .stMarkdown div, .stCaption {
        color: #a9a9a9 !important;
        font-family: 'Times New Roman', serif;
    }
    
    /* Profile Blue Text & SNS Bio Matching */
    .stMarkdown a {
        color: #4682b4 !important; /* SteelBlue */
        text-decoration: none;
    }
    .stMarkdown strong {
        color: #c5a059 !important; /* Gold */
    }
    /* Specific override for profile "blue" parts if they are simple text */
    span[style*="color:blue"], span[style*="color: blue"], span[style*="color:Blue"] {
        color: #4682b4 !important; 
    }
    /* Override standard info/success messages to be dark? */
    .stAlert {
        color: #e0e0e0 !important;
        background-color: #333 !important;
        border: 1px solid #555;
    }

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
    .streamlit-expanderHeader {
        background-color: #222 !important;
        color: #c5a059 !important;
        border-radius: 4px;
    }
    /* When open (Streamlit uses details[open]) */
    details[open] .streamlit-expanderHeader {
        background-color: #222 !important; 
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
'''

p_css = re.compile(r'st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)', re.DOTALL)
if p_css.search(content):
    content = p_css.sub(f'st.markdown("""{new_css}""", unsafe_allow_html=True)', content)
    print("Updated Global CSS with Final Fixes.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
