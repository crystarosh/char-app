
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Dedent Image Section
# Currently inside `for i, label ...` loop (8 spaces).
# Need to dedent to 4 spaces.
# The block starts with `        st.markdown("### 🖼️ 画像")` (8 spaces)
# And ends before `    st.markdown("### 🤝 人間関係")` (4 spaces, fixed previously).

# I will find the block and replace it with dedented version.
# Note: Python `re` needs careful handling of whitespace.

# Pattern: Capture 8-space indented "Image" block.
# It seems my previous `restore_delete_checkbox.py` inserted it.
# The previous view showed line 240: `        st.markdown("### 🖼️ 画像")`

p_image_block = re.compile(
    r'(^[ \t]{8}st\.markdown\("### 🖼️ 画像"\).*?)(?=^[ \t]{4}st\.markdown\("### 🤝 人間関係"\))', 
    re.DOTALL | re.MULTILINE
)

m_img = p_image_block.search(content)

if m_img:
    block = m_img.group(1)
    # Dedent by 4 spaces
    # Lines starting with 8 spaces -> 4 spaces
    # Lines starting with 12 spaces -> 8 spaces, etc.
    # Be careful not to strip everything.
    dedented_block = re.sub(r'^    ', '', block, flags=re.MULTILINE)
    
    # Wait, simple `replace('    ', '', 1)` on each line?
    # Only if it starts with 4 spaces?
    dedented_block = "\n".join([line[4:] if line.startswith("    ") else line for line in block.splitlines()])
    
    # Ensure newline at end if stripped
    if block.endswith("\n") and not dedented_block.endswith("\n"):
        dedented_block += "\n"
        
    content = content[:m_img.start()] + dedented_block + content[m_img.end():]
    print("Fixed: Dedented Image Section (Stopped 8x repetition).")
else:
    # Try searching for the block without the end lookahead being too strict,
    # or check if it's already fixed (unlikely if user complains).
    # Maybe manual scan?
    # Let's try to match just the start.
    if '        st.markdown("### 🖼️ 画像")' in content:
        # Fallback: Replace known header indentation
        content = content.replace('        st.markdown("### 🖼️ 画像")', '    st.markdown("### 🖼️ 画像")')
        content = content.replace('    current_images = existing_data', '    current_images = existing_data') # Checking alignment
        # This is risky. Better to match block.
        print("Warning: Regex failed, attempting text replacement for header only? No, unsafe.")
    else:
        print("Block 1 not found or already dedented.")

# Fix 2: Sidebar "New Registration" Button - Clear State
# Pattern: `if st.sidebar.button("➕ 新規登録", use_container_width=True):`
# Replace the body.

sidebar_btn_code = r'''    if st.sidebar.button("➕ 新規登録", use_container_width=True):
        st.session_state.view_mode = 'register'
        st.session_state.editing_char_id = None
        # Clear input state
        for k in list(st.session_state.keys()):
            if (k.startswith('reg_') or k.startswith('stat_') or k.startswith('p_stat_') 
                or k.startswith('input_') or k.startswith('picker_') or k == 'bio_input_area'
                or k.startswith('u') or k.startswith('del_img_')): # Clear uploaders and deletes too
                try:
                     del st.session_state[k]
                except:
                     pass
        st.rerun()'''

p_sidebar = re.compile(
    r'if st\.sidebar\.button\("➕ 新規登録", use_container_width=True\):.*?st\.rerun\(\)', 
    re.DOTALL
)

m_sidebar = p_sidebar.search(content)
if m_sidebar:
    content = content[:m_sidebar.start()] + sidebar_btn_code + content[m_sidebar.end():]
    print("Fixed: Sidebar New Registration now clears state.")
else:
    print("Sidebar button block not found.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
