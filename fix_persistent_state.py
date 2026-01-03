
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# This script performs 3 tasks:
# 1. Update `def main()` to init reg_form_key and sidebar button to rotate it.
# 2. Add "Jump to Character" dropdown to `render_relation_page`.
# 3. Mass update `render_register_page` to use `key=f"..._{sid}"` for all inputs.

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Task 1: Main & Sidebar ---

# 1a. Init reg_form_key in main start
# Look for `def main():` and `st.title(...)`
if "if 'reg_form_key' not in st.session_state:" not in content:
    content = content.replace(
        'st.title("🛡️ キャラクター図鑑")', 
        'st.title("🛡️ キャラクター図鑑")\n    if "reg_form_key" not in st.session_state:\n        st.session_state.reg_form_key = str(uuid.uuid4())'
    )

# 1b. Rotate key in Sidebar Button
# Find the sidebar button block we fixed earlier.
# Pattern: `if st.sidebar.button("➕ 新規登録", use_container_width=True):`
# We want to add `st.session_state.reg_form_key = str(uuid.uuid4())` before `st.rerun()`.
# Using regex to inject it.
p_sidebar = re.compile(r'(if st\.sidebar\.button\("➕ 新規登録".*?st\.session_state\.editing_char_id = None)', re.DOTALL)
m_sidebar = p_sidebar.search(content)
if m_sidebar:
    # Inject the key rotation
    replacement = m_sidebar.group(1) + '\n        st.session_state.reg_form_key = str(uuid.uuid4())'
    content = content.replace(m_sidebar.group(1), replacement)
    print("Updated Sidebar Button to rotate session key.")


# --- Task 2: Graph Navigation ---

# Find `st.markdown("### 凡例")` in `render_relation_page`.
# Add the jumper before or after.
if "詳細を見るキャラクター" not in content:
    jumper_code = r'''
    st.markdown("---")
    st.markdown("### 🔗 詳細ページへ移動")
    nav_opts = ["(選択してください)"] + [c['name'] for c in manager.characters]
    nav_sel = st.selectbox("詳細を見るキャラクターを選択", nav_opts, key="graph_nav_sel")
    if nav_sel != "(選択してください)":
        target = next((c for c in manager.characters if c['name'] == nav_sel), None)
        if target:
            st.session_state.selected_char_id = target['id']
            st.session_state.view_mode = 'detail'
            st.rerun()

    st.markdown("### 凡例")'''
    
    content = content.replace('st.markdown("### 凡例")', jumper_code)
    print("Added Graph Navigation Dropdown.")


# --- Task 3: Render Register Page Mass Key Injection ---

# This is the tricky part. Regex replacement of input calls to append unique suffix.
# Target function: `render_register_page`
# Strategy: 
# 1. Define `sid = st.session_state.reg_form_key` at start of function.
# 2. Use regex to find `st.text_input(..., key="...")` and `st.text_input(..., key=...)`??
#    Most don't have key.
#    `st.text_input("Label", ...)` -> `st.text_input("Label", ..., key=f"label_{sid}")`
#    This is hard to regex robustly for all distinct inputs.
#    
#    Instead, I will manually reconstruct the critical top section logic where most unkeyed inputs are.
#    And simpler regex for the rest.

# 3a. Inject `sid` definition
# Find `st.subheader(title)` -> add `sid = st.session_state.get('reg_form_key', 'init')`
content = content.replace(
    'st.subheader(title)', 
    'st.subheader(title)\n    sid = st.session_state.get("reg_form_key", "init")'
)

# 3b. Helpers for regex replacement
def add_key_to_widget(match):
    # match.group(0) is the entire `st.text_input(...)` line/block
    # Check if `key=` exists.
    text = match.group(0)
    
    # Extract label to form a unique key base
    # Label is usually the first string arg: `("Label"` or `('Label'`
    m_label = re.search(r'\(["\'](.*?)["\']', text)
    if not m_label: return text # Can't find label, skip
    
    label_slug = "".join([c if c.isalnum() else "_" for c in m_label.group(1)])[:20]
    
    if "key=" in text:
        # Replace existing key value with suffixed version
        # key="my_key" -> key=f"my_key_{sid}"
        # key='my_key' -> key=f"my_key_{sid}"
        return re.sub(r'key=["\'](.*?)["\']', r'key=f"\1_{sid}"', text)
    else:
        # Insert key=...
        # Look for closing parenthesis.
        # This is simple if line ends with `)`
        # `st.text_input("...", value=...)` -> `st.text_input(..., key=f"{label_slug}_{sid}")`
        if text.endswith(')'):
             return text[:-1] + f', key=f"{label_slug}_{sid}")'
        return text # Multi-line? Skip for safety or simple replace

# Apply to typical single-line inputs in the top block
# We target lines like: `var = st.text_input("Label", ...)`
# Pattern: `\s+\w+\s+=\s+st\.(text_input|selectbox|color_picker)\(.*?\)
# But `color_picker` has callback args we must be careful.
# Let's focus on `text_input` in the top block which causes the persistence.

patterns = [
    (r'st\.text_input\(".*?"[^)]+\)', add_key_to_widget),
    (r'st\.selectbox\(".*?"[^)]+\)', add_key_to_widget),
    # Handles: user_name, last_name, first_name, name_en, race, role, age, origin, height, appearance, eye_color_text, hair_color_text, image_color_text, personality, works.
]

