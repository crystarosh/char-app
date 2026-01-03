
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the CSS for Gothic/Victorian Dark Mode
# Colors:
# Bg: #1E1E24 (Dark Gunmetal)
# Sidebar: #121212 (Almost Black)
# Text: #E0E0E0 (Light Gray/Ivory)
# Primary Accent: #800020 (Burgundy) or #8B0000 (Dark Red)
# Secondary Accent: #C5A059 (Antique Gold)
# Inputs: #2D2D33 (Dark gray input bg), Silver border

css_style = r'''
<style>
    /* Global Background and Text */
    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Georgia', 'Times New Roman', serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #333;
    }
    
    /* Input Fields (Text Input, Number Input, Selectbox, Text Area) */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #2c2c2c !important;
        color: #f0f0f0 !important;
        border: 1px solid #555 !important;
        border-radius: 4px;
        font-family: 'Georgia', serif;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #c5a059 !important; /* Gold focus */
        box-shadow: 0 0 5px #c5a05955 !important;
    }

    /* Selectbox Options Menu */
    ul[data-baseweb="menu"] {
        background-color: #2c2c2c !important;
        color: #f0f0f0 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Garamond', 'Georgia', serif !important;
        color: #c5a059 !important; /* Antique Gold Headers */
        text-shadow: 1px 1px 2px #000;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #3e2723 !important; /* Dark Brown/Red base */
        color: #ffecb3 !important; /* Light Gold text */
        border: 1px solid #c5a059 !important;
        font-family: 'Georgia', serif;
        border-radius: 4px;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #5d4037 !important;
        border-color: #ffe082 !important;
        color: #ffffff !important;
        box-shadow: 0 0 8px #c5a05988;
    }
    
    /* Primary Button (Register) */
    .stButton button[kind="primary"] {
        background-color: #800020 !important; /* Burgundy */
        border: 1px solid #a52a2a !important;
        color: white !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #a00030 !important;
        box-shadow: 0 0 10px #800020aa;
    }
    
    /* Labels */
    label, .stMarkdown p {
        color: #cccccc !important;
        font-family: 'Georgia', serif;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #222 !important;
        color: #c5a059 !important;
        border: 1px solid #444;
    }
    
    /* Dataframe/Table */
    .stDataFrame {
        border: 1px solid #444;
    }
    
    /* Success/Info/Warning messages */
    .stAlert {
        background-color: #2c2c2c !important;
        color: #e0e0e0 !important;
        border: 1px solid #555;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #888;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #c5a059 !important;
        border-bottom-color: #c5a059 !important;
    }

</style>
'''

# Injection into `def main():`
# Find `st.set_page_config` call or `def main():` start.
# `st.set_page_config` is usually at the top top level.
# I will check if `st.set_page_config` exists in global scope or main.
# Usually it's global.
# But `char_app.py` has `def main()` at end.
# I'll inject `st.markdown(css, unsafe_allow_html=True)` immediately after `def main():` line.

if '<style>' not in content:
    # Prepare the injection block
    injection = f'    st.markdown("""{css_style}""", unsafe_allow_html=True)\n'
    
    # Locate main
    p_main = re.compile(r'def main\(\):')
    m_main = p_main.search(content)
    if m_main:
        # Check indentation. Python def is 0 indent?
        # main usually starts with:
        # def main():
        #     st.set_page_config(...) # Maybe?
        
        # If I replace `def main():` with `def main():\n    st.markdown(...)`
        # I need to be careful about what follows `def main():`.
        # Usually it's indented code.
        
        # Let's verify `main` content via view_file if needed?
        # Actually I can just replace `st.title("🛡️ キャラクター図鑑")` since I know where that is (modified earlier).
        # Earlier I replaced it with title + session key init.
        # I can append style injection there.
        
        target_str = 'st.title("🛡️ キャラクター図鑑")'
        replacement = f'st.markdown("""{css_style}""", unsafe_allow_html=True)\n    {target_str}'
        
        content = content.replace(target_str, replacement)
        print("Injected Gothic Dark Mode CSS before title.")
    else:
        print("Could not find 'def main():' or title to inject CSS.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
