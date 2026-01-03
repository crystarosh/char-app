import streamlit as st
import json
import os
import uuid
from PIL import Image
import plotly.graph_objects as go
import networkx as nx
import time
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image, ImageDraw, ImageFont
import re

def normalize_path(path):
    if not path: return None
    # Replace backslashes with forward slashes for cross-platform compatibility
    return path.replace("\\", "/")

def get_safe_image(img_path):
    if not img_path: return None
    norm_path = normalize_path(img_path)
    if os.path.exists(norm_path):
        return norm_path
    
    # If the exact path doesn't exist, try looking in 'images/' just in case
    # This helps if the DB says 'images\foo.jpg' but we are on Linux
    basename = os.path.basename(norm_path)
    alt_path = os.path.join("images", basename)
    if os.path.exists(alt_path):
        return alt_path
        
    return None

# --- Configuration ---
DATA_DIR = "data"
IMAGES_DIR = "images"
JSON_FILE = os.path.join(DATA_DIR, "characters.json")



# --- Data Management Class ---
class CharacterManager:
    def __init__(self):
        self._ensure_directories()
        self.use_gsheets = False
        self.gc = None
        self.sh = None
        self._connect_gsheets()
        self.characters = self.load_data()

    def _ensure_directories(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
        if not os.path.exists(JSON_FILE):
             with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _connect_gsheets(self):
        try:
            # Check if secrets exist
            if "gcp_service_account" in st.secrets:
                # Create credentials object manually from secrets dict
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds_dict = dict(st.secrets["gcp_service_account"])
                
                # Fix private key if it has escaped newlines (common issue in TOML)
                # Streamlit secrets usually handle this, but explicit fix is safe
                if "\\n" in creds_dict["private_key"]:
                    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                self.gc = gspread.authorize(creds)
                
                # Connect to Sheet
                sheet_name = "CharDB"
                self.sh = self.gc.open(sheet_name)
                self.use_gsheets = True
                print("Connected to Google Sheets")
            else:
                print("No Google Cloud secrets found. Using local JSON.")
        except Exception as e:
            print(f"Google Sheets connection failed: {e}")
            self.use_gsheets = False

    def load_data(self):
        if self.use_gsheets and self.sh:
            try:
                ws = self.sh.sheet1
                # Expecting Col A: ID, Col B: JSON String
                raw_data = ws.get_all_values()
                loaded_chars = []
                # Skip header if exists (Assume Row 1 is header if it says 'id')
                start_idx = 0
                if raw_data and raw_data[0] and raw_data[0][0] == 'id':
                    start_idx = 1
                
                for row in raw_data[start_idx:]:
                    if len(row) >= 2:
                        json_str = row[1]
                        if json_str:
                            try:
                                c_data = json.loads(json_str)
                                loaded_chars.append(c_data)
                            except:
                                pass
                return loaded_chars
            except Exception as e:
                print(f"Failed to load from Sheet: {e}")
                # Fallback to local
        
        # Local JSON Fallback (Primary if no sheets, Fallback if sheets error)
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_data(self):
        # 1. Save to Local JSON (Backup/Cache)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.characters, f, indent=4, ensure_ascii=False)
            
        # 2. Save to Google Sheets (Sync)
        if self.use_gsheets and self.sh:
            try:
                ws = self.sh.sheet1
                # Prepare data: Header + Rows
                data_rows = [['id', 'json_data']]
                for c in self.characters:
                    # Compact JSON for storage
                    j_str = json.dumps(c, ensure_ascii=False)
                    data_rows.append([c['id'], j_str])
                
                # Clear and Update
                ws.clear()
                ws.update('A1', data_rows) 
            except Exception as e:
                print(f"Failed to save to Sheet: {e}")
                st.error("Google Sheetsへの保存に失敗しました（ローカルのみ保存されました）")

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
            
        # Return logical path with forward slashes for DB consistency
        return file_path.replace("\\", "/")

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
                self.characters[i] = updated_data
                self.save_data()
                return True
        return False

# --- Security Helper (Global) ---
def verify_admin():
    # 1. Get Input
    pw_input = st.session_state.get("global_admin_pw", "")
    
    # 2. Get Secret (Deep Search)
    secret_pw = st.secrets.get("app_password")
    if not secret_pw:
        # Search in all top-level sections
        for key in st.secrets:
            val = st.secrets[key]
            # Check if it's a dict/AttrDict and contains app_password
            # Streamlit secrets are dict-like.
            try:
                if isinstance(val, (dict, type(st.secrets))) or hasattr(val, 'get'):
                    if "app_password" in val:
                         secret_pw = val["app_password"]
                         break
            except:
                pass

    # 3. Verify
    if not secret_pw:
        # Debug: Show available keys to help user
        keys_str = ", ".join(list(st.secrets.keys()))
        st.error(f"⚠️ 管理用パスワード(Secrets)が設定されていません。クラウド設定を確認してください。(検出されたキー: {keys_str})")
        return False
        
    if pw_input == secret_pw:
        return True
    
    st.error("パスワードが間違っています。")
    return False

# --- UI Functions (Placeholders) ---
def render_register_page(manager, edit_char_id=None):
    title = "新規キャラクター登録"
    existing_data = {}
    
    # Init session state for relations
    if 'reg_relations' not in st.session_state:
        st.session_state.reg_relations = []
    
    if edit_char_id:
        title = "キャラクター編集"
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

    # Security Input moved to Global (main)
    # verify_admin() available globally

    st.markdown(f"### <span style='color:#bbb'>⚜</span> {title}", unsafe_allow_html=True)
    sid = st.session_state.get("reg_form_key", "init")
    
    with st.container():
        user_name = st.text_input("ユーザー名 (PL名)", key=f"user_name_{sid}", value=existing_data.get('user_name', ''), placeholder="例: プレイヤーA")
        
        col_name1, col_name2, col_name3 = st.columns([2, 2, 2])
        
        with col_name1:
            first_name_in = st.text_input("名 (First Name)", key=f"first_name_{sid}", value=existing_data.get('first_name', existing_data.get('name', '')), placeholder="例: アーサー")
        with col_name2:
            last_name_in = st.text_input("姓 (Last Name)", key=f"last_name_{sid}", value=existing_data.get('last_name', ''), placeholder="例: ペンドラゴン")
        with col_name3:
            name_en_in = st.text_input("英語/ローマ字表記", key=f"name_en_{sid}", value=existing_data.get('name_en', ''), placeholder="例: Arthur Pendragon")
            
        full_name_combined = f"{last_name_in} {first_name_in}".strip()
        if not full_name_combined:
             full_name_combined = first_name_in 
             
        col1, col2 = st.columns(2)
        details = existing_data.get('details', {})
        
        with col1:
            race_opts = ["人間", "魔族", "聖族", "その他"]
            curr_race = details.get('race', '人間')
            if curr_race not in race_opts: curr_race = 'その他'
            race_in = st.selectbox("種族 (基本設定)", race_opts, index=race_opts.index(curr_race), key=f"race_{sid}")
            
            # --- Template Selection ---
            template_dir = "templates"
            valid_templates = []
            if os.path.exists(template_dir):
                # Filter for profile backgrounds (sim_profile_*)
                valid_templates = [f for f in os.listdir(template_dir) if f.startswith("sim_profile") and (f.endswith(".png") or f.endswith(".jpg"))]
                valid_templates.sort()
            
            if not valid_templates: 
                valid_templates = ["sim_profile_hum.png"]

            # Determine default based on current Race if no specific template is saved
            saved_tmpl = details.get('template_file')
            default_tmpl = saved_tmpl
            
            if not default_tmpl or default_tmpl not in valid_templates:
                # Fallback mapping
                race_map = {"人間": "sim_profile_hum.png", "魔族": "sim_profile_魔族.png", "聖族": "sim_profile_聖族.png"}
                default_tmpl = race_map.get(race_in, "sim_profile_hum.png")
                if default_tmpl not in valid_templates and valid_templates:
                    default_tmpl = valid_templates[0]

            tmpl_idx = 0
            if default_tmpl in valid_templates:
                tmpl_idx = valid_templates.index(default_tmpl)

            selected_template = st.selectbox("台紙テンプレート", valid_templates, index=tmpl_idx, key=f"tpl_sel_{sid}")
            
            # Preview Thumbnail
            tp_path = os.path.join(template_dir, selected_template)
            if os.path.exists(tp_path):
                st.image(tp_path, caption="選択中の台紙", width=150)

            role_in = st.text_input("職業 / 表示用種族名", key=f"role_{sid}", value=details.get('role', ''), placeholder="例: 騎士 / 混血の魔族")
            
            age = st.text_input("年齢", key=f"age_{sid}", value=details.get('age', ''), placeholder="例: 24歳")
            origin = st.text_input("出身 / 所属", key=f"origin_{sid}", value=details.get('origin', ''), placeholder="例: キャメロット")

        with col2:
            height_weight = st.text_input("身長 / 体重", key=f"hw_{sid}", value=details.get('height_weight', ''), placeholder="例: 180cm / 75kg")
            appearance = st.text_input("容姿 / 外見的特徴", key=f"app_{sid}", value=details.get('appearance', ''), placeholder="例: 金髪碧眼、右頬に傷")
             
             # --- Color Inputs ---
            def color_picker_callback(picker_key, text_key):
                if picker_key in st.session_state:
                     st.session_state[text_key] = st.session_state[picker_key]

            ec_col1, ec_col2 = st.columns([1, 4])
            with ec_col1:
                current_eye = details.get('eye_color', '#000000')
                if not current_eye.startswith('#') or len(current_eye) != 7: current_eye = '#000000'
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                st.color_picker("目", value=current_eye, key="picker_eye", label_visibility="collapsed", on_change=color_picker_callback, args=("picker_eye", "input_eye"))
            with ec_col2:
                eye_color = st.text_input("目の色", value=details.get('eye_color', ''), key="input_eye", placeholder="例: #FF0000")

            hc_col1, hc_col2 = st.columns([1, 4])
            with hc_col1:
                current_hair = details.get('hair_color', '#000000')
                if not current_hair.startswith('#') or len(current_hair) != 7: current_hair = '#000000'
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                st.color_picker("髪", value=current_hair, key="picker_hair", label_visibility="collapsed", on_change=color_picker_callback, args=("picker_hair", "input_hair"))
            with hc_col2:
                hair_color = st.text_input("髪の色", value=details.get('hair_color', ''), key="input_hair", placeholder="例: #000000")

            ic_col1, ic_col2 = st.columns([1, 4])
            with ic_col1:
                current_img = details.get('image_color', '#000000')
                if not current_img.startswith('#') or len(current_img) != 7: current_img = '#000000'
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                st.color_picker("イメージ", value=current_img, key="picker_img", label_visibility="collapsed", on_change=color_picker_callback, args=("picker_img", "input_img"))
            with ic_col2:
                image_color = st.text_input("イメージカラー", value=details.get('image_color', ''), key="input_img", placeholder="例: #123456")

            personality_text = st.text_input("性格（一言で）", value=details.get('personality', ''), placeholder="例: 正義感が強い、頑固")
            works_url = st.text_input("作品URL / 関連リンク", value=existing_data.get('works_url', ''))
    
        st.markdown("### <span style='color:#bbb'>⚜</span> 詳細設定", unsafe_allow_html=True)
    
    # RESTORED: Char Counts
    
    st.markdown("##### プロフィール画像用テキスト (Card 1)")
    st.caption("Card 1 (Profile) の下部ベージュエリアに表示されるテキストです。約150文字程度推奨。")
    memo_val = details.get('memo', '')
    memo_in = st.text_area("プロフィール用簡易設定", value=memo_val, height=100, key="memo_input_area")
    st.caption(f"現在の文字数: {len(memo_in)} 文字")

    st.markdown("##### SNS用（短文） (Card 2)")
    st.caption("Card 2 (Stats) 右下のエリアに表示されるテキストです。約250文字以内で入力してください。")
    bio_short_val = existing_data.get('bio_short', '')
    bio_short = st.text_area("SNS用短文", value=bio_short_val, height=150, max_chars=250, key="bio_short_input")
    st.caption(f"現在の文字数: {len(bio_short)} 文字")
    
    st.markdown("##### 詳細用（長文） (Web詳細)")
    st.caption("Webの詳細画面で表示される全文です。画像には使用されません。")
    bio_long_val = existing_data.get('bio', '')
    bio_in = st.text_area("詳細設定・裏設定など", value=bio_long_val, height=300, key="bio_input_area")
    st.caption(f"現在の文字数: {len(bio_in)} 文字")
    st.markdown("### <span style='color:#bbb'>⚜</span> 基礎ステータス", unsafe_allow_html=True)
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
    
    st.markdown("### <span style='color:#bbb'>⚜</span> 性格ステータス", unsafe_allow_html=True)
    labels_personality = ["積極性", "協調性", "慎重さ", "適応力", "精神力", "寛容さ", "道徳・倫理観", "社交性"]
    stats_pers_data = existing_data.get('personality_stats', {})
    new_stats_pers = {}
    
    cols_pers = st.columns(4)
    for i, label in enumerate(labels_personality):
        with cols_pers[i % 4]:
            new_stats_pers[label] = st.slider(label, 1, 5, int(stats_pers_data.get(label, 3)))

    st.markdown("### <span style='color:#bbb'>⚜</span> 画像", unsafe_allow_html=True)
    current_images = existing_data.get('images', []) if edit_char_id else []

    with st.expander("ℹ️ 推奨プロフィール画像のサイズについて"):
        st.markdown("""
        **プロフィール用 全身画像 (Image 2)**
        - **推奨最小サイズ**: 320 x 520 px
        - **推奨比率**: 1 : 1.6 (横幅の1.6倍の高さ)
        - **表示仕様**: 横方向は中央、縦方向は上から20%の位置を中心にトリミングされます。
        
        **ギャラリー用 縦長画像 (Image 2共用)**
        - **推奨最小サイズ**: 288 x 596 px
        - **推奨比率**: 1 : 2.07 (約1:2 - 横幅の2倍の高さ)
        
        **💡 ヒント**: 
        画像2（全身画像）には、**横幅の約2倍の高さがある縦長画像**を使用すると、プロフィールカードとギャラリーの両方で綺麗に収まります。
        """)
    
    # helper to get path safely
    def get_cur(idx):
        if idx < len(current_images): return current_images[idx]
        return None

    img_col1, img_col2 = st.columns(2)
    u1, u2, u3, u4, u5, u6 = None, None, None, None, None, None
    d1, d2, d3, d4, d5, d6 = False, False, False, False, False, False
    
    with img_col1:
        st.markdown("**画像1 (Profile)** <span style='color:red; font-size:0.8em'>(必須)</span>", unsafe_allow_html=True)
        # Safe Image Load
        p1 = get_safe_image(get_cur(0))
        if p1: 
            st.image(p1, width=100)
            d1 = st.checkbox("画像1を削除", key=f"del_img_1_{sid}")
        u1 = st.file_uploader("上書き/新規 (No.1)", type=["png", "jpg"], key=f"u1_{sid}")
        
        st.markdown("**画像3 (Gallery A)**")
        p3 = get_safe_image(get_cur(2))
        if p3: 
            st.image(p3, width=100)
            d3 = st.checkbox("画像3を削除", key=f"del_img_3_{sid}")
        u3 = st.file_uploader("上書き/新規 (No.3)", type=["png", "jpg"], key=f"u3_{sid}")
        
        st.markdown("**画像5 (Gallery C)**")
        p5 = get_safe_image(get_cur(4))
        if p5: 
            st.image(p5, width=100)
            d5 = st.checkbox("画像5を削除", key=f"del_img_5_{sid}")
        u5 = st.file_uploader("上書き/新規 (No.5)", type=["png", "jpg"], key=f"u5_{sid}")

    with img_col2:
        st.markdown("**画像2 (Full Body)** <span style='color:red; font-size:0.8em'>(必須)</span>", unsafe_allow_html=True)
        p2 = get_safe_image(get_cur(1))
        if p2: 
            st.image(p2, width=100)
            d2 = st.checkbox("画像2を削除", key=f"del_img_2_{sid}")
        u2 = st.file_uploader("上書き/新規 (No.2)", type=["png", "jpg"], key=f"u2_{sid}")
        
        st.markdown("**画像4 (Gallery B)**")
        p4 = get_safe_image(get_cur(3))
        if p4: 
            st.image(p4, width=100)
            d4 = st.checkbox("画像4を削除", key=f"del_img_4_{sid}")
        u4 = st.file_uploader("上書き/新規 (No.4)", type=["png", "jpg"], key=f"u4_{sid}")

        st.markdown("**画像6 (Gallery D)**")
        p6 = get_safe_image(get_cur(5))
        if p6: 
            st.image(p6, width=100)
            d6 = st.checkbox("画像6を削除", key=f"del_img_6_{sid}")
        u6 = st.file_uploader("上書き/新規 (No.6)", type=["png", "jpg"], key=f"u6_{sid}")

    st.markdown("---")
    st.markdown("### <span style='color:#bbb'>⚜</span> 人間関係", unsafe_allow_html=True)
    
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
        if not verify_admin():
            return
            
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
                "template_file": selected_template,
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

                # FIX: Ensure order is [u1, u2, u3, u4, u5] AND Handle Deletion
        ordered_uploads = [u1, u2, u3, u4, u5, u6]
        ordered_deletes = [d1, d2, d3, d4, d5, d6]
        
        updated_paths = []
        for i in range(6): 
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

    # --- DELETE BUTTON ---
    if edit_char_id:
        st.markdown("---")
        col_del_1, col_del_2 = st.columns([1, 4])
        with col_del_1:
             # Delete Logic
             if st.checkbox("削除モード", key="enable_del"):
                 if st.button("このキャラクターを削除", type="primary"):
                     if verify_admin():
                         manager.delete_character(edit_char_id)
                         st.success("削除しました！")
                         time.sleep(1)
                         st.session_state.editing_char_id = None
                         st.session_state.view_mode = 'list'
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

    # Security Input moved to Global (main)

    # --- LIST MODE ---
    if st.session_state.view_mode == 'list':
        
        st.markdown("# The Legend of Crystarosh Characters List")

        
        tab_card, tab_text = st.tabs(["🖼️ カード表示", "📋 データベース表示"])
        
        # --- TAB 1: CARD VIEW ---
        with tab_card:
            # [Duplicate CSS Removed]
            
            if not manager.characters:
                st.info("キャラクターが登録されていません。")
            else:
                cols = st.columns(5)
                for i, char in enumerate(manager.characters):
                    with cols[i % 5]:
                         raw_img_path = char['images'][0] if (char['images'] and char['images'][0]) else None
                         target_img = get_safe_image(raw_img_path)
                         
                         if target_img:
                             try:
                                 from PIL import Image as PILImage
                                 # Open and resize for icon
                                 img_obj = PILImage.open(target_img)
                                 # Crop to square center
                                 w, h = img_obj.size
                                 min_dim = min(w, h)
                                 left = (w - min_dim)/2
                                 top = (h - min_dim)/2
                                 img_obj = img_obj.crop((left, top, left+min_dim, top+min_dim))
                                 st.image(img_obj, use_container_width=True)
                             except:
                                 st.empty() # Fail silently on corrupt image
                         else:
                             # Placeholder
                             st.markdown(f"""
                             <div style='background-color:#ccc; height:100px; display:flex; align-items:center; justify-content:center; color:#666;'>
                             No Image
                             </div>
                             """, unsafe_allow_html=True)
                             
                         disp_name = char.get('first_name', char['name'])
                         if st.button(disp_name, key=f"sel_{char['id']}", use_container_width=True):
                             st.session_state.selected_char_id = char['id']
                             st.session_state.view_mode = 'detail'
                             st.rerun()

        # --- TAB 2: TEXT DATABASE VIEW ---
        with tab_text:
            if not manager.characters:
                st.info("データがありません")
            else:
                # 1. Search & Sort Controls
                c_search, c_sort, c_order = st.columns([3, 1, 1])
                with c_search:
                    search_q = st.text_input("🔍 キーワード検索 (名前, 種族, 所属など)", placeholder="検索ワードを入力...")
                with c_sort:
                    sort_key = st.selectbox("並べ替え項目", ["名前 (Name)", "種族 (Role)", "年齢 (Age)", "所属 (Origin)", "身長 (Height)"])
                with c_order:
                    sort_order = st.selectbox("順序", ["昇順 (ASC)", "降順 (DESC)"])
                
                # 2. Filter Logic
                filtered_chars = []
                for char in manager.characters:
                    # Search target string
                    details = char.get('details', {})
                    search_str = f"{char['name']} {char.get('first_name','')} {char.get('last_name','')} {char.get('name_en','')} {details.get('role','')} {details.get('origin','')} {details.get('age','')} {details.get('personality','')}"
                    
                    if not search_q or (search_q.lower() in search_str.lower()):
                        filtered_chars.append(char)
                
                # 3. Sort Logic
                reverse = True if "DESC" in sort_order else False
                
                def get_sort_val(c):
                    d = c.get('details', {})
                    if "名前" in sort_key: return c['name']
                    if "種族" in sort_key: return d.get('role', '')
                    if "年齢" in sort_key: 
                        # Try to parse int for correct sorting? simple string sort for now.
                        return d.get('age', '')
                    if "所属" in sort_key: return d.get('origin', '')
                    if "身長" in sort_key: return d.get('height_weight', '')
                    return c['name']
                
                filtered_chars.sort(key=get_sort_val, reverse=reverse)
                
                # 4. Table Header
                st.markdown("---")
                h_name, h_role, h_orig, h_age, h_act = st.columns([3, 2, 2, 1, 1])
                h_name.markdown("**名前 / Name**")
                h_role.markdown("**種族・職業**")
                h_orig.markdown("**所属**")
                h_age.markdown("**年齢**")
                h_act.markdown("**操作**")
                st.markdown("---")
                
                # 5. Render Rows
                for char in filtered_chars:
                    details = char.get('details', {})
                    
                    # Row Layout
                    # Use container for hover effect? Streamlit native doesn't support hover well.
                    # Just flat design.
                    
                    bg_style = "" # Could alternate colors if loop index used
                    
                    r_name, r_role, r_orig, r_age, r_act = st.columns([3, 2, 2, 1, 1])
                    
                    if char.get('first_name') and char.get('last_name'):
                        base_name = f"{char['first_name']}・{char['last_name']}"
                    else:
                        base_name = char['name']
                    name_disp = base_name
                    if char.get('name_en'):
                        name_disp += f" <br><span style='color:gray; font-size:0.8em'>{char['name_en']}</span>"
                    
                    r_name.markdown(name_disp, unsafe_allow_html=True)
                    r_role.write(details.get('role', '-'))
                    r_orig.write(details.get('origin', '-'))
                    r_age.write(details.get('age', '-'))
                    
                    if r_act.button("詳細", key=f"tbl_btn_{char['id']}"):
                        st.session_state.selected_char_id = char['id']
                        st.session_state.view_mode = 'detail'
                        st.rerun()
                    
                    st.markdown("<hr style='margin: 5px 0; border-top: 1px dashed #ddd;'>", unsafe_allow_html=True)

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
            main_img_path = get_safe_image(char['images'][0] if (char['images'] and char['images'][0]) else None)
            if main_img_path:
                st.image(main_img_path, use_container_width=True)
            else:
                 st.info("画像が見つかりません (クラウド上では画像は一時ファイルのため消えることがあります)")

            # Sub Images Gallery with Viewer Mode
            if len(char['images']) > 1:
                st.markdown("##### <span style='color:#bbb'>⚜</span> ギャラリー", unsafe_allow_html=True)
                cols_sub = st.columns(3)
                for i, raw_path in enumerate(char['images'][1:]):
                    img_path = get_safe_image(raw_path)
                    with cols_sub[i % 3]:
                        # Make thumbnail clickable to simple expander?
                        # Streamlit image click -> fullscreen is default.
                        # User wants "Popup" but "Don't get stuck".
                        # If we use `st.button` with image as label? No.
                        # We can use a button "🔍" under each image to open a modal-like view.
                        if img_path:
                            st.image(img_path, use_container_width=True)
                            if st.button("拡大", key=f"view_{i}"):
                                st.session_state.view_mode = 'image_view'
                                st.session_state.view_img_path = img_path
                                st.rerun()
                        else:
                             st.markdown("<div style='font-size:0.8em; color:#999'>No Img</div>", unsafe_allow_html=True)

        with col_info:
            # Basic Stats
            st.markdown("### <span style='color:#bbb'>⚜</span> ステータス", unsafe_allow_html=True)

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
            
            
            # SHOW MEMO (Profile Text)
            memo_txt = details.get('memo', '')
            if memo_txt:
                with st.expander('プロフィール画像用テキストを確認', expanded=False):
                    st.markdown(f'<div style="background-color: #2c2c2c; color: #e0e0e0; padding: 10px; border-radius: 5px; border: 1px solid #555;">{memo_txt}</div>', unsafe_allow_html=True)
                    st.caption(f'{len(memo_txt)}文字')
            
# Show Short Bio openly if exists
            if char.get('bio_short'):
                st.markdown(f'<div style="background-color: #2c2c2c; color: #e0e0e0; padding: 10px; border-radius: 5px; border: 1px solid #555;">{char["bio_short"]}</div>', unsafe_allow_html=True)
            
            # Show Long Bio in expander
            raw_bio = char.get('bio', '')
            if raw_bio:
                with st.expander("詳細本文を見る", expanded=False):
                    st.write(raw_bio)
            
            # Moved URL here (was Appearance)
            if char.get('works_url'):
                st.markdown(f"**🔗 関連リンク**: [{char['works_url']}]({char['works_url']})")

            # Relations with Icons and Links
            st.markdown("### <span style='color:#bbb'>⚜</span> 人間関係", unsafe_allow_html=True)
            if char.get('relations'):
                for i, rel in enumerate(char['relations']):
                    target_id = rel['target_id']
                    target_char = manager.get_character(target_id)
                    
                    # Relation Row
                    r_c1, r_c2 = st.columns([1, 4])
                    with r_c1:
                         if target_char and target_char.get('images'):
                             t_img_path = get_safe_image(target_char['images'][0])
                             if t_img_path:
                                 st.image(t_img_path, width=50) # Small icon
                             else:
                                 st.markdown("👤")
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
                    if verify_admin():
                        with st.spinner("生成中..."):
                            zip_data = generate_card_zip(char, manager)
                            st.download_button("ダウンロード", zip_data, f"{char['name']}.zip", "application/zip")
            
            with col_edit:
                c_e1, c_e2 = st.columns(2)
                with c_e1:
                    if st.button("✏️ 修正"):
                        if verify_admin():
                            st.session_state.editing_char_id = char['id']
                            st.rerun()
                with c_e2:
                    if st.button("🗑️ 削除"):
                        if verify_admin():
                            manager.delete_character(char['id'])
                            st.session_state.view_mode = 'list'
                            st.session_state.selected_char_id = None
                            st.success("削除しました")
                            time.sleep(1)
                            st.rerun()


def generate_card_zip(char, manager):
    import io
    import zipfile
    import os
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
    import math
    import string

    # --- V33 RADAR VISUAL MATCH (Grid on Top, Darker Lines, Bold Frame) ---
    print(f"DEBUG: V33 - {char.get('name')}")

    CANVAS_1 = (1024, 1024)
    CANVAS_LANDSCAPE = (1024, 768)
    
    FONT_PATH = "fonts/NotoSansJP-Regular.otf"
    TEXTURE_PATH = "C:/Users/sweet/.gemini/antigravity/brain/f632eb69-1385-4e0a-bf7b-2cc9ec5d7899/old_paper_texture_1767013103684.png"
    CORNER_PATH = "C:/Users/sweet/.gemini/antigravity/brain/f632eb69-1385-4e0a-bf7b-2cc9ec5d7899/victorian_corner_1767013906098.png"

    def get_font(size):
        try:
            return ImageFont.truetype(FONT_PATH, int(size))
        except:
            return ImageFont.load_default()

    f_small = get_font(24)
    f_med = get_font(30)
    f_large = get_font(50)
    f_romaji = get_font(40)

    def draw_text(draw, text, position, font, fill, anchor="la"):
        if text:
            try:
                draw.text(position, text, font=font, fill=fill, anchor=anchor)
            except:
                pass

    def draw_text_wrapped(draw, text, x, y, max_h, max_w, font, fill, align="left", valign="top", dry_run=False):
        if not text: return 0 if dry_run else y
        lines = []
        for line in text.splitlines():
            current = ""
            for c in line:
                try:
                    w = draw.textlength(current + c, font=font)
                except:
                    w = len(current + c) * font.size
                if w > max_w:
                    lines.append(current)
                    current = c
                else:
                    current += c
            if current: lines.append(current)
            
        line_height = int(font.size * 1.5)
        total_h = len(lines) * line_height
        
        if dry_run: return total_h
        
        start_y = y
        if valign == "center":
            start_y = y + (max_h - total_h) // 2
        
        current_y = start_y
        for l in lines:
            draw.text((x, current_y), l, font=font, fill=fill)
            current_y += line_height
        return current_y

    def load_image_masked(path, size, radius=0, centering=(0.5, 0.5)):
        try:
            img = Image.open(path).convert("RGBA")
            img = ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=centering)
            if radius > 0:
                mask = Image.new("L", size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
                ret = Image.new("RGBA", size, (0,0,0,0))
                ret.paste(img, (0,0), mask=mask)
                return ret
            return img
        except:
            ph = Image.new('RGBA', size, (200, 200, 200, 255))
            d = ImageDraw.Draw(ph)
            d.text((size[0]//2, size[1]//2), "No Img", fill="gray", anchor="mm", font=f_small)
            return ph

    def inputs_paste_shadowed_strict(base_img, fg_img, xy, blur=7, offset=(0,0), alpha_val=130):
        if not fg_img: return
        
        alpha = fg_img.split()[-1]
        w, h = fg_img.size
        
        margin = blur * 3
        sw, sh = w + margin*2, h + margin*2
        shadow_layer = Image.new("RGBA", (sw, sh), (0,0,0,0))
        
        silhouette = Image.new("RGBA", (w, h), (0,0,0,alpha_val)) 
        silhouette.putalpha(alpha.point(lambda p: alpha_val if p > 0 else 0)) 
        
        shadow_layer.paste(silhouette, (margin, margin))
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur))
        
        sx = xy[0] - margin + offset[0]
        sy = xy[1] - margin + offset[1]
        
        base_img.alpha_composite(shadow_layer, (int(sx), int(sy)))
        base_img.alpha_composite(fg_img, xy)

    def draw_shadowed_rounded_image(base_img, img_path, box, radius=20, blur=10, shadow_offset=(5, 5), centering=(0.5, 0.5)):
        x, y, w, h = box
        try:
            src = Image.open(img_path).convert("RGBA")
        except:
            if not img_path: return 
            src = Image.new('RGBA', (w, h), (200, 200, 200, 0))
            
        src = ImageOps.fit(src, (w, h), method=Image.Resampling.LANCZOS, centering=centering)
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
        
        margin = blur + 10
        sw, sh = w + margin*2, h + margin*2
        shadow = Image.new("RGBA", (sw, sh), (0,0,0,0))
        sdraw = ImageDraw.Draw(shadow)
        sdraw.rounded_rectangle((margin, margin, margin+w, margin+h), radius=radius, fill=(0, 0, 0, 150)) 
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
        
        sx = x - margin + shadow_offset[0]
        sy = y - margin + shadow_offset[1]
        base_img.paste(shadow, (sx, sy), shadow)
        base_img.paste(src, (x, y), mask=mask)
        
    def draw_radar(base_img, center, radius, stats, labels, color_fill, color_line):
        S = 4
        w, h = base_img.size
        size = int(radius * 2.5 * S)
        c_rel = (size // 2, size // 2)
        r_sc = radius * S
        
        poly_layer = Image.new("RGBA", (size, size), (0,0,0,0))
        draw_p = ImageDraw.Draw(poly_layer)
        
        n = len(labels)
        angle_step = 2 * math.pi / n
        start_angle = -math.pi / 2

        # Draw Filled Polygon FIRST (on poly layer)
        # Using Alpha 80 from V32 (approx 30%)
        
        vals = [int(stats.get(l, 3)) for l in labels]
        pts = []
        for j in range(n):
            v = min(vals[j], 5)
            r = r_sc * (v/5)
            if v > 5: r = r_sc * (6/5)
            ang = start_angle + j * angle_step
            pts.append((c_rel[0] + r*math.cos(ang), c_rel[1] + r*math.sin(ang)))
            
        if len(pts) > 2:
            draw_p.polygon(pts, fill=color_fill) 
            draw_p.polygon(pts, outline=color_line, width=2*S)
            
        # Paste Filled Polygon onto base_img
        target_size = int(radius * 2.5)
        res = poly_layer.resize((target_size, target_size), resample=Image.Resampling.LANCZOS)
        
        paste_x = center[0] - target_size // 2
        paste_y = center[1] - target_size // 2
        base_img.alpha_composite(res, (paste_x, paste_y))
        
        # V33: Draw Grid Lines ON TOP of Base Image
        # Darker Gray (#666666) to ensure visibility
        # Thicker "5" Frame to emulate Plotly style
        draw = ImageDraw.Draw(base_img)
        
        for i in range(1, 6):
            r = radius * (i/5)
            pts_g = []
            for j in range(n):
                ang = start_angle + j * angle_step
                pts_g.append((center[0] + r*math.cos(ang), center[1] + r*math.sin(ang)))
            
            # Special Bold Frame at 5
            if i == 5:
                draw.polygon(pts_g, outline="#666666", width=2)
            else:
                draw.polygon(pts_g, outline="#888888", width=1)

        # Spokes
        for j in range(n):
            ang = start_angle + j * angle_step
            end = (center[0] + radius*math.cos(ang), center[1] + radius*math.sin(ang))
            draw.line([center, end], fill="#888888", width=1)
        
        # Labels
        for j in range(n):
            ang = start_angle + j * angle_step
            lx = center[0] + (radius+30)*math.cos(ang)
            ly = center[1] + (radius+30)*math.sin(ang)
            anchor = "mm"
            if math.cos(ang) > 0.2: anchor="lm"
            elif math.cos(ang) < -0.2: anchor="rm"
            draw.text((lx, ly), labels[j], fill="#333", font=get_font(20), anchor=anchor)

    def make_transparent(img):
        datas = img.getdata()
        new_data = []
        for item in datas:
            if item[0] > 230 and item[1] > 230 and item[2] > 230:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        return img

    def draw_decorations(draw, w, h):
        if os.path.exists(CORNER_PATH):
            try:
                corner = Image.open(CORNER_PATH).convert("RGBA").resize((150, 150))
                corner = make_transparent(corner)
                tl = corner.transpose(Image.FLIP_LEFT_RIGHT)
                draw._image.paste(tl, (0, 0), tl)
                draw._image.paste(corner, (w-150, 0), corner)
                bl = corner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
                draw._image.paste(bl, (0, h-150), bl)
                br = corner.transpose(Image.FLIP_TOP_BOTTOM)
                draw._image.paste(br, (w-150, h-150), br)
            except:
                pass
        draw.rectangle((40, 40, w-40, h-40), outline="#5d4037", width=2)

    # --- 1. PROFILE CARD (V33 - Keep margins 50) ---
    def create_card_1():
        print(f"DEBUG: Creating Card 1 for {char.get('name')}")
        details = char.get('details', {})
        race = details.get('race', '人間')
        
        custom_tmpl = details.get('template_file')
        if custom_tmpl and os.path.exists(os.path.join("templates", custom_tmpl)):
             t_file = custom_tmpl
        else:
             # Fallback to Race Standard
             template_map = {
                "人間": "sim_profile_hum.png",
                "魔族": "sim_profile_魔族.png",
                "聖族": "sim_profile_聖族.png",
                "その他": "sim_profile_hum.png"
             }
             t_file = template_map.get(race, "sim_profile_hum.png")
        
        # Determine Text Color based on Template
        # Demon templates (Dark BG) -> White Text
        # Human/Saint/Elf/Others (Light BG) -> Dark Text (#333333)
        if "魔族" in t_file:
            txt_col = "#FFFFFF"
        else:
            txt_col = "#333333"
            
        memo_col = "#333333" # Memo area is always beige/light
        
        t_path = os.path.join("templates", t_file)
        if os.path.exists(t_path):
            img = Image.open(t_path).convert("RGBA").resize(CANVAS_1)
        else:
            img = Image.new("RGBA", CANVAS_1, (255, 255, 255, 255))
        
        # V31 Margins (50px side)
        margin_x = 50
        area_w = 1024 - (margin_x*2) # 924
        area_right = 1024 - margin_x # 974
        
        img1_box = (125, 107, 360, 360)
        
        im2_w = 320
        im2_x = area_right - im2_w
        
        img2_box = (im2_x, 107, im2_w, 520)
        
        if len(char['images']) > 0:
            if char['images'][0] and os.path.exists(char['images'][0]):
                draw_shadowed_rounded_image(img, char['images'][0], img1_box, radius=20)
        if len(char['images']) > 1:
             if char['images'][1] and os.path.exists(char['images'][1]):
                draw_shadowed_rounded_image(img, char['images'][1], img2_box, radius=20, centering=(0.5, 0.2))
            
        draw = ImageDraw.Draw(img)
        lx = 125
        ly = 492
        
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname}・{lname}" if fname and lname else char.get('name', '')
        
        font_lbl = get_font(16)
        font_val = get_font(22)
        font_name = get_font(30)
        font_code = get_font(14)
        
        draw.text((lx, ly), "Name:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly-5), full, font=font_name, fill=txt_col, anchor="la")
        ly += 50
        
        draw.text((lx, ly), "Age:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly), details.get('age', '-'), font=font_val, fill=txt_col, anchor="la")
        ly += 40
        
        draw.text((lx, ly), "Class:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly), details.get('role', '-'), font=font_val, fill=txt_col, anchor="la")
        ly += 40
        
        draw.text((lx, ly), "H/W:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly), details.get('height_weight', '-'), font=font_val, fill=txt_col, anchor="la")
        ly += 40
        
        draw.text((lx, ly), "Affil:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly), details.get('origin', '-'), font=font_val, fill=txt_col, anchor="la")
        
        cx = 564
        cy = 180
        step_y = 65
        
        draw.text((cx, cy), "Race", font=font_lbl, fill=txt_col, anchor="mm")
        draw.text((cx, cy+25), race, font=font_val, fill=txt_col, anchor="mm")
        cy += step_y
        
        def draw_color_row(label, hex_val, y_pos):
             draw.text((cx, y_pos), label, font=font_lbl, fill=txt_col, anchor="mm")
             start_x = cx - 50
             if hex_val.startswith('#'):
                  draw.rectangle((start_x, y_pos+20, start_x+30, y_pos+45), fill=hex_val, outline="black")
                  draw.text((start_x+40, y_pos+32), hex_val, font=font_code, fill=txt_col, anchor="lm")
             else:
                  draw.text((cx, y_pos+32), hex_val, font=font_val, fill=txt_col, anchor="mm")

        draw_color_row("Eye", details.get('eye_color', '-'), cy)
        cy += step_y
        
        draw_color_row("Hair", details.get('hair_color', '-'), cy)
        cy += step_y
        
        draw_color_row("Image Color", details.get('image_color', '-'), cy)

        un = char.get('user_name', '')
        if un: 
             draw.text((820, 40), f"{un}", font=get_font(24), fill=txt_col, anchor="la")
             
        memo_x = margin_x
        memo_y = 750
        
        title_font = get_font(20)
        body_font = get_font(18)
        
        title_text = "【簡易設定】"
        int_pad = 40
        text_x = memo_x + int_pad
        text_w = area_w - (int_pad*2)
        
        draw.text((text_x, memo_y), title_text, font=title_font, fill=memo_col, anchor="la")
        draw_text_wrapped(draw, details.get('memo', ''), text_x, memo_y+35, 9999, text_w, body_font, memo_col, valign="top")
        
        return img

    # --- 2. STATS CARD (V33 - Grid on Top, Darker) ---
    def create_card_2():
        print("DEBUG: Creating Card 2 (V33)")
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
        draw = ImageDraw.Draw(bg)
        
        draw_decorations(draw, 1024, 768)
        
        un = char.get('user_name', '')
        if un: draw.text((512, 25), f"User: {un}", font=f_small, fill="gray", anchor="mm")
        
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname}・{lname}" if fname and lname else char.get('name', '')
        draw.text((512, 60), full, font=f_med, fill="#3e2723", anchor="mm")
        
        chart_y = 330 
        chart_r = 110 
        
        lbl_b = ["知力", "体力", "魔力", "防御力", "行動力", "攻撃力", "自信"]
        draw.text((256, 120), "基礎能力", font=f_med, fill="#3e2723", anchor="mm") 
        # V33: Alpha 80 (V32 value)
        draw_radar(bg, (256, chart_y), chart_r, char.get('stats', {}), lbl_b, (30, 136, 229, 80), (30, 136, 229, 255))
        
        lbl_p = ["積極性", "協調性", "慎重さ", "適応力", "精神力", "寛容さ", "道徳・倫理観", "社交性"]
        draw.text((768, 120), "性格傾向", font=f_med, fill="#3e2723", anchor="mm")
        draw_radar(bg, (768, chart_y), chart_r, char.get('personality_stats', {}), lbl_p, (229, 57, 53, 80), (229, 57, 53, 255))
        
        dx = 130
        dy = 500
        draw.text((dx, dy), "【詳細概要】", font=f_med, fill="#3e2723") 
        bio = char.get('bio_short', '') or char.get('bio', '')[:250]
        
        max_w = 1024 - (dx * 2) 
        draw_text_wrapped(draw, bio, dx, dy+45, 200, max_w, get_font(16), "#212121")
        
        draw.text((512, 750), "Legend of Crystarosh", font=get_font(12), fill="#5d4037", anchor="mm")
        
        return bg

    # --- 3. GALLERY CARD (V33 - Keep V31 Layout) ---
    def create_card_3():
        print("DEBUG: Creating Card 3 (V33)")
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
            
        imgs = char.get('images', [])
        def gv(i): return imgs[i] if i<len(imgs) and imgs[i] and os.path.exists(imgs[i]) else None
        p2, p3, p4, p5 = gv(2), gv(3), gv(5), gv(4)
        
        y_start = 100
        w = 288
        h_sq = 288 
        h_tall = 288 * 2 + 20 
        gap = 20
        R = 25
        
        sh_off = (4, 4)
        sh_blur = 7
        sh_alpha = 130
        
        if p2:
             i = load_image_masked(p2, (w, h_tall), radius=R, centering=(0.5, 0.5))
             inputs_paste_shadowed_strict(bg, i, (60, y_start), blur=sh_blur, offset=sh_off, alpha_val=sh_alpha)
             
        if p3:
             i = load_image_masked(p3, (w, h_sq), radius=R)
             inputs_paste_shadowed_strict(bg, i, (368, y_start), blur=sh_blur, offset=sh_off, alpha_val=sh_alpha)
             
        if p4:
             i = load_image_masked(p4, (w, h_sq), radius=R)
             inputs_paste_shadowed_strict(bg, i, (676, y_start), blur=sh_blur, offset=sh_off, alpha_val=sh_alpha)
             
        y_bot = y_start + h_sq + gap 
        if p5:
             i = load_image_masked(p5, (w, h_sq), radius=R)
             inputs_paste_shadowed_strict(bg, i, (368, y_bot), blur=sh_blur, offset=sh_off, alpha_val=sh_alpha)
        
        rel_x = 676
        rel_y = 408 
        
        draw = ImageDraw.Draw(bg)
        draw_decorations(draw, 1024, 768)
        
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname}・{lname}" if fname and lname else char.get('name', '')
        draw.text((512, 80), full, font=get_font(21), fill="#3e2723", anchor="mm")

        en = char.get('name_en', '')
        if en: draw.text((512, 55), en, font=get_font(21), fill="#3e2723", anchor="mm")
        
        draw.text((rel_x + w//2, rel_y), "【人間関係】", font=get_font(24), fill="#3e2723", anchor="mt") 
        
        rels = char.get('relations', [])[:4]
        
        list_y = rel_y + 40
        
        for i, r in enumerate(rels):
             col = i % 2
             row = i // 2
             bx = rel_x + col * 144
             by = list_y + row * 144
             
             rtype = r.get('type', '').split('/')[0]
             draw.text((bx+72, by+20), rtype, font=get_font(14), fill="#5d4037", anchor="mm")
             
             tid = r.get('target_id')
             all_chars = {c['id']: c for c in manager.characters}
             tgt = all_chars.get(tid)
             
             ic_sz = 60
             ic = None
             if tgt and tgt.get('images'):
                 ic = load_image_masked(tgt['images'][0], (ic_sz, ic_sz), radius=10)
             else:
                 ic = Image.new("RGBA", (ic_sz, ic_sz), (220, 220, 220, 255))
             
             bg.paste(ic, (bx+42, by+40), ic)
             
             if tgt: tname = tgt.get('first_name', tgt.get('name', ''))
             elif r.get('target_name'): tname = r.get('target_name', '')
             else: tname = "?"
             tname = tname.split()[0]
             
             draw.text((bx+72, by+115), tname, font=get_font(16), fill="#3e2723", anchor="mm")

        draw.text((512, 750), "Legend of Crystarosh", font=get_font(12), fill="#5d4037", anchor="mm")
            
        return bg

    # --- Debug Mode Maintained ---
    i1 = create_card_1()
    i2 = create_card_2()
    i3 = create_card_3()
    
    b = io.BytesIO()
    with zipfile.ZipFile(b, "a", zipfile.ZIP_DEFLATED, False) as z:
        safe_name = "".join([c for c in char['name'] if c.isalnum() or c in (' ','_','-')]).strip()
        if not safe_name: safe_name = "card_images"
        bu = io.BytesIO(); i1.convert("RGB").save(bu, "JPEG"); z.writestr(f"{safe_name}_profile.jpg", bu.getvalue())
        bu2 = io.BytesIO(); i2.convert("RGB").save(bu2, "JPEG"); z.writestr(f"{safe_name}_stats.jpg", bu2.getvalue())
        bu3 = io.BytesIO(); i3.convert("RGB").save(bu3, "JPEG"); z.writestr(f"{safe_name}_gallery.jpg", bu3.getvalue())
    b.seek(0)
    return b


def render_relation_page(manager):
    import streamlit.components.v1 as components
    from pyvis.network import Network
    import base64

    st.markdown("## <span style='color:#bbb'>⚜</span> 人間関係図", unsafe_allow_html=True)
    
    if not manager.characters:
        st.info("キャラクターが登録されていません。")
        return

    # Initialize Pyvis Network with larger height and physics
    net = Network(height='700px', width='100%', bgcolor='#ffffff', font_color='black')
    
    # Physics toggles
    # Setting physics to help spacing
    net.force_atlas_2based(
        gravity=-50,
        central_gravity=0.01,
        spring_length=300, # Increased from 200 for spacing
        spring_strength=0.08,
        damping=0.4,
        overlap=0
    )
    
    # Or use buttons to play with it
    # net.show_buttons(filter_=['physics']) 

    # Function to convert image to base64
    def get_image_base64(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception:
            return None

    # Add Nodes
    for char in manager.characters:
        char_id = char['id']
        # Label: First Name Only
        label = char.get('first_name', char['name'])
        title = f"{char['name']}\n{char['details'].get('role', '')}"
        
        image_b64 = None
        image_b64 = None
        if char['images']:
            # Safe Load for Graph
            p = get_safe_image(char['images'][0])
            if p:
                image_b64 = get_image_base64(p)
        
        if image_b64:
            img_src = f"data:image/png;base64,{image_b64}"
            # Increase size
            net.add_node(char_id, label=label, title=title, shape='circularImage', image=img_src, size=40) # size 30->40
        else:
            net.add_node(char_id, label=label, title=title, color='#1E88E5', shape='dot', size=20)

    # Add Edges
    edge_colors = {
        "血縁": "#E53935",
        "仲間": "#43A047",
        "ライバル": "#FB8C00",
        "敵対": "#000000",
        "友人": "#039BE5",
        "主従": "#5E35B1",
        "恋人": "#E91E63",
        "片思い": "#F48FB1",
        "その他": "#8E24AA"
    }
    
    # Helper to get color if multiple types
    def get_color(types_str):
        # types_str is like "Kindred/Ally"
        first = types_str.split('/')[0]
        return edge_colors.get(first, "#999999")

    added_edges = set()

    for char in manager.characters:
        if 'relations' in char:
            for rel in char['relations']:
                source = char['id']
                target = rel['target_id']
                rel_types = rel['type'] # String like "TypeA/TypeB"
                
                target_exists = any(c['id'] == target for c in manager.characters)
                if target_exists:
                    color = get_color(rel_types)
                    label = f"{rel_types}\n({rel.get('desc', '')})"
                    
                    # Prevent duplicates if undirected? Stored directed.
                    # But graph can show arrows.
                    net.add_edge(source, target, color=color, label=label, font={'size': 12, 'align': 'middle'})

    tmp_html_path = os.path.join(DATA_DIR, "relationship_graph.html")
    net.save_graph(tmp_html_path)
    
    with open(tmp_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    components.html(html_content, height=720)
    
    # Legend
    
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

    st.markdown("### 凡例")
    cols = st.columns(5)
    keys = list(edge_colors.keys())
    for i, k in enumerate(keys):
        c = edge_colors[k]
        cols[i % 5].markdown(f"<span style='color:{c}'>■</span> {k}", unsafe_allow_html=True)


# --- Main App ---
def main():
    st.markdown("""
        <style>
        /* === GOTHIC VICTORIAN DARK MODE (RESCUE MASTER) === */
        
        /* 1. Global Background & Font */
        .stApp {
            background-color: #1a1a1a !important;
            color: #e0e0e0 !important;
            font-family: 'Times New Roman', serif;
        }
        
        /* 2. Header & Sidebar */
        header[data-testid="stHeader"] {
            background-color: #1a1a1a !important;
        }
        [data-testid="stSidebar"] {
            background-color: #111111 !important;
            border-right: 1px solid #333;
        }
        
        /* 3. Inputs (Text, Number, Select) -> Dark BG / White Text */
        .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #2c2c2c !important;
            color: #f0f0f0 !important;
            border: 1px solid #555 !important;
            border-radius: 4px;
            font-family: 'Times New Roman', serif;
        }
        ul[data-baseweb="menu"] {
            background-color: #2c2c2c !important;
            color: #f0f0f0 !important;
        }
        
        /* 4. Text Elements & Labels */
        label, .stMarkdown p, .stMarkdown span, .stMarkdown div, .stCaption, .stText p {
            color: #d0d0d0 !important;
            font-family: 'Times New Roman', serif;
        }
        
        /* 5. Headings -> Gold */
        h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            font-family: 'Garamond', 'Times New Roman', serif !important;
            color: #c5a059 !important;
            text-shadow: 1px 1px 2px #000;
            border-bottom: 1px solid #444; /* Subtle separator for headers */
            padding-bottom: 5px;
        }
        .stMarkdown strong {
            color: #c5a059 !important;
        }
        
        /* 6. Links -> SteelBlue */
        .stMarkdown a {
            color: #4682b4 !important;
            text-decoration: none;
        }
        
        /* 7. Buttons */
        /* DEFAULT (Secondary/Delete/Cancel) -> BLACK */
        /* Target generic button classes and specific overrides */
        div.stButton > button {
            background-color: #000000 !important;
            color: #cccccc !important;
            border: 1px solid #333 !important;
            border-radius: 4px;
            font-family: 'Times New Roman', serif;
        }
        div.stButton > button:hover {
            background-color: #333333 !important;
            color: #ffffff !important;
            border-color: #555 !important;
        }
        
        /* PRIMARY (Register, Sidebar) -> MAROON */
        /* Explicitly target kind="primary" */
        div.stButton > button[kind="primary"] {
            background-color: #330000 !important;
            color: white !important;
            border: 1px solid #a52a2a !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #550000 !important;
            box-shadow: 0 0 8px #330000aa;
        }
        /* Explicit check for buttons that might lose 'kind' attribute mapping in some contexts? 
           No, Streamlit renders data-testid="stButton" -> button -> kind="primary" reliably. */
    
        /* 8. Tabs */
        .stTabs [data-baseweb="tab"] {
            color: #d3d3d3 !important;
            background-color: transparent !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #4682b4 !important;
            border-bottom-color: #4682b4 !important;
        }
        
        /* 9. Expander */
        .streamlit-expanderHeader {
            background-color: #222222 !important;
            color: #c5a059 !important;
            border: 1px solid #444;
            border-radius: 4px;
        }
        details[open] .streamlit-expanderHeader {
            background-color: #222222 !important; 
        }
        div[data-testid="stExpander"] {
            background-color: #1a1a1a !important;
            border: 1px solid #444 !important;
            color: #e0e0e0 !important;
        }
        .streamlit-expanderContent {
            background-color: #1a1a1a !important;
            color: #e0e0e0 !important;
        }
        
        /* Expander/Tabs Hover Fix */
        /* Expander/Tabs Hover Fix - FORCE DARK BACKGROUND ALWAYS */
        .streamlit-expanderHeader, .streamlit-expanderHeader:hover, .streamlit-expanderHeader:focus, .streamlit-expanderHeader[aria-expanded="true"] {
             background-color: #222222 !important;
             color: #c5a059 !important;
        }
        
        div[data-testid="stExpander"] > details > summary {
             background-color: #222222 !important;
             color: #c5a059 !important;
        }
        div[data-testid="stExpander"] > details > summary:hover {
             background-color: #333333 !important;
             color: #e0be79 !important;
        }
        
        /* Download Button background -> Dark Red */
        [data-testid="stDownloadButton"] > button {
             background-color: #330000 !important;
             color: white !important;
             border: 1px solid #a52a2a !important;
        }
        [data-testid="stDownloadButton"] > button:hover {
             background-color: #550000 !important;
        }
        
        /* 10. Table / DataFrame */
        div[data-testid="stDataFrame"] {
            background-color: #2c2c2c !important;
            border: 1px solid #696969;
        }
        div[data-testid="stDataFrame"] div[role="gridcell"] {
            background-color: #2c2c2c !important;
            color: #e0e0e0 !important;
        }
        div[data-testid="stDataFrame"] div[role="columnheader"] {
            background-color: #444444 !important;
            color: #ffffff !important;
        }
        
        /* 11. Alerts / Info Boxes (Background Dark, Text Gray) */
        .stAlert {
            background-color: #2c2c2c !important;
            color: #e0e0e0 !important;
            border: 1px solid #555;
        }
        
        /* 12. Custom HTML Divs (for our manual injection) */
        /* These are inline styles mostly, but good to have fallback */
        
        </style>
        """, unsafe_allow_html=True)

    st.set_page_config(page_title="The Legend of Crystarosh Characters List", page_icon="images/logo_shield.png", layout="wide")

    

    
    # Gothic/Victorian Dark Mode CSS
    
    
    if "reg_form_key" not in st.session_state:
        st.session_state.reg_form_key = str(uuid.uuid4())
    
    manager = CharacterManager()

    # Session State Initialization
    if 'editing_char_id' not in st.session_state:
        st.session_state.editing_char_id = None
        
    # Sidebar Navigation Logic
    # To fix "Left menu doesn't return to list", we check if the sidebar selection changed or is re-clicked.
    # Streamlit sidebar radio doesn't fire event on re-click of same item.
    # We can add a "Reset" button or use the fact that if we are in 'detail' mode, we might want to go back to list 
    # if the user interacts with the sidebar '一覧・詳細' again? No, hard to detect.
    # Force a "Home/List" button in sidebar?
    
    st.sidebar.title("メニュー")
    
    # Custom Navigation
    # Using buttons instead of radio for better control? 
    # Or just add a "Back to List" button in sidebar anytime we are in detail mode.
    
    view_mode = st.session_state.get('view_mode', 'list')
    
    if st.sidebar.button("📂 キャラクター一覧", use_container_width=True, type="primary"):
        st.session_state.view_mode = 'list'
        st.session_state.selected_char_id = None
        st.session_state.editing_char_id = None # Correctly clear editing state
        st.rerun()
        
    st.sidebar.divider()
    

    if st.sidebar.button("➕ 新規登録", use_container_width=True, type="primary"):
        if verify_admin():
            st.session_state.view_mode = 'register'
            st.session_state.editing_char_id = None
            st.session_state.reg_form_key = str(uuid.uuid4())
            # Clear input state
            for k in list(st.session_state.keys()):
                if (k.startswith('reg_') or k.startswith('stat_') or k.startswith('p_stat_') 
                    or k.startswith('input_') or k.startswith('picker_') or k == 'bio_input_area'
                    or k == 'bio_short_input' or k.startswith('rel_') # Clear persistent text areas
                    or k.startswith('u') or k.startswith('del_img_')): # Clear uploaders and deletes too
                    try:
                         del st.session_state[k]
                    except:
                         pass
            st.rerun()

    if st.sidebar.button("🤝 人間関係", type="primary", use_container_width=True):
        st.session_state.view_mode = 'relation'
        st.rerun()

    st.sidebar.divider()
    
    # --- Global Security Input ---
    with st.sidebar.expander("🔒 セキュリティ設定", expanded=False):
        st.caption("変更・保存・削除に必要です")
        st.text_input("編集パスワード", type="password", key="global_admin_pw")

    # Routing
    # We use session_state.view_mode as primary router
    current_mode = st.session_state.get('view_mode', 'list')

    if current_mode == 'register':
         render_register_page(manager, st.session_state.get('editing_char_id'))
    elif current_mode == 'relation':
         render_relation_page(manager)
    elif current_mode == 'image_view':
        # Simple Image Viewer
        st.button("詳細に戻る", on_click=lambda: st.session_state.update(view_mode='detail'))
        img_path = st.session_state.get('view_img_path')
        if img_path:
            st.image(img_path, use_container_width=True)
        else:
            st.error("画像エラー")
    else:
         # Default to list/detail handler
         # Ensure we initialize if needed
         if 'view_mode' not in st.session_state: st.session_state.view_mode = 'list'
         render_list_page(manager)

if __name__ == "__main__":
    main()

