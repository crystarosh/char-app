import streamlit as st
import json
import os
import uuid
from PIL import Image
import plotly.graph_objects as go
import networkx as nx
import time
import base64
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
DATA_DIR = "data"
IMAGES_DIR = "images"
JSON_FILE = os.path.join(DATA_DIR, "characters.json")



# --- Data Management Class ---
class CharacterManager:
    def __init__(self):
        self._ensure_directories()
        self.characters = self.load_data()

    def _ensure_directories(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
        if not os.path.exists(JSON_FILE):
             with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def load_data(self):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_data(self):
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.characters, f, indent=4, ensure_ascii=False)

    def add_character(self, char_data):
        self.characters.append(char_data)
        self.save_data()

    def save_image(self, uploaded_file):
        if uploaded_file is None:
            return None
        
        file_ext = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(IMAGES_DIR, unique_filename)
        
        # Save explicitly using PIL or just write bytes
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path

    def get_character(self, char_id):
        for char in self.characters:
            if char['id'] == char_id:
                return char
        return None

    def delete_character(self, char_id):
        self.characters = [c for c in self.characters if c['id'] != char_id]
        self.save_data()

    def update_character(self, char_id, updated_data):
        for i, char in enumerate(self.characters):
            if char['id'] == char_id:
                # Merge or replace. Here we replace but keep ID.
                updated_data['id'] = char_id
                # Keep images if not updated? Or handle in UI.
                # If updated_data['images'] is empty, should we keep old ones?
                # The UI logic will handle what to pass.
                self.characters[i] = updated_data
                self.save_data()
                return True
        return False

