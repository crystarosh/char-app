
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- 1. Change Primary Button Color (#800000 -> #330000) ---
# Also update hover (#a00000 -> #550000)
content = content.replace("#800000", "#330000")
content = content.replace("#a00000", "#550000")
print("Updated Primary Button Colors to Darker Blood Red (#330000).")

# --- 2. Update Page Config (Title & Icon) ---
# Old: st.set_page_config(page_title="...", layout='wide') or similar.
# We want: st.set_page_config(page_title="The Legend of Crystarosh Characters List", page_icon="images/favicon.png", layout="wide")

new_title = "The Legend of Crystarosh Characters List"
new_icon = "images/favicon.png"

# Regex replace st.set_page_config parameters
# Pattern matches `st.set_page_config(...)` non-greedy
p_config = re.compile(r'st\.set_page_config\((.*?)\)', re.DOTALL)
match = p_config.search(content)
if match:
    # We replace the whole call to be safe and clean
    # We maintain layout='wide'
    replacement = f'st.set_page_config(page_title="{new_title}", page_icon="{new_icon}", layout="wide")'
    content = p_config.sub(replacement, content)
    print("Updated Page Config (Title, Icon).")
else:
    # If not found, check if we should add it? It usually exists.
    # We'll prepend it to main() or top of script if missing.
    # But it likely exists.
    print("Warning: st.set_page_config not found via regex.")

# --- 3. Update Visual Headers ---
# Find: st.header("📚 キャラクター一覧")
# Replace with: st.header("The Legend of Crystarosh Characters List")
# Also maybe "新規キャラクター登録" -> "New Character Registration"? User didn't ask for that. 
# Just the "Title? Character book..." request. I'll stick to the "List" page header.
content = content.replace('st.header("📚 キャラクター一覧")', f'st.header("{new_title}")')

# Also update the logic if it uses h1/h2?
# content = content.replace('st.title("キャラクター一覧")', f'st.title("{new_title}")') # Just in case

print("Updated Visual Headers.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
