
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Update UI (Labels & Add Image 6) ---

# We need to find the Image Section blocks.
# I'll use regex to locate the columns block and inject Image 6.

# Search for `with img_col2:` block.
# It contains Img 2 and Img 4.
# We want to add Img 6.

p_col2 = re.compile(
    r'(with img_col2:.*?u4 = st\.file_uploader\("上書き/新規 \(No\.4\)", type=\["png", "jpg"\], key=f"u4_\{sid\}"\))', 
    re.DOTALL
)

m_col2 = p_col2.search(content)
if m_col2:
    # Add Image 6 code
    addition = r'''
        
        st.markdown("**画像6 (Gallery D)**")
        if get_cur(5): 
            st.image(get_cur(5), width=100)
            d6 = st.checkbox("画像6を削除", key=f"del_img_6_{sid}")
        u6 = st.file_uploader("上書き/新規 (No.6)", type=["png", "jpg"], key=f"u6_{sid}")'''
    
    # Also update Image 2 label to include "(必須)"
    block = m_col2.group(1)
    block = block.replace('st.markdown("**画像2 (Full Body)**")', 'st.markdown("**画像2 (Full Body)** <span style="color:red; font-size:0.8em">(必須)</span>", unsafe_allow_html=True)')
    
    new_block = block + addition
    content = content.replace(m_col2.group(1), new_block)
    print("Added Image 6 UI and Img 2 Warning.")
else:
    print("Image Col 2 block not found via regex.")

# Update Image 1 label in img_col1
content = content.replace(
    'st.markdown("**画像1 (Profile)**")', 
    'st.markdown("**画像1 (Profile)** <span style="color:red; font-size:0.8em">(必須)</span>", unsafe_allow_html=True)'
)
print("Added Img 1 Warning.")

# Initialize u6/d6 variables
# Look for `u1, u2, u3, u4, u5 = ...`
p_init = re.compile(r'u1, u2, u3, u4, u5 = None, None, None, None, None')
if p_init.search(content):
    content = p_init.sub('u1, u2, u3, u4, u5, u6 = None, None, None, None, None, None', content)
    
p_init_d = re.compile(r'd1, d2, d3, d4, d5 = False, False, False, False, False')
if p_init_d.search(content):
    content = p_init_d.sub('d1, d2, d3, d4, d5, d6 = False, False, False, False, False, False', content)

print("Updated init variables for u6/d6.")


# --- Task 2: Update Submit Logic ---

# 1. Update lists to include u6, d6
content = content.replace(
    'ordered_uploads = [u1, u2, u3, u4, u5]', 
    'ordered_uploads = [u1, u2, u3, u4, u5, u6]'
)
content = content.replace(
    'ordered_deletes = [d1, d2, d3, d4, d5]', 
    'ordered_deletes = [d1, d2, d3, d4, d5, d6]'
)

# 2. Update loop range(5) -> range(6)
content = content.replace('for i in range(5):', 'for i in range(6):')
print("Updated Submit Logic for 6 images.")


# --- Task 3: Update Gallery Mapping (Card 3) ---

# Current mapping: `p2, p3, p4, p5 = gv(2), gv(3), None, gv(4)` (after recent fix)
# We want to map:
# p2 (Left) = gv(2) (Img 3)
# p3 (Top C) = gv(3) (Img 4)
# p4 (Top R) = gv(5) (Img 6)  <-- New!
# p5 (Bot C) = gv(4) (Img 5)

p_map = re.compile(r'p2, p3, p4, p5 = gv\(2\), gv\(3\), None, gv\(4\)')
if p_map.search(content):
    content = p_map.sub('p2, p3, p4, p5 = gv(2), gv(3), gv(5), gv(4)', content)
    print("Updated Gallery Mapping to fill all 4 slots (3,4,6,5).")
else:
    # If previous fix failed or regex differs?
    # Maybe try original pattern if it wasn't applied?
    # Or strict manual replacement?
    if 'p2, p3, p4, p5 = gv(2), gv(3), None, gv(4)' in content:
        content = content.replace(
            'p2, p3, p4, p5 = gv(2), gv(3), None, gv(4)',
            'p2, p3, p4, p5 = gv(2), gv(3), gv(5), gv(4)'
        )
        print("Updated Gallery Mapping (Simple Replace).")
    else:
        print("Gallery mapping line not found.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