# We must only apply this inside `render_register_page`.
p_func = re.compile(r'def render_register_page\(.*?:(.*?)def ', re.DOTALL)
m_func = p_func.search(content)

if m_func:
    func_body = m_func.group(1)
    new_body = func_body
    
    # We replace strict single-line calls first to be safe.
    # st.text_input("Label", val, placeholder)
    
    # Specific targeted replacements for the top block variables to ensure keys.
    # user_name
    new_body = re.sub(
        r'(user_name\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"user_name_{sid}"', 
        new_body
    )
    # last_name
    new_body = re.sub(
        r'(last_name_in\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"last_name_{sid}"', 
        new_body
    )
    # first_name
    new_body = re.sub(
        r'(first_name_in\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"first_name_{sid}"', 
        new_body
    )
    # name_en
    new_body = re.sub(
        r'(name_en_in\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"name_en_{sid}"', 
        new_body
    )
    # race_in (Selectbox)
    new_body = re.sub(
        r'(race_in\s*=\s*st\.selectbox\(".*?")', 
        r'\1, key=f"race_{sid}"', 
        new_body
    )
    # role_in
    new_body = re.sub(
        r'(role_in\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"role_{sid}"', 
        new_body
    )
    # age
    new_body = re.sub(
        r'(age\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"age_{sid}"', 
        new_body
    )
    # origin
    new_body = re.sub(
        r'(origin\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"origin_{sid}"', 
        new_body
    )
    # height_weight
    new_body = re.sub(
        r'(height_weight\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"hw_{sid}"', 
        new_body
    )
    # appearance
    new_body = re.sub(
        r'(appearance\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"app_{sid}"', 
        new_body
    )
    # personality_text
    new_body = re.sub(
        r'(personality_text\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"pers_{sid}"', 
        new_body
    )
    # works_url
    new_body = re.sub(
        r'(works_url\s*=\s*st\.text_input\(".*?")', 
        r'\1, key=f"works_{sid}"', 
        new_body
    )
    
    # Colors (special case, have keys already)
    # existing key="picker_eye" -> key=f"picker_eye_{sid}"
    new_body = re.sub(r'key="picker_eye"', 'key=f"picker_eye_{sid}"', new_body)
    new_body = re.sub(r'key="input_eye"', 'key=f"input_eye_{sid}"', new_body)
    new_body = re.sub(r'key="picker_hair"', 'key=f"picker_hair_{sid}"', new_body)
    new_body = re.sub(r'key="input_hair"', 'key=f"input_hair_{sid}"', new_body)
    new_body = re.sub(r'key="picker_img"', 'key=f"picker_img_{sid}"', new_body)
    new_body = re.sub(r'key="input_img"', 'key=f"input_img_{sid}"', new_body)
    
    # Bio/Memo
    new_body = re.sub(r'key="memo_input_area"', 'key=f"memo_{sid}"', new_body)
    new_body = re.sub(r'key="bio_short_input"', 'key=f"bio_s_{sid}"', new_body)
    new_body = re.sub(r'key="bio_input_area"', 'key=f"bio_l_{sid}"', new_body)
    
    # Stats Sliders (Loop)
    # `st.slider(label, 1, 5, val)` -> `st.slider(label, 1, 5, val, key=f"stat_{label}_{sid}")`
    # Regex for slider without key
    new_body = re.sub(
        r'st\.slider\(label, 1, 5, val\)', 
        r'st.slider(label, 1, 5, val, key=f"stat_{label}_{sid}")', 
        new_body
    )
    # Personality Sliders
    new_body = re.sub(
        r'st\.slider\(label, 1, 5, int\(stats_pers_data\.get\(label, 3\)\)\)', 
        r'st.slider(label, 1, 5, int(stats_pers_data.get(label, 3)), key=f"pstat_{label}_{sid}")', 
        new_body
    )
    
    # Limit Break
    new_body = re.sub(r'key="lb_target"', 'key=f"lb_t_{sid}"', new_body)
    new_body = re.sub(r'key="lb_value"', 'key=f"lb_v_{sid}"', new_body)
    
    # Images with existing keys
    # key="u1" -> key=f"u1_{sid}"
    for i in range(1, 6):
        new_body = re.sub(f'key="u{i}"', f'key=f"u{i}_{{sid}}"', new_body)
        new_body = re.sub(f'key="del_img_{i}"', f'key=f"del_img_{i}_{{sid}}"', new_body)

    # Relations
    new_body = re.sub(r'key="rel_target"', 'key=f"rel_{sid}"', new_body)
    new_body = re.sub(r'key="rel_types"', 'key=f"relt_{sid}"', new_body)
    new_body = re.sub(r'key="rel_desc"', 'key=f"reld_{sid}"', new_body)
    # Delete button in relations loop: key=f"del_rel_{i}" -> key=f"del_rel_{i}_{sid}"
    new_body = re.sub(r'key=f"del_rel_\{i\}"', r'key=f"del_rel_{i}_{sid}"', new_body)
    
    # Update content
    content = content.replace(func_body, new_body)
    print("Mass updated widgets in render_register_page with dynamic keys.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
