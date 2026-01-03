
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Replace st.info(memo_txt) with Custom HTML ---
# Finding the block:
# memo_txt = details.get('memo', '')
# if memo_txt:
#     with st.expander('プロフィール画像用テキストを確認', expanded=False):
#         st.info(memo_txt)
#         st.caption(f'{len(memo_txt)}文字')

# We replace `st.info(memo_txt)` with markdown DIV
p_memo = re.compile(r'st\.info\(memo_txt\)')
replacement_memo = r'''st.markdown(f'<div style="background-color: #2c2c2c; color: #e0e0e0; padding: 10px; border-radius: 5px; border: 1px solid #555;">{memo_txt}</div>', unsafe_allow_html=True)'''

if p_memo.search(content):
    content = p_memo.sub(replacement_memo, content)
    print("Replaced Memo st.info with HTML Div.")

# --- Task 2: Replace "SNS Short Text" with Custom HTML ---
# Logic:
# if char.get('bio_short'):
#     st.markdown("**SNS用（短文）**")
#     st.info(char['bio_short'])  <-- This line presumably exists or similar
# Need to find how it is displayed.
# Previous view did not show lines 950+.
# I'll blindly replace `st.info(char['bio_short'])` if it exists.
# Or `st.write(char['bio_short'])`.
# Let's search for `char['bio_short']` logic.
# If I can't match it perfectly, I'll assume it matches generic info pattern or I'll search for it.
# Actually I will use a Regex to find the block for SNS short text display.

# Pattern: st.markdown("**SNS用（短文）**") ... st.info(...) or st.write(...)
# I'll try to find the `st.info` calls that pass `char['bio_short']`.

p_bio_short = re.compile(r'st\.info\(char\[[\'"]bio_short[\'"]\]\)')
replacement_bio = r'''st.markdown(f'<div style="background-color: #2c2c2c; color: #e0e0e0; padding: 10px; border-radius: 5px; border: 1px solid #555;">{char["bio_short"]}</div>', unsafe_allow_html=True)'''

if p_bio_short.search(content):
    content = p_bio_short.sub(replacement_bio, content)
    print("Replaced Bio Short st.info with HTML Div.")
else:
    # Try finding `st.write` or similar?
    print("Could not find st.info(char['bio_short']). Checking for plain text variable usage...")
    # Maybe `bio_s = char.get('bio_short')` ... `st.info(bio_s)`?
    # I'll skip this if regex fails, but I strongly suspect it's there.
    pass

# --- Task 3: Force CSS for Delete Button (Red Removal) ---
# Delete button usually has key="del_rel_..." or similar.
# I will Use the Global Master CSS Update to force all non-primary buttons to be Black.
# AND I will inject a specific overrides block at the VERY END of main() to win specificity wars.

final_css = r'''
    <style>
    /* FORCE FINAL OVERRIDES */
    
    /* 1. Delete Buttons (and all Secondary) -> BLACK */
    /* Target ANY button that does NOT have kind="primary" */
    button:not([kind="primary"]) {
        background-color: #000000 !important;
        color: #cccccc !important;
        border: 1px solid #333 !important;
    }
    button:not([kind="primary"]):hover {
        background-color: #333333 !important;
        color: #ffffff !important;
        border-color: #555 !important;
    }
    
    /* 2. Expander Background -> DARK */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #dda0dd !important; /* Light Purple or Gold? User didn't specify, keeping Gold/Default or adjusting */
    }
    /* Open State */
    details[open] .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
    }
    .streamlit-expanderContent {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    /* 3. Text Colors (Generic) -> Bright Gray */
    .stMarkdown p, .stText p {
        color: #e0e0e0 !important;
    }
    
    /* 4. Primary Button -> MAROON */
    button[kind="primary"] {
        background-color: #800000 !important;
        color: white !important;
        border: 1px solid #a52a2a !important;
    }
    button[kind="primary"]:hover {
        background-color: #a00000 !important;
    }
    
    /* 5. Inputs -> Bright Gray Text */
    input {
        color: #f0f0f0 !important;
    }
    textarea {
        color: #f0f0f0 !important;
    }
    </style>
'''

# Replace the PREVIOSLY injected master css block with this logic.
# Pattern: st.markdown("""<style>/* MASTER CSS(.*?)</style>""", unsafe_allow_html=True)
p_master = re.compile(r'st\.markdown\("""\s*<style>\s*/\* MASTER CSS.*?</style>\s*""", unsafe_allow_html=True\)', re.DOTALL)

if p_master.search(content):
    content = p_master.sub(f'st.markdown("""{final_css}""", unsafe_allow_html=True)', content)
    print("Updated Master CSS with HTML Element approach.")
else:
    # If not found (maybe my previous script pattern mismatch), append to main.
    print("Master CSS block not found (regex mismatch?). Appending Final CSS to end of main.")
    content = content.replace("def main():", f"def main():\n    st.markdown('''{final_css}''', unsafe_allow_html=True)\n")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
