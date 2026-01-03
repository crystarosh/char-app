
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# Goal: Restore "Delete Image" checkboxes in Edit Mode.
# Modifying Image UI block and Submit Logic.

restore_delete_code = r'''    st.markdown("### 🖼️ 画像")
    current_images = existing_data.get('images', []) if edit_char_id else []
    
    # helper to get path safely
    def get_cur(idx):
        if idx < len(current_images): return current_images[idx]
        return None

    img_col1, img_col2 = st.columns(2)
    u1, u2, u3, u4, u5 = None, None, None, None, None
    d1, d2, d3, d4, d5 = False, False, False, False, False
    
    with img_col1:
        st.markdown("**画像1 (Profile)**")
        if get_cur(0): 
            st.image(get_cur(0), width=100)
            d1 = st.checkbox("画像1を削除", key="del_img_1")
        u1 = st.file_uploader("上書き/新規 (No.1)", type=["png", "jpg"], key="u1")
        
        st.markdown("**画像3 (Gallery A)**")
        if get_cur(2): 
            st.image(get_cur(2), width=100)
            d3 = st.checkbox("画像3を削除", key="del_img_3")
        u3 = st.file_uploader("上書き/新規 (No.3)", type=["png", "jpg"], key="u3")
        
        st.markdown("**画像5 (Gallery C)**")
        if get_cur(4): 
            st.image(get_cur(4), width=100)
            d5 = st.checkbox("画像5を削除", key="del_img_5")
        u5 = st.file_uploader("上書き/新規 (No.5)", type=["png", "jpg"], key="u5")

    with img_col2:
        st.markdown("**画像2 (Full Body)**")
        if get_cur(1): 
            st.image(get_cur(1), width=100)
            d2 = st.checkbox("画像2を削除", key="del_img_2")
        u2 = st.file_uploader("上書き/新規 (No.2)", type=["png", "jpg"], key="u2")
        
        st.markdown("**画像4 (Gallery B)**")
        if get_cur(3): 
            st.image(get_cur(3), width=100)
            d4 = st.checkbox("画像4を削除", key="del_img_4")
        u4 = st.file_uploader("上書き/新規 (No.4)", type=["png", "jpg"], key="u4")

    st.markdown("---")
'''

submit_logic_update = r'''        # FIX: Ensure order is [u1, u2, u3, u4, u5] AND Handle Deletion
        ordered_uploads = [u1, u2, u3, u4, u5]
        ordered_deletes = [d1, d2, d3, d4, d5]
        
        updated_paths = []
        for i in range(5): 
            old_path = current_images[i] if i < len(current_images) else None
            new_file = ordered_uploads[i] if i < len(ordered_uploads) else None
            is_deleted = ordered_deletes[i] if i < len(ordered_deletes) else False
            
            # Logic:
            # 1. New File Uploaded -> Use New File (Limit Break)
            # 2. Deleted Checked -> Use None (Remove)
            # 3. Old Path Exists -> Keep Old Path
            
            final_path = None
            if new_file:
                saved_path = manager.save_image(new_file)
                if saved_path:
                    final_path = saved_path
            elif is_deleted:
                final_path = None # Explicitly remove
            else:
                if old_path:
                    final_path = old_path
            
            # Note: We must maintain the LIST SIZE or allow None holes?
            # V33 renderer logic iterates `imgs` list.
            # If we remove item 2, indices shift! This causes scramble again.
            # We MUST Insert None or placeholder if we want to preserve "Slot 5".
            # BUT Current logic `updated_paths.append` creates a dense list.
            # If user deletes Image 3, Image 4 becomes Image 3.
            # This SHIFTS the layout.
            # Is this desired?
            # If user wants to "Empty Slot 3" but keep "Slot 4"...
            # The current system uses `len(images)` logic implicitly?
            # No, `create_card_3` uses `p2 = gv(2)`, `p3 = gv(3)`.
            # If we delete index 2, then index 3 becomes 2.
            # So Image 4 MOVES to Slot 3 (Left Tall).
            # This is standard list behavior.
            # If user wants fixed slots, we need to store `[path, path, None, path]`.
            # Does `manager.save` support storing None?
            # `current_images` comes from json.
            # If `updated_paths` has None, does JSON save it? Yes, null.
            # `gv(i)` handle None? `return imgs[i] ... if ... os.path.exists`.
            # So None is safe.
            # So I should APPEND None if necessary to keep alignment?
            # Actually, `render_register_page` usually compacts lists?
            # My previous code: `if final_path: updated_paths.append`.
            # This COMPACTS.
            # Meaning: Deleting Image 3 shifts Image 4 to Position 3.
            # This explains why users get confused about layout positions!
            # If they want specific layout, they rely on Index.
            # If I pad with None, I can preserve slots.
            # Let's try to PAD with None to length 5.
            
            updated_paths.append(final_path)
            
        new_char['images'] = updated_paths
'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Block 1: Image UI
p1 = re.compile(r'st\.markdown\("### 🖼️ 画像"\).*?(?=st\.markdown\("### 🤝 人間関係"\))', re.DOTALL)
m1 = p1.search(content)

if m1:
    content = content[:m1.start()] + restore_delete_code + content[m1.end():]
    print("RESTORED: Image Delete Checkboxes & Slot-based UI.")
else:
    print("Block 1 not found.")

# Block 2: Submit Logic
p2 = re.compile(r'# FIX: Ensure order is \[u1.*?new_char\[\'images\'\] = updated_paths', re.DOTALL)
m2 = p2.search(content)

if m2:
    content = content[:m2.start()] + submit_logic_update + content[m2.end():]
    print("UPDATED: Submit Logic to handle Deletion and Nones.")
else:
    print("Block 2 not found.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
