
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# Function to update: render_register_page
# Goal: Restore 'memo' input for Card 1 Profile text.
# It should be saved to details['memo'].

update_code = r'''def render_register_page(manager, edit_char_id=None):
    title = "📝 新規キャラクター登録"
    existing_data = {}
    
    # Init session state for relations
    if 'reg_relations' not in st.session_state:
        st.session_state.reg_relations = []
    
    if edit_char_id:
        title = "✏️ キャラクター編集"
        existing_data = manager.get_character(edit_char_id)
        if not existing_data:
            st.error("キャラクターが見つかりません。")
            if st.button("一覧に戻る"):
                st.session_state.editing_char_id = None
                st.session_state.view_mode = 'list'
                st.rerun()
            return

        if 'reg_loaded_id' not in st.session_state or st.session_state.reg_loaded_id != edit_char_id:
            st.session_state.reg_relations = existing_data.get('relations', [])
            st.session_state.reg_loaded_id = edit_char_id
    else:
        if 'reg_loaded_id' in st.session_state and st.session_state.reg_loaded_id is not None:
             st.session_state.reg_relations = []
             st.session_state.reg_loaded_id = None

    if st.button("← 一覧に戻る"):
        st.session_state.editing_char_id = None
        st.session_state.view_mode = 'list'
        st.rerun()

    st.subheader(title)
    
    with st.container():
        user_name = st.text_input("ユーザー名 (PL名)", value=existing_data.get('user_name', ''), placeholder="例: プレイヤーA")
        
        col_name1, col_name2, col_name3 = st.columns([2, 2, 2])
        
        with col_name1:
            last_name_in = st.text_input("姓 (Last Name)", value=existing_data.get('last_name', ''), placeholder="例: ペンドラゴン")
        with col_name2:
            first_name_in = st.text_input("名 (First Name)", value=existing_data.get('first_name', existing_data.get('name', '')), placeholder="例: アーサー")
        with col_name3:
            name_en_in = st.text_input("英語/ローマ字表記", value=existing_data.get('name_en', ''), placeholder="例: Arthur Pendragon")
            
        full_name_combined = f"{last_name_in} {first_name_in}".strip()
        if not full_name_combined:
             full_name_combined = first_name_in 
             
        col1, col2 = st.columns(2)
        details = existing_data.get('details', {})
        
        with col1:
            race_opts = ["人間", "魔族", "聖族", "その他"]
            curr_race = details.get('race', '人間')
            if curr_race not in race_opts: curr_race = 'その他'
            race_in = st.selectbox("種族 (テンプレート選択)", race_opts, index=race_opts.index(curr_race))
            
            role_in = st.text_input("職業 / 表示用種族名", value=details.get('role', ''), placeholder="例: 騎士 / 混血の魔族")
            
            age = st.text_input("年齢", value=details.get('age', ''), placeholder="例: 24歳")
            origin = st.text_input("出身 / 所属", value=details.get('origin', ''), placeholder="例: キャメロット")

        with col2:
            height_weight = st.text_input("身長 / 体重", value=details.get('height_weight', ''), placeholder="例: 180cm / 75kg")
            appearance = st.text_input("容姿 / 外見的特徴", value=details.get('appearance', ''), placeholder="例: 金髪碧眼、右頬に傷")
             
             # --- Color Inputs ---
            def color_picker_callback(picker_key, text_key):
                if picker_key in st.session_state:
                     st.session_state[text_key] = st.session_state[picker_key]

            ec_col1, ec_col2 = st.columns([1, 4])
            with ec_col1:
                current_eye = details.get('eye_color', '#000000')
                if not current_eye.startswith('#') or len(current_eye) != 7: current_eye = '#000000'
                st.color_picker("目", value=current_eye, key="picker_eye", label_visibility="collapsed", on_change=color_picker_callback, args=("picker_eye", "input_eye"))
            with ec_col2:
                eye_color = st.text_input("目の色", value=details.get('eye_color', ''), key="input_eye", placeholder="例: #FF0000")

            hc_col1, hc_col2 = st.columns([1, 4])
            with hc_col1:
                current_hair = details.get('hair_color', '#000000')
                if not current_hair.startswith('#') or len(current_hair) != 7: current_hair = '#000000'
                st.color_picker("髪", value=current_hair, key="picker_hair", label_visibility="collapsed", on_change=color_picker_callback, args=("picker_hair", "input_hair"))
            with hc_col2:
                hair_color = st.text_input("髪の色", value=details.get('hair_color', ''), key="input_hair", placeholder="例: #000000")

            ic_col1, ic_col2 = st.columns([1, 4])
            with ic_col1:
                current_img = details.get('image_color', '#000000')
                if not current_img.startswith('#') or len(current_img) != 7: current_img = '#000000'
                st.color_picker("イメージ", value=current_img, key="picker_img", label_visibility="collapsed", on_change=color_picker_callback, args=("picker_img", "input_img"))
            with ic_col2:
                image_color = st.text_input("イメージカラー", value=details.get('image_color', ''), key="input_img", placeholder="例: #123456")

            personality_text = st.text_input("性格（一言で）", value=details.get('personality', ''), placeholder="例: 正義感が強い、頑固")
            works_url = st.text_input("作品URL / 関連リンク", value=existing_data.get('works_url', ''))
    
    st.markdown("### 📝 詳細設定")
    
    # RESTORED: Card 1 Memo Input
    st.markdown("##### プロフィール画像用テキスト (Card 1)")
    st.caption("Card 1 (Profile) の下部ベージュエリアに表示されるテキストです。約150文字程度推奨。")
    memo_in = st.text_area("プロフィール用簡易設定", value=details.get('memo', ''), height=100, key="memo_input_area")

    st.markdown("##### SNS用（短文） (Card 2)")
    st.caption("Card 2 (Stats) 右下のエリアに表示されるテキストです。約250文字以内で入力してください。")
    bio_short = st.text_area("SNS用短文", value=existing_data.get('bio_short', ''), height=150, max_chars=250, key="bio_short_input")
    
    st.markdown("##### 詳細用（長文） (Web詳細)")
    st.caption("Webの詳細画面で表示される全文です。画像には使用されません。")
    bio_in = st.text_area("詳細設定・裏設定など", value=existing_data.get('bio', ''), height=300, key="bio_input_area")

    st.markdown("### 📊 基礎ステータス")
    labels_basic = ["知力", "体力", "魔力", "防御力", "行動力", "攻撃力", "自信"]
    stats_basic_data = existing_data.get('stats', {})
    new_stats_basic = {}
    
    cols_basic = st.columns(4)
    for i, label in enumerate(labels_basic):
        with cols_basic[i % 4]:
            val = 3
            if label == "防御力":
                 val = int(stats_basic_data.get("防御力", stats_basic_data.get("社交性", 3)))
            else:
                 val = int(stats_basic_data.get(label, 3))
            new_stats_basic[label] = st.slider(label, 1, 5, val)
    
    st.caption("【限界突破】特定のステータスを5以上に設定したい場合は以下で指定してください。")
    lb_col1, lb_col2 = st.columns([2, 1])
    with lb_col1:
        lb_target = st.selectbox("突破するステータス", ["(なし)"] + labels_basic, key="lb_target")
    with lb_col2:
        lb_value = st.number_input("突破値 (6~10)", min_value=6, max_value=10, value=6, key="lb_value")
    
    if lb_target != "(なし)":
        new_stats_basic[lb_target] = lb_value

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
    uploads = []
    with img_col1:
        uploads.append(st.file_uploader("画像1 (バストショット - 必須)", type=["png", "jpg"], key="u1"))
        uploads.append(st.file_uploader("画像3", type=["png", "jpg"], key="u3"))
        uploads.append(st.file_uploader("画像5", type=["png", "jpg"], key="u5")) 
    with img_col2:
        uploads.append(st.file_uploader("画像2 (全身 - 推奨)", type=["png", "jpg"], key="u2"))
        uploads.append(st.file_uploader("画像4", type=["png", "jpg"], key="u4"))

    st.markdown("---")
    st.markdown("### 🤝 人間関係")
    
    r_col1, r_col2, r_col3, r_col4 = st.columns([2, 2, 2, 1])
    existing_chars = [c for c in manager.characters if c['id'] != edit_char_id]
    
    char_options = []
    char_map = {}
    for c in existing_chars:
        disp = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
        if not disp: disp = c['name']
        char_options.append(disp)
        char_map[disp] = c['name'] 

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
        st.session_state.rel_target = item['target_name']
        st.session_state.rel_types = item['type'].split('/')
        st.session_state.rel_desc = item['desc']

    if add_rel_btn:
        if r_target_disp == "(選択)":
            st.warning("相手を選択してください")
        elif not r_types:
            st.warning("関係性を選択してください")
        else:
            target_id = None
            target_name_original = ""
            for c in existing_chars:
                 d = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
                 if not d: d = c['name']
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
                st.button("編集", key=f"edit_rel_{i}", on_click=edit_relation_callback, args=(i,))
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
                "memo": memo_in, # SAVING MEMO
            },
            "works_url": works_url, 
            "images": current_images[:], 
            "relations": st.session_state.reg_relations
        }
        
        if lb_target != "(なし)":
             new_char['stats'][lb_target] = lb_value

        updated_paths = []
        for i in range(5): 
            old_path = current_images[i] if i < len(current_images) else None
            new_file = uploads[i] if i < len(uploads) else None
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
                del st.session_state[k]
        
        time.sleep(1)
        st.rerun()
'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

import re
pattern = re.compile(r"^def render_register_page.*?^(?=def |if __name__)", re.MULTILINE | re.DOTALL)
match = pattern.search(content)

if match:
    # Use re.sub or generic replacement?
    # Simple slicing is safer for big blocks.
    pre = content[:match.start()]
    post = content[match.end():]
    new_content = pre + update_code + "\n\n" + post
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("RESTORED: Card 1 Memo Input.")
else:
    print("Error: Could not find render_register_page block.")
