    try:
        img1 = create_image_1(char)
        img2 = create_image_2(char)
        img3 = create_image_3(char) # New
        
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Save Img 1
            b1 = io.BytesIO()
            img1.save(b1, format='PNG')
            zf.writestr(f"{char['name']}_basic.png", b1.getvalue())
            
            # Save Img 2
            b2 = io.BytesIO()
            img2.save(b2, format='PNG')
            zf.writestr(f"{char['name']}_detail.png", b2.getvalue())
            
            # Save Img 3
            b3 = io.BytesIO()
            img3.save(b3, format='PNG')
            zf.writestr(f"{char['name']}_fullbody.png", b3.getvalue())
            
        zip_buf.seek(0)
        return zip_buf
    except Exception as e:
        print(e)
        return None

def render_relation_page(manager):
    import streamlit.components.v1 as components
    from pyvis.network import Network
    import base64

    st.header("🤝 人間関係図")
    
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
        if char['images']:
            image_b64 = get_image_base64(char['images'][0])
        
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
    st.markdown("### 凡例")
    cols = st.columns(5)
    keys = list(edge_colors.keys())
    for i, k in enumerate(keys):
        c = edge_colors[k]
        cols[i % 5].markdown(f"<span style='color:{c}'>■</span> {k}", unsafe_allow_html=True)


# --- Main App ---
def main():
    st.set_page_config(page_title="Character Manager", layout="wide", page_icon="🛡️")
    st.title("🛡️ キャラクター図鑑")
    
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
    
    if st.sidebar.button("📂 キャラクター一覧", use_container_width=True):
        st.session_state.view_mode = 'list'
        st.session_state.selected_char_id = None
        st.session_state.editing_char_id = None # Correctly clear editing state
        st.rerun()
        
    if st.sidebar.button("➕ 新規登録", use_container_width=True):
        st.session_state.view_mode = 'register'
        st.session_state.editing_char_id = None
        st.rerun()

    if st.sidebar.button("🕸️ 人間関係図", use_container_width=True):
        st.session_state.view_mode = 'relation'
        st.rerun()

    st.sidebar.divider()

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