# --- UI Functions (Placeholders) ---
def render_register_page(manager, edit_char_id=None):
    title = "📝 新規キャラクター登録"
    btn_label = "登録する"
    existing_data = {}
    
    # Init session state for relations
    if 'reg_relations' not in st.session_state:
        st.session_state.reg_relations = []
    
    if edit_char_id:
        title = "✏️ キャラクター編集"
        btn_label = "更新する"
        existing_data = manager.get_character(edit_char_id)
        if not existing_data:
            st.error("キャラクターが見つかりません。")
            if st.button("一覧に戻る"):
                st.session_state.editing_char_id = None
                st.session_state.view_mode = 'list'
                st.rerun()
            return

        # Load relations into state only once/on change
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

    st.subheader("📝 キャラクター基本登録")
    
    # Name Handling (Split)
    with st.container():
        # User Name (PL Name)
        user_name = st.text_input("ユーザー名 (PL名)", value=existing_data.get('user_name', ''), placeholder="例: プレイヤーA")
        
        # Name Inputs
        col_name1, col_name2, col_name3 = st.columns([2, 2, 2])
        
        with col_name1:
            last_name_in = st.text_input("姓 (Last Name)", value=existing_data.get('last_name', ''), placeholder="例: ペンドラゴン")
        with col_name2:
            first_name_in = st.text_input("名 (First Name)", value=existing_data.get('first_name', existing_data.get('name', '')), placeholder="例: アーサー")
        with col_name3:
            # New Field: English / Romaji Name
            name_en_in = st.text_input("英語/ローマ字表記", value=existing_data.get('name_en', ''), placeholder="例: Arthur Pendragon")
            
        full_name_combined = f"{last_name_in} {first_name_in}".strip()
        if not full_name_combined:
             full_name_combined = first_name_in # Fallback
        col1, col2 = st.columns(2)
        details = existing_data.get('details', {})
        
        with col1:
            # Removed separate name input, integrated above
            role = st.text_input("種族 / 職業", value=details.get('role', ''), placeholder="例: 人間 / 騎士")
            age = st.text_input("年齢", value=details.get('age', ''), placeholder="例: 24歳")
            origin = st.text_input("出身 / 所属", value=details.get('origin', ''), placeholder="例: キャメロット")

        with col2:
            height_weight = st.text_input("身長 / 体重", value=details.get('height_weight', ''), placeholder="例: 180cm / 75kg")
            appearance = st.text_input("容姿 / 外見的特徴", value=details.get('appearance', ''), placeholder="例: 金髪碧眼、右頬に傷")
             
             # --- Color Inputs ---
            def color_picker_callback(picker_key, text_key):
                # Always update if key exists, even if black
                if picker_key in st.session_state:
                     st.session_state[text_key] = st.session_state[picker_key]

            # Eye Color
            ec_col1, ec_col2 = st.columns([1, 4])
            with ec_col1:
                # Default logic: if hex is valid use it, else #000000.
                current_eye = details.get('eye_color', '#000000')
                if not current_eye.startswith('#') or len(current_eye) != 7: current_eye = '#000000'
                st.color_picker("目", value=current_eye, key="picker_eye", label_visibility="collapsed", on_change=color_picker_callback, args=("picker_eye", "input_eye"))
            with ec_col2:
                eye_color = st.text_input("目の色", value=details.get('eye_color', ''), key="input_eye", placeholder="例: #FF0000")

            # Hair Color
            hc_col1, hc_col2 = st.columns([1, 4])
            with hc_col1:
                current_hair = details.get('hair_color', '#000000')
                if not current_hair.startswith('#') or len(current_hair) != 7: current_hair = '#000000'
                st.color_picker("髪", value=current_hair, key="picker_hair", label_visibility="collapsed", on_change=color_picker_callback, args=("picker_hair", "input_hair"))
            with hc_col2:
                hair_color = st.text_input("髪の色", value=details.get('hair_color', ''), key="input_hair", placeholder="例: #000000")

            # Image Color
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
    
    # Bio Split: Short (SNS) and Long (Detail)
    # Existing 'bio' mapped to Long. New 'bio_short' to Short.
    
    st.markdown("##### SNS用（短文）")
    st.caption("SNS画像（詳細）に表示されるテキストです。約250文字以内で入力してください（推奨）。")
    bio_short = st.text_area("SNS用短文", value=existing_data.get('bio_short', ''), height=150, max_chars=250, key="bio_short_input")
    
    st.markdown("##### 詳細用（長文）")
    st.caption("詳細画面で表示される全文です。折りたたんで表示されます。")
    bio_in = st.text_area("詳細設定・裏設定など", value=existing_data.get('bio', ''), height=300, key="bio_input_area")

    st.markdown("### 📊 基礎ステータス")
    # Changed "社交性" -> "防御力"
    labels_basic = ["知力", "体力", "魔力", "防御力", "行動力", "攻撃力", "自信"]
    stats_basic_data = existing_data.get('stats', {})
    new_stats_basic = {}
    
    cols_basic = st.columns(4)
    for i, label in enumerate(labels_basic):
        with cols_basic[i % 4]:
            val = 3
            if label == "防御力":
                 # Migrate from old "社交性" if exists, or default 3
                 val = int(stats_basic_data.get("防御力", stats_basic_data.get("社交性", 3)))
            else:
                 val = int(stats_basic_data.get(label, 3))
            new_stats_basic[label] = st.slider(label, 1, 5, val)
    
    # Limit Break Option
    st.caption("【限界突破】特定のステータスを5以上に設定したい場合は以下で指定してください。")
    lb_col1, lb_col2 = st.columns([2, 1])
    with lb_col1:
        lb_target = st.selectbox("突破するステータス", ["(なし)"] + labels_basic, key="lb_target")
    with lb_col2:
        lb_value = st.number_input("突破値 (6~10)", min_value=6, max_value=10, value=6, key="lb_value")
    
    # Apply Limit Break
    if lb_target != "(なし)":
        new_stats_basic[lb_target] = lb_value

    st.markdown("### 🧠 性格ステータス")
    # Added "社交性"
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
        uploads.append(st.file_uploader("画像5", type=["png", "jpg"], key="u5")) # New 5th slot
    with img_col2:
        uploads.append(st.file_uploader("画像2 (全身 - 推奨)", type=["png", "jpg"], key="u2"))
        uploads.append(st.file_uploader("画像4", type=["png", "jpg"], key="u4"))

    # Bio input removed (duplicate). 
    # Use the one at the top.
    
    st.markdown("---")
    st.markdown("### 🤝 人間関係")
    
    r_col1, r_col2, r_col3, r_col4 = st.columns([2, 2, 2, 1])
    existing_chars = [c for c in manager.characters if c['id'] != edit_char_id]
    
    # Format names as "First Last"
    char_options = []
    char_map = {}
    for c in existing_chars:
        disp = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
        if not disp: disp = c['name']
        char_options.append(disp)
        char_map[disp] = c['name'] # Map back to original name for logic if needed, but safer to lookup by ID

    with r_col1:
        r_target_disp = st.selectbox("相手", ["(選択)"] + char_options, key="rel_target")
        
        # We need to map display name back to original 'name' (target_name) stored in JSON?
        # Actually, stored target_name should probably be full name. 
        # But existing logic uses `c['name']`.
        # Let's find the character object matching the display name.
        
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
            # Safely look for target_id using display name matching
            # Construct display name for each existing char to match
            target_id = None
            target_name_original = ""
            
            for c in existing_chars:
                 d = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
                 if not d: d = c['name']
                 if d == r_target_disp:
                     target_id = c['id']
                     target_name_original = c['name'] # Keep original name for data consistency? Or update?
                     # User wants name order "First Last". If we save "First Last" in target_name, displayed elsewhere will be correct.
                     # But graph uses `target_name`.
                     # Let's save the Display Name as target_name.
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
                st.error(f"対象キャラクター '{r_target}' が見つかりませんでした。リストから選択し直してください。")

    if st.session_state.reg_relations:
        st.markdown("#### 設定済みリスト")
        for i, rel in enumerate(st.session_state.reg_relations):
            c1, c2, c3 = st.columns([5, 1, 1])
            with c1:
                st.write(f"**{rel['target_name']}**: [{rel['type']}] {rel['desc']}")
            with c2:
                # Edit Button: Use callback to update state before rerun
                st.button("編集", key=f"edit_rel_{i}", on_click=edit_relation_callback, args=(i,))
            with c3:
                if st.button("削除", key=f"del_rel_{i}"):
                    st.session_state.reg_relations.pop(i)
                    st.rerun()

    st.markdown("---")
    
    # Removed old submit button logic that referenced undefined 'name'
    # and caused duplicate buttons.
    pass

    submitted = st.button("登録 / 更新", type="primary")
    
    if submitted:
        if not first_name_in:
            st.error("名 (First Name) は必須です。")
            return

        new_char = {
            "id": edit_char_id if edit_char_id else str(uuid.uuid4()),
            "user_name": user_name, # Added User Name
            "name": full_name_combined,
            "last_name": last_name_in,
            "first_name": first_name_in,
            "name_en": name_en_in, # New Field
            "bio": bio_in,
            "bio_short": bio_short, # Added Bio Short
            "stats": new_stats_basic, # Use slider values
            "personality_stats": new_stats_pers,
            "details": {
                "age": age,
                "role": role,
                "origin": origin,
                "height_weight": height_weight,
                "personality": personality_text,
                "appearance": appearance,
                "eye_color": eye_color,
                "hair_color": hair_color,
                "image_color": image_color,
            },
            "works_url": works_url, # Deprecate or keep hidden
            "images": current_images[:], # Start with existing images
            "relations": st.session_state.reg_relations
        }
        
        # Handle Limit Break Override
        if lb_target != "(なし)":
             new_char['stats'][lb_target] = lb_value

        # Handle New Images
        updated_paths = []
        for i in range(5): # Up to 5
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
            # Redirect to Detail View
            st.session_state.view_mode = 'detail'
            st.session_state.selected_char_id = edit_char_id
            st.session_state.editing_char_id = None # Clear editing flag
        else:
            manager.add_character(new_char)
            st.success("登録しました！")
            st.session_state.view_mode = 'list'
            
        # Clear form state keys
        for k in list(st.session_state.keys()):
            if (k.startswith('reg_') or k.startswith('stat_') or k.startswith('p_stat_') 
                or k.startswith('input_') or k.startswith('picker_') or k == 'bio_input_area'):
                del st.session_state[k]
        
        time.sleep(1)
        st.rerun()

