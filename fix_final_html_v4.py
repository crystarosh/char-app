
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Fix Delete Button (Make it Black/Secondary) ---
# Currently: st.button("🗑️ 削除", type="primary")
# Replace with: st.button("🗑️ 削除") 
# (Removing type="primary" makes it secondary, which our CSS styles as Black/Dark Gray)

if 'st.button("🗑️ 削除", type="primary")' in content:
    content = content.replace('st.button("🗑️ 削除", type="primary")', 'st.button("🗑️ 削除")')
    print("Fixed Delete Button: Removed type='primary' to allow Black styling.")
else:
    print("Delete button pattern not found (or already fixed).")

# --- Task 2: Fix SNS Short Text (Bio Short) ---
# Current Pattern found: st.info(char['bio_short'], icon="📝")
# Replacement: st.markdown HTML div

p_bio = re.compile(r'st\.info\(char\[[\'"]bio_short[\'"]\], icon=["\']📝["\']\)')
replacement_html = r'''st.markdown(f'<div style="background-color: #2c2c2c; color: #e0e0e0; padding: 10px; border-radius: 5px; border: 1px solid #555;">{char["bio_short"]}</div>', unsafe_allow_html=True)'''

if p_bio.search(content):
    content = p_bio.sub(replacement_html, content)
    print("Replaced SNS Short Text (with icon) with HTML Div.")
else:
    # Try without icon just in case
    p_bio_no_icon = re.compile(r'st\.info\(char\[[\'"]bio_short[\'"]\]\)')
    if p_bio_no_icon.search(content):
        content = p_bio_no_icon.sub(replacement_html, content)
        print("Replaced SNS Short Text (no icon) with HTML Div.")
    else:
        print("SNS Short Text pattern not found.")

# --- Task 3: Ensure Master CSS is robust ---
# I will NOT re-inject the huge block if it's already there, to avoid duplicates.
# But I will verify if `button:not([kind="primary"])` selector exists.
# If not, I'll append it to the existing style block.

if 'button:not([kind="primary"])' not in content:
    print("Warning: highly specific Black Button selector not found. Appending it.")
    # Append to the last st.markdown style block roughly, or just append a new fix block at the end of main.
    # Appending to main is safer.
    
    fix_css = r'''
    st.markdown("""
    <style>
    /* EMERGENCY FIX OVERRIDES */
    button:not([kind="primary"]) {
        background-color: #000000 !important;
        color: #cccccc !important;
        border: 1px solid #333 !important;
    }
    button:not([kind="primary"]):hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    /* Expander Fix just in case */
    div[data-testid="stExpander"] {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    .streamlit-expanderHeader {
        background-color: #222 !important;
        color: #c5a059 !important;
    }
    details[open] .streamlit-expanderHeader {
        background-color: #222 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    '''
    # Insert before last lines of main or file end?
    # char_app.py usually ends with `if __name__ == "__main__": main()`
    # I'll insert it at the very end of `main()` definition indentation.
    # This is risky without parsing.
    # Instead, I'll replace `if __name__ == "__main__":` with the fix + the check.
    
    content = content.replace('if __name__ == "__main__":', f'{fix_css}\n\nif __name__ == "__main__":')
    print("Appended Emergency Fix CSS.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
