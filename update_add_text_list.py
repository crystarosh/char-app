
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# UPDATE: Add Text List View with Search/Sort
# Function to be replaced: render_list_page

new_code = r'''def render_list_page(manager):
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
        
        tab_card, tab_text = st.tabs(["🖼️ カード表示", "📋 データベース表示"])
        
        # --- TAB 1: CARD VIEW ---
        with tab_card:
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
            </style>
            """, unsafe_allow_html=True)
            
            if not manager.characters:
                st.info("キャラクターが登録されていません。")
            else:
                cols = st.columns(5)
                for i, char in enumerate(manager.characters):
                    with cols[i % 5]:
                         target_img = char['images'][0] if char['images'] else None
                         if target_img:
                             try:
                                 from PIL import Image as PILImage
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
                    
                    name_disp = char['name']
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
                        zip_data = generate_card_zip(char, manager)
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
'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

import re
pattern = re.compile(r"^def render_list_page.*?^(?=def |if __name__)", re.MULTILINE | re.DOTALL)
match = pattern.search(content)

if match:
    # Use re.sub or generic replacement?
    # Simple slicing is safer for big blocks.
    pre = content[:match.start()]
    post = content[match.end():]
    new_content = pre + new_code + "\n\n" + post
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Added Table View successfully.")
else:
    print("Error: Could not find render_list_page block.")
