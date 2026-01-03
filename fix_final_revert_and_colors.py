
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Revert Slider CSS ---
# User said "Status params very hard to read... revert to previous".
content = re.sub(
    r'/\* --- SLIDER \(Status Bar\) --- \*/.*?div\[role="slider"\] \{[^}]+\}\s*}',
    '',
    content,
    flags=re.DOTALL
)
# Also just remove any Slider block if regex fails
if "/* --- SLIDER" in content:
    # Manual removal if simple regex misses
    start = content.find("/* --- SLIDER")
    end = content.find("/* --- TABS ---", start)
    if start != -1 and end != -1:
        content = content[:start] + content[end:]
        print("Removed Slider CSS block.")

# --- Task 2: Fix Modify/Register Button Types ---
# Ensure "更新保存" is type="primary"
# My previous regex might have missed or it was already primary.
# I will check lines around 400-500.
# I'll just Replace the exact strings again to be super sure.

# Update Button
content = content.replace(
    'st.button("更新保存", key="reg_btn", use_container_width=True)',
    'st.button("更新保存", key="reg_btn", use_container_width=True, type="primary")'
)
# Reg Button (New)
content = content.replace(
    'st.button("新規登録", key="reg_btn", use_container_width=True)',
    'st.button("新規登録", key="reg_btn", use_container_width=True, type="primary")'
)

# --- Task 3: Fix Update CSS ---
# User: "Blue text still blue", "Expander white on open".

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
    label, .stMarkdown p, .stMarkdown span, .stMarkdown div, .stCaption {
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
    span[style*="color:blue"], span[style*="color: blue"], span[style*="color:Blue"] {
        color: #4682b4 !important; 
    }
    /* Force captions to be SteelBlue if they were blue? No, usually gray. */
    /* But user said "Profile text... still blue". */
    /* Maybe it's `st.info` or `st.markdown(":blue[...]"). */
    span[data-baseweb="tag"] {
        background-color: #4682b4 !important;
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
    
    /* Alerts */
    .stAlert {
        color: #e0e0e0 !important;
        background-color: #333 !important;
        border: 1px solid #555;
    }
    </style>
'''

p_css = re.compile(r'st\.markdown\("""\s*<style>.*?</style>\s*""", unsafe_allow_html=True\)', re.DOTALL)

if p_css.search(content):
    content = p_css.sub(f'st.markdown("""{new_css}""", unsafe_allow_html=True)', content)
    print("Replaced CSS block with Final Reverted Version.")
else:
    print("CSS block not found for replacement.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
