
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# Goal: Restore the missing UI sections and logic in render_register_page.
# Missing: Personality Stats, Image Uploads, Human Relations, Submit Button.
# Also fix the indentation of the Submit Logic.

restore_code = r'''    st.caption("【限界突破】特定のステータスを5以上に設定したい場合は以下で指定してください。")
    lb_col1, lb_col2 = st.columns([2, 1])
    with lb_col1:
        lb_target = st.selectbox("突破するステータス", ["(なし)"] + labels_basic, key="lb_target")
    with lb_col2:
        lb_value = st.number_input("突破値 (6~10)", min_value=6, max_value=10, value=6, key="lb_value")
    
    st.markdown("### 🧠 性格ステータス")
    labels_personality = ["積極性", "協調性", "慎重さ", "適応力", "精神力", "寛容さ", "道徳・倫理観", "社交性"]
    stats_pers_data = existing_data.get('personality_stats', {})
    new_stats_pers = {}
    
    cols_pers = st.columns(4)
    for i, label in enumerate(labels_personality):
        with cols_pers[i % 4]:
            new_stats_pers[label] = st.slider(label, 1, 5, int(stats_pers_data.get(label, 3)))

    st.markdown("### 🖼️ 画像")
    current_images = existing_data.get('images', []) if edit_char_id else []
    if current_images:
        st.image(current_images, width=100, caption=[f"No.{i+1}" for i in range(len(current_images))])

    img_col1, img_col2 = st.columns(2)
    u1, u2, u3, u4, u5 = None, None, None, None, None
    
    with img_col1:
        u1 = st.file_uploader("画像1 (バストショット - 必須)", type=["png", "jpg"], key="u1")
        u3 = st.file_uploader("画像3 (Gallery A)", type=["png", "jpg"], key="u3")
        u5 = st.file_uploader("画像5 (Gallery C)", type=["png", "jpg"], key="u5") 
    with img_col2:
        u2 = st.file_uploader("画像2 (全身 - 推奨)", type=["png", "jpg"], key="u2")
        u4 = st.file_uploader("画像4 (Gallery B)", type=["png", "jpg"], key="u4")

    st.markdown("---")
    st.markdown("### 🤝 人間関係")
    
    r_col1, r_col2, r_col3, r_col4 = st.columns([2, 2, 2, 1])
    existing_chars = [c for c in manager.characters if c['id'] != edit_char_id]
    
    char_options = []
    char_map = {}
    for c in existing_chars:
        # Avoid empty names breaking display
        d = f"{c.get('last_name', '')} {c.get('first_name', '')}".strip()
        if not d: d = c.get('name', 'Unknown')
        char_options.append(d)
        char_map[d] = c['name'] 

    with r_col1:
        r_target_disp = st.selectbox("相手", ["(選択)"] + char_options, key="rel_target")
    with r_col2:
        r_types = st.multiselect("関係性 (複数可)", ["血縁", "仲間", "友人", "ライバル", "敵対", "主従", "恋人", "片思い", "その他"], key="rel_types")
    with r_col3:
        r_desc = st.text_input("詳細", key="rel_desc")
    with r_col4:
        add_rel_btn = st.button("追加")
        
    def edit_relation_callback(idx):
        item = st.session_state.reg_relations.pop(idx)
        # We don't have separate state vars bound to inputs easily without rerunning.
        # This callback approach is tricky in Streamlit. simpler to just delete and re-add.
        pass

    if add_rel_btn:
        if r_target_disp == "(選択)":
            st.warning("相手を選択してください")
        elif not r_types:
            st.warning("関係性を選択してください")
        else:
            target_id = None
            target_name_original = ""
            for c in existing_chars:
                 d = f"{c.get('last_name', '')} {c.get('first_name', '')}".strip()
                 if not d: d = c.get('name', '')
                 if d == r_target_disp:
                     target_id = c['id']
                     target_name_original = d
                     break
            
            if target_id:
                st.session_state.reg_relations.append({
                    "target_id": target_id,
                    "target_name": target_name_original,
                    "type": "/".join(r_types),
                    "desc": r_desc
                })
            else:
                st.error(f"対象キャラクターが見つかりませんでした。")

    if st.session_state.reg_relations:
        st.markdown("#### 設定済みリスト")
        for i, rel in enumerate(st.session_state.reg_relations):
            c1, c2, c3 = st.columns([5, 1, 1])
            with c1:
                st.write(f"**{rel['target_name']}**: [{rel['type']}] {rel['desc']}")
            with c2:
                # Edit button complex logic skipped for stability, just Delete available
                st.write("") 
            with c3:
                if st.button("削除", key=f"del_rel_{i}"):
                    st.session_state.reg_relations.pop(i)
                    st.rerun()

    st.markdown("---")
    
    submitted = st.button("登録 / 更新", type="primary")
    
    if submitted:
        if not first_name_in:
            st.error("名 (First Name) は必須です。")
            return

        new_char = {
            "id": edit_char_id if edit_char_id else str(uuid.uuid4()),
            "user_name": user_name, 
            "name": full_name_combined,
            "last_name": last_name_in,
            "first_name": first_name_in,
            "name_en": name_en_in,
            "bio": bio_in,
            "bio_short": bio_short, 
            "stats": new_stats_basic, 
            "personality_stats": new_stats_pers,
            "details": {
                "race": race_in, 
                "age": age,
                "role": role_in, 
                "origin": origin,
                "height_weight": height_weight,
                "personality": personality_text,
                "appearance": appearance,
                "eye_color": eye_color,
                "hair_color": hair_color,
                "image_color": image_color,
                "memo": memo_in,
            },
            "works_url": works_url, 
            "images": current_images[:], 
            "relations": st.session_state.reg_relations
        }
        
        if lb_target != "(なし)":
             new_char['stats'][lb_target] = lb_value

        # FIX: Ensure order is [u1, u2, u3, u4, u5]
        ordered_uploads = [u1, u2, u3, u4, u5]
        
        updated_paths = []
        for i in range(5): 
            old_path = current_images[i] if i < len(current_images) else None
            new_file = ordered_uploads[i] if i < len(ordered_uploads) else None
            if new_file:
                saved_path = manager.save_image(new_file)
                if saved_path:
                    updated_paths.append(saved_path)
            else:
                if old_path:
                    updated_paths.append(old_path)
        new_char['images'] = updated_paths
        
        if edit_char_id:
            manager.update_character(edit_char_id, new_char)
            st.success("更新しました！")
            st.session_state.view_mode = 'detail'
            st.session_state.selected_char_id = edit_char_id
            st.session_state.editing_char_id = None 
        else:
            manager.add_character(new_char)
            st.success("登録しました！")
            st.session_state.view_mode = 'list'
            
        for k in list(st.session_state.keys()):
            if (k.startswith('reg_') or k.startswith('stat_') or k.startswith('p_stat_') 
                or k.startswith('input_') or k.startswith('picker_') or k == 'bio_input_area'):
                try:
                    del st.session_state[k]
                except:
                    pass
        
        time.sleep(1)
        st.rerun()
'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Identify the broken block.
# Starts from `st.caption("【限界突破】...` (line 223 in view)
# Ends at the end of `render_register_page` (which is before `def render_list_page` or `main` call)

# Careful regex to capture everything from Limit Break UI start to the end of the function body.
# The previous view showed `render_list_page` starting at line 270.
# The broken block is roughly 223 to 267.

start_marker = 'st.caption("【限界突破】特定のステータスを5以上に設定したい場合は以下で指定してください。")'

p_search = re.compile(re.escape(start_marker) + r'.*?(?=def render_list_page)', re.DOTALL)
match = p_search.search(content)

if match:
    # Replace the broken tail with the restored tail
    content = content[:match.start()] + restore_code + "\n\n\n" + content[match.end():]
    print("Mega Fix Applied: Restored Metadata, Image UI, Relations, and Submit Logic.")
else:
    print("Error: Could not find the start marker for replacement.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
