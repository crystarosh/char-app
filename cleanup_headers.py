
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Remove "Shield Icon" from Header ---
# Find the block:
#         # Header with Logo
#         h_logo, h_title = st.columns([1, 10])
#         with h_logo:
#             st.image("images/logo_shield.png", use_container_width=True)
#         with h_title:
#             st.markdown("# The Legend of Crystarosh Characters List")

# User wants to remove the icon.
# "Delete shield icon only or hide it."
# "Delete word 'Character Zukan' if okay."

# I will replace this whole block with JUST the markdown title (No columns, no icon).
# But wait, user said "Delete the word 'Character Zukan' if okay".
# If they think "The Legend..." IS "Character Zukan", then removing it means NO HEADER.
# "If deleting this whole line... is fine... delete it."
# "Delete the word... if fine."
# I will try to keep the English Title (it looks cool).
# I will remove the Shield Icon part.
# And I will ensure "📚 キャラクター一覧" is gone.

p_header_block = re.compile(r'# Header with Logo.*?st\.markdown\("# The Legend of Crystarosh Characters List"\)', re.DOTALL)

# Replacement: Just the title
replacement_header = r'st.markdown("# The Legend of Crystarosh Characters List")'

if p_header_block.search(content):
    content = p_header_block.sub(replacement_header, content)
    print("Replaced Header Block: Removed Shield Icon, kept English Title.")
else:
    print("Header Block not found via regex.")

# --- Task 2: Remove Old Japanese Header "📚 キャラクター一覧" ---
if 'st.header("📚 キャラクター一覧")' in content:
    content = content.replace('st.header("📚 キャラクター一覧")', '')
    print("Removed Old Japanese Header.")

# --- Task 3: Remove "Character Zukan" text if found elsewhere? ---
# Not found in logic, likely referring to the old header.

# --- Task 4: Fix Indentation of the new header line ---
# The regex replacement puts `st.markdown` where the block started.
# The block logic `st.columns` usage was likely indented 8 spaces.
# My replacement string `st.markdown(...)` has 0 spaces.
# I need to match indentation.
# Regex captures the start. I should check indentation.
# Actually, I'll validly indent the replacement.
# Matches within `if` block (8 spaces).
replacement_header_indented = '        st.markdown("# The Legend of Crystarosh Characters List")'
# Refine logic:
# Find block. Get start pos. Check content.
# Since I used `p_header_block.sub`, I lost context.
# I will reload content and use careful replace.

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for the indented block (4 or 8 spaces)
# It matches:
#         # Header with Logo
#         h_logo, h_title = st.columns([1, 10])
#         with h_logo:
#             st.image("images/logo_shield.png", use_container_width=True)
#         with h_title:
#             st.markdown("# The Legend of Crystarosh Characters List")

# It might be 4 or 8 spaces depending on previous fix.
# I will match strictly.
p_block = re.compile(r'(\s+)# Header with Logo.*?\1    st\.markdown\("# The Legend of Crystarosh Characters List"\)', re.DOTALL)

def replace_fn(match):
    indent = match.group(1)
    # Return just the title, indented
    return f'{indent}st.markdown("# The Legend of Crystarosh Characters List")'

content = p_block.sub(replace_fn, content)
print("Smartly removed Shield layout, kept Title.")

# Remove old header if present
content = content.replace('st.header("📚 キャラクター一覧")', '')

# Save
with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
