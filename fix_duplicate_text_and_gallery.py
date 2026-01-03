
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Duplicate Limit Break Text
# Indentation issue. Line 224 caption is inside the for loop.
# It matches `    st.caption("【限界突破】...` (8 spaces).
# Should be 4 spaces.
# I'll replace the loop end and the caption.
# OLD:
#         st.slider(...)
#     
#         st.caption(...)
# NEW:
#         st.slider(...)
# 
#     st.caption(...)

p_dup = re.compile(
    r'(st\.slider\(label, 1, 5, val.*?\))\s+st\.caption\("【限界突破】', 
    re.DOTALL
)

m_dup = p_dup.search(content)
if m_dup:
    # We keep the slider line, newline, then dedented caption
    new_block = m_dup.group(1) + '\n\n    st.caption("【限界突破】'
    content = content.replace(m_dup.group(0), new_block)
    print("Fixed: Dedented Limit Break caption.")
else:
    # Try simpler replacement if regex misses due to whitespace
    if '        st.caption("【限界突破】' in content:
        content = content.replace('        st.caption("【限界突破】', '    st.caption("【限界突破】')
        print("Fixed: Dedented Limit Break caption (Simple Replace).")
    else:
        print("Duplicate text block not found.")

# Fix 2: Gallery Card 3 Mapping
# Change `p2, p3, p4, p5 = gv(2), gv(3), gv(4), gv(5)`
# To `p2, p3, p4, p5 = gv(2), gv(3), None, gv(4)` ??
# User complains "Lower Left" is missing. This usually means Bottom Center (x=368, y_bot).
# Current code: `p5` maps to `gv(5)` (Index 5).
# We only have Indices 0-4. So `p5` is None. Bottom Center is empty.
# Top Right `p4` maps to `gv(4)` (Index 4). This is filled.
# So we have Left, Top Center, Top Right. Bottom Center Empty.
# User wants Bottom Center filled?
# If I move Image 5 to Bottom Center: `p5 = gv(4)`.
# Then Top Right `p4` becomes None.
# Result: Left, Top Center, Bottom Center. (Inverted 'L' shape).
# This seems to match "fill the grid from left to right, top to bottom"?
# Left Col (Tall), Middle Col (Top, Bot), Right Col (Top, Bot).
# Filling 3 gallery images: Left, Mid-Top, Mid-Bot.
# This fixes "Lower Left" (Mid-Bot) missing.

# Pattern: `p2, p3, p4, p5 = gv(2), gv(3), gv(4), gv(5)`
p_map = re.compile(r'p2, p3, p4, p5 = gv\(2\), gv\(3\), gv\(4\), gv\(5\)')

if p_map.search(content):
    # New mapping:
    # p2 (Left) = gv(2) [Image 3]
    # p3 (Top C) = gv(3) [Image 4]
    # p4 (Top R) = None [Empty]
    # p5 (Bot C) = gv(4) [Image 5]
    content = re.sub(
        r'p2, p3, p4, p5 = gv\(2\), gv\(3\), gv\(4\), gv\(5\)',
        'p2, p3, p4, p5 = gv(2), gv(3), None, gv(4)', 
        content
    )
    print("Fixed: Gallery Card 3 Image Mapping (Targeting Bottom Center).")
else:
    print("Gallery mapping line not found.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