def render_list_page(manager):
    # Mode Management
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'list'
    if 'selected_char_id' not in st.session_state:
        st.session_state.selected_char_id = None

    # check if editing (which might have been set from detail view)
    if st.session_state.get('editing_char_id'):
         render_register_page(manager, st.session_state.editing_char_id)
         return

    # --- LIST MODE ---
    if st.session_state.view_mode == 'list':
        st.header("📚 キャラクター一覧")
        
        # CSS for 1:1 Thumbnails and better cards
        st.markdown("""
        <style>
        .char-card-container {
            position: relative;
            margin-bottom: 20px;
            cursor: pointer;
        }
        .char-card-img {
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            border-radius: 8px 8px 0 0;
            display: block;
        }
        .stButton button {
            width: 100%;
            border-radius: 0 0 8px 8px !important;
            margin-top: 0px !important;
            padding-top: 10px;
            padding-bottom: 10px;
            border-top: none;
        }
        /* CSS Hack to make button cover image? Too risky. 
           Instead, just style the button to look integrated and remove gap. */
        </style>
        """, unsafe_allow_html=True)
        
        if not manager.characters:
            st.info("キャラクターが登録されていません。")
            return

        # Grid Layout (5 columns for tighter packing)
        cols = st.columns(5)
        for i, char in enumerate(manager.characters):
            with cols[i % 5]:
                 # Image: Force Square Crop
                 target_img = char['images'][0] if char['images'] else None
                 if target_img:
                     try:
                         # Crop on the fly
                         from PIL import Image as PILImage # Avoid conflict if any
                         p_img = PILImage.open(target_img)
                         min_d = min(p_img.size)
                         cw, ch = p_img.size
                         left = (cw - min_d) / 2
                         top = (ch - min_d) / 2
                         right = (cw + min_d) / 2
                         bottom = (ch + min_d) / 2
                         crop_img = p_img.crop((left, top, right, bottom))
                         st.image(crop_img, use_container_width=True)
                     except:
                         st.image(target_img, use_container_width=True)
                 else:
                     st.markdown('<div style="aspect-ratio:1/1; background:#eee;"></div>', unsafe_allow_html=True)
                 
                 # Label: use first_name if available, else name
                 disp_name = char.get('first_name', char['name'])
                 
                 # Button using display name
                 if st.button(disp_name, key=f"sel_{char['id']}", use_container_width=True):
                     st.session_state.selected_char_id = char['id']
                     st.session_state.view_mode = 'detail'
                     st.rerun()

    # --- DETAIL MODE ---
    elif st.session_state.view_mode == 'detail':
        char_id = st.session_state.selected_char_id
        char = manager.get_character(char_id)
        
        if not char:
             st.session_state.view_mode = 'list'
             st.rerun()
             return

        # Navigation Callback
        def go_back():
            st.session_state.view_mode = 'list'
            st.session_state.selected_char_id = None
        
        # Header (Fixed: First Last order)
        h_col1, h_col2 = st.columns([6, 1])
        with h_col1:
            # Construct name: First Last
            d_name = char['name']
            if char.get('first_name') and char.get('last_name'):
                d_name = f"{char['first_name']} {char['last_name']}"
            st.header(d_name) 
        with h_col2:
            st.button("詳細を閉じる", key="back_btn_top", on_click=go_back)

        # Layout
        col_main, col_info = st.columns([1, 2])
        
        with col_main:
            # Main Image
            if char['images']:
                st.image(char['images'][0], use_container_width=True)

            # Sub Images Gallery with Viewer Mode
            if len(char['images']) > 1:
                st.markdown("##### 📸 ギャラリー")
                cols_sub = st.columns(3)
                for i, img_path in enumerate(char['images'][1:]):
                    with cols_sub[i % 3]:
                        # Make thumbnail clickable to simple expander?
                        # Streamlit image click -> fullscreen is default.
                        # User wants "Popup" but "Don't get stuck".
                        # If we use `st.button` with image as label? No.
                        # We can use a button "🔍" under each image to open a modal-like view.
                        st.image(img_path, use_container_width=True)
                        if st.button("拡大", key=f"view_{i}"):
                            st.session_state.view_mode = 'image_view'
                            st.session_state.view_img_path = img_path
                            st.rerun()

        with col_info:
            # Basic Stats
            st.markdown("### 📊 ステータス")

            # Check Limit Break
            over_5_stats = []
            for k, v in char.get('stats', {}).items():
                if v > 5:
                    over_5_stats.append(f"{k}: {v}")

            if over_5_stats:
                st.caption(f"⚡ 限界突破: {', '.join(over_5_stats)}")

            def draw_radar(title, stats_dict, color):
                if not stats_dict: return
                categories = list(stats_dict.keys())
                values = list(stats_dict.values())
                categories.append(categories[0])
                values.append(values[0]) # Close loop
                
                # Enhanced Limit Break Visualization (Revised)
                # Requirement: 
                # - Base outer boundary at 5.
                # - Values > 5 are placed on a "further outer dotted line" regardless of value.
                # Implementation:
                # - Map all values > 5 to exactly 6 (visual max).
                # - Set chart range to [0, 6].
                # - Draw a strong grid line at 5.
                # - Draw a dotted grid line at 6.
                
                # Visual Mapping
                mapped_values = []
                for v in values:
                    if v > 5:
                        mapped_values.append(6) # Clamp to visual max
                    else:
                        mapped_values.append(v)
                
                fig = go.Figure(data=go.Scatterpolar(
                    r=mapped_values, 
                    theta=categories,
                    fill='toself',
                    name=title,
                    line_color=color
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 6], # Fixed Visual Max at 6
                            tickvals=[0, 1, 2, 3, 4, 5, 6],
                            ticktext=["", "", "", "", "", "5", "LB"], # Only label 5 and LB? Or just empty.
                            showticklabels=False,
                            gridcolor="rgba(0,0,0,0.1)" 
                        )),
                    showlegend=False,
                    margin=dict(l=30, r=30, t=30, b=30),
                    height=250,
                    title=dict(text=title, font=dict(size=14)),
                )
                
                # 1. Reference Line at 5 (Standard Max) - THICK Solid
                fig.add_trace(go.Scatterpolar(
                    r=[5] * len(categories),
                    theta=categories,
                    mode='lines',
                    line=dict(color='gray', width=3), # Bold line
                    hoverinfo='skip',
                    showlegend=False
                ))
                
                # 2. Outer Line at 6 (Limit Break) - Dotted
                # Previously dash='dot'. User asked for "Outer circumference as dotted line"
                fig.add_trace(go.Scatterpolar(
                    r=[6] * len(categories),
                    theta=categories,
                    mode='lines',
                    line=dict(color='gray', dash='dot', width=1), # Dotted line
                    hoverinfo='skip',
                    showlegend=False
                ))

                # Check for breakthrough
                is_broken = any(v > 5 for v in values)
                st.plotly_chart(fig, use_container_width=True)
                if is_broken:
                    st.caption(f"🌟 **{title}**: 限界突破 (MAX > 5) あり！")

            c_char1, c_char2 = st.columns(2)
            with c_char1:
                draw_radar("基礎能力", char.get('stats', {}), '#1E88E5')
            with c_char2:
                draw_radar("性格傾向", char.get('personality_stats', {}), '#E53935')

            st.divider()

            # Info Table (Striped)
            details = char.get('details', {})
            
            # Use smaller font for table to fit
            st.markdown("""
            <style>
            .info-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9em;
            }
            .info-table tr:nth-child(even) {
                background-color: #f5f5f5;
            }
            .info-table td {
                padding: 6px 10px;
                border: 1px solid #ddd;
            }
            .info-table td:first-child {
                font-weight: bold;
                background-color: #e8f5e9;
                width: 30%;
            }
            </style>
            """, unsafe_allow_html=True)


            # Utility to make color chip
            def color_chip(hex_code):
                if hex_code and hex_code.startswith('#') and len(hex_code) == 7:
                    # Width 24px (2x height)
                    return f'<span style="background-color: {hex_code}; display: inline-block; width: 24px; height: 12px; border: 1px solid #888; margin-right: 4px; vertical-align: middle;"></span>{hex_code}'
                return hex_code if hex_code else '-'

            table_html = f"""
            <table class="info-table">
                <tr><td>表記名</td><td>{char.get('name_en', '-')}</td></tr>
                <tr><td>年齢</td><td>{details.get('age', '-')}</td></tr>
                <tr><td>種族/職業</td><td>{details.get('role', '-')}</td></tr>
                <tr><td>出身/所属</td><td>{details.get('origin', '-')}</td></tr>
                <tr><td>身長/体重</td><td>{details.get('height_weight', '-')}</td></tr>
                <tr><td>容姿/外見</td><td>{details.get('appearance', '-')}</td></tr>
                <tr><td>目の色</td><td>{color_chip(details.get('eye_color'))}</td></tr>
                <tr><td>髪の色</td><td>{color_chip(details.get('hair_color'))}</td></tr>
                <tr><td>イメージカラー</td><td>{color_chip(details.get('image_color'))}</td></tr>
                <tr><td>性格</td><td>{details.get('personality', '-')}</td></tr>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Bio Display
            st.markdown("**詳細設定・経歴**")
            
            # Show Short Bio openly if exists
            if char.get('bio_short'):
                st.info(char['bio_short'], icon="📝")
            
            # Show Long Bio in expander
            raw_bio = char.get('bio', '')
            if raw_bio:
                with st.expander("詳細本文を見る", expanded=False):
                    st.write(raw_bio)
            
            # Moved URL here (was Appearance)
            if char.get('works_url'):
                st.markdown(f"**🔗 関連リンク**: [{char['works_url']}]({char['works_url']})")

            # Relations with Icons and Links
            st.subheader("🔗 人間関係")
            if char.get('relations'):
                for i, rel in enumerate(char['relations']):
                    target_id = rel['target_id']
                    target_char = manager.get_character(target_id)
                    
                    # Relation Row
                    r_c1, r_c2 = st.columns([1, 4])
                    with r_c1:
                         if target_char and target_char.get('images'):
                             st.image(target_char['images'][0], width=50) # Small icon
                    with r_c2:
                         if st.button(f"{rel['target_name']} ({rel['type']})", key=f"rel_{char['id']}_{i}"):
                             if target_char:
                                st.session_state.selected_char_id = target_char['id']
                                st.rerun()
                         st.caption(rel.get('desc', ''))
            else:
                st.caption("登録なし")
            
            st.divider()
            
            # Action Buttons at Bottom
            col_sns, col_edit = st.columns([2, 1])
            with col_sns:
                 if st.button("📱 SNS用カード画像を生成 (ZIP)"):
                    with st.spinner("生成中..."):
                        zip_data = generate_card_zip(char)
                        st.download_button("ダウンロード", zip_data, f"{char['name']}.zip", "application/zip")
            
            with col_edit:
                c_e1, c_e2 = st.columns(2)
                with c_e1:
                    if st.button("✏️ 修正"):
                        st.session_state.editing_char_id = char['id']
                        st.rerun()
                with c_e2:
                    if st.button("🗑️ 削除", type="primary"):
                        manager.delete_character(char['id'])
                        st.session_state.view_mode = 'list'
                        st.session_state.selected_char_id = None
                        st.success("削除しました")
                        time.sleep(1)
                        st.rerun()

def generate_card_zip(char):
    from PIL import Image, ImageDraw, ImageFont
    import io
    import zipfile
    import os

    # Load Fonts
    font_path = os.path.join("fonts", "NotoSansJP-Regular.otf")
    if not os.path.exists(font_path):
        # Fallback if font download failed or path is wrong
        font_path = "meiryo.ttc" 

    try:
        font_large = ImageFont.truetype(font_path, 40)
        font_medium = ImageFont.truetype(font_path, 24) 
        font_small = ImageFont.truetype(font_path, 18)
        font_romaji = ImageFont.truetype("arial.ttf", 22) # Keep Arial for Romaji or use Noto? Noto covers English too.
        # Let's use Noto for everything for consistency, or keep Arial if preferred. 
        # User asked for Noto JP specifically for "Japanese font".
        # I'll stick to Noto for JP parts.
    except:
        # Fallback system fonts
        try:
            font_large = ImageFont.truetype("meiryo.ttc", 40)
            font_medium = ImageFont.truetype("meiryo.ttc", 24)
            font_small = ImageFont.truetype("meiryo.ttc", 18)
            font_romaji = ImageFont.truetype("arial.ttf", 22)
        except:
             font_large = ImageFont.load_default()
             font_medium = ImageFont.load_default()
             font_small = ImageFont.load_default()
             font_romaji = ImageFont.load_default()

    # Load Background Texture
    # Hardcoded path for the generated texture. 
    # In real app, this should be in assets dir. 
    bg_path = r"C:\Users\sweet\.gemini\antigravity\brain\f632eb69-1385-4e0a-bf7b-2cc9ec5d7899\old_paper_texture_1767013103684.png"
    base_texture = None
    if os.path.exists(bg_path):
        try:
