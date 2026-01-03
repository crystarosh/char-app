
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Remove Global Shield Header from main() ---
# Found at line 1647: st.title("🛡️ キャラクター図鑑")
if 'st.title("🛡️ キャラクター図鑑")' in content:
    content = content.replace('st.title("🛡️ キャラクター図鑑")', '')
    print("Removed Global Shield Header.")
else:
    print("Global Shield Header not found (already removed?).")

# --- Task 2: Fix Database Name Formatting (First・Last) ---
# Logic is in `render_list_page` -> Tab 2 -> `for char in filtered_chars:`
# Current code:
# name_disp = char['name']
# if char.get('name_en'):
#     name_disp += f" <br><span style='color:gray; font-size:0.8em'>{char['name_en']}</span>"

# We want to change `name_disp = char['name']` to a priority check.

# Regex to find the loop start and name assignment
# Pattern: `name_disp = char['name']`
# We'll replace it with:
# if char.get('first_name') and char.get('last_name'):
#     base_name = f"{char['first_name']}・{char['last_name']}"
# else:
#     base_name = char['name']
# name_disp = base_name

# But wait, `char['name']` is sometimes constructed from inputs. 
# `char_app.py` line 373: `"name": full_name_combined`
# And `full_name_combined` was `f"{last_name_in} {first_name_in}"`.
# So `char['name']` is "Last First" (space separated).
# User wants "First・Last" (dot separated).

# So I should synthesize it from `first_name` and `last_name` fields if they exist.

p_name_disp = re.compile(r"name_disp = char\['name'\]")
replacement_code = r'''
                    if char.get('first_name') and char.get('last_name'):
                        base_name = f"{char['first_name']}・{char['last_name']}"
                    else:
                        base_name = char['name']
                    name_disp = base_name
'''
# Indentation? `name_disp` is inside `for char` loop (20 spaces? or 16?)
# In `view_file` line 603: `                    name_disp = char['name']` (20 spaces)
# So I should indent my replacement by 20 spaces.

indented_replacement = replacement_code.strip().replace('\n', '\n                    ')

if p_name_disp.search(content):
    content = p_name_disp.sub(indented_replacement, content)
    print("Updated Database Name Formatting logic.")
else:
    print("Name assignment logic not found via regex.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
