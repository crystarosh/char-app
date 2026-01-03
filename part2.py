    def create_image_3(char):
        from PIL import ImageOps
        import json 
        
        img = base_texture.copy()
        draw = ImageDraw.Draw(img)
        draw_decorations(draw, 800, 600)
        
        # 1. Full Body Image (Left Side)
        target_img_path = None
        if len(char['images']) > 1:
            target_img_path = char['images'][1] 
        elif char['images']:
            target_img_path = char['images'][0]
            
        if target_img_path:
             try:
                 full_img = Image.open(target_img_path).convert("RGBA")
                 box_w, box_h = 380, 500
                 full_img.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
                 fw, fh = full_img.size
                 fx = 50 + (box_w - fw) // 2
                 fy = 50 + (box_h - fh) // 2
                 img.paste(full_img, (fx, fy), full_img) 
             except:
                 pass

        # 2. Right Side 
        
        # Name Area (Right Top)
        # Format: First Last
        char_name = char['name']
        if char.get('first_name') and char.get('last_name'):
             char_name = f"{char['first_name']} {char['last_name']}"
        
        # Font size: smaller (font_medium or font_large depending on length, but requested smaller)
        # Let's use font_medium explicitly for consistency with Image 2 change request "smaller".
        try:
             # Check if we need to load medium locally or use global? Global `font_medium` exists.
             draw.text((450, 40), char_name, fill="#3e2723", font=font_medium)
        except:
             draw.text((450, 40), char_name, fill="#3e2723", font=font_large)

        # Middle Grid (Image 3 & 4 Side-by-Side)
        img3_path = char['images'][2] if len(char['images']) > 2 else None
        img4_path = char['images'][3] if len(char['images']) > 3 else None
        
        y_imgs = 130
        sq_size = 140
        
        # Image 3 (Left of Right Column)
        if img3_path:
            try:
                i3 = Image.open(img3_path).convert("RGBA")
                i3 = ImageOps.fit(i3, (sq_size, sq_size), method=Image.LANCZOS)
                img.paste(i3, (450, y_imgs))
            except:
                pass
        else:
             draw.rectangle([450, y_imgs, 450+sq_size, y_imgs+sq_size], outline="#ccc")

        # Image 4 (Right of Right Column)
        if img4_path:
            try:
                i4 = Image.open(img4_path).convert("RGBA")
                i4 = ImageOps.fit(i4, (sq_size, sq_size), method=Image.LANCZOS)
                img.paste(i4, (450 + sq_size + 20, y_imgs))
            except:
                pass
        else:
             draw.rectangle([450 + sq_size + 20, y_imgs, 450 + 2*sq_size + 20, y_imgs+sq_size], outline="#ccc")

        # 3. Relations (Right Bottom)
        all_chars_map = {}
        data_path = os.path.join("data", "characters.json") 
        if not os.path.exists(data_path):
             data_path = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\data\characters.json"
             
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                ac = json.load(f)
                all_chars_map = {c['id']: c for c in ac}
        except:
            pass

        rels = char.get('relations', [])
        valid_rels = []
        for r in rels:
            if r['target_id'] in all_chars_map:
                valid_rels.append(r)
            if len(valid_rels) >= 5: break
            
        # Draw Rel Nodes
        # Title: Smaller font (font_small)
        # Pos: Lower down. Original y=320 text, 370 nodes.
        # "Block overall down".
        # Let's move down by 30px.
        
        y_rel_title = 350
        draw.text((450, y_rel_title), "【メイン人間関係】", fill="#3e2723", font=font_small)
            
        if valid_rels:
            start_x = 450
            start_y = y_rel_title + 50 # 400
            step_x = 60 
            step_x = 60 
            
            for i, r in enumerate(valid_rels):
                cx = start_x + (i * step_x)
                cy = start_y
                
                # Type (Above)
                rtype = r['type'].split('/')[0][:4]
                try:
                    font_path = os.path.join("fonts", "NotoSansJP-Regular.otf")
                    if not os.path.exists(font_path): font_path = "meiryo.ttc"
                    type_font = ImageFont.truetype(font_path, 10) 
                except:
                    type_font = ImageFont.truetype("arial.ttf", 9)
                    
                try:
                    tw = draw.textlength(rtype, font=type_font)
                    tx = cx + (50 - tw) / 2
                    draw.text((tx, cy), rtype, fill="#5d4037", font=type_font)
                except:
                    draw.text((cx, cy), rtype, fill="#5d4037", font=font_small)

                # Icon
                icon_y = cy + 15
                target_c = all_chars_map.get(r['target_id'])
                if target_c and target_c.get('images'):
                    try:
                        t_img = Image.open(target_c['images'][0]).convert("RGBA")
                        t_img = ImageOps.fit(t_img, (50, 50), method=Image.LANCZOS)
                        img.paste(t_img, (cx, icon_y)) 
                    except:
                        draw.rectangle([cx, icon_y, cx+50, icon_y+50], fill="#ddd")
                else:
                    draw.rectangle([cx, icon_y, cx+50, icon_y+50], fill="#ddd")
                
                # Name (Below)
                t_name = target_c.get('first_name', target_c['name'])
                target_width = 58
                size = 14 
                used_font = font_small
                try:
                    while size > 6:
                         try:
                             font_path = os.path.join("fonts", "NotoSansJP-Regular.otf")
                             if not os.path.exists(font_path): font_path = "meiryo.ttc"
                             test_font = ImageFont.truetype(font_path, size)
                         except:
                             test_font = ImageFont.truetype("arial.ttf", size)
                         w = draw.textlength(t_name, font=test_font)
                         if w <= target_width:
                             used_font = test_font
                             break
                         size -= 1
                    else:
                         used_font = ImageFont.truetype("arial.ttf", 8)
                         while draw.textlength(t_name, font=used_font) > target_width and len(t_name) > 0:
                             t_name = t_name[:-1]
                except:
                    pass

                try:
                    nw = draw.textlength(t_name, font=used_font)
                    nx = cx + (50 - nw) / 2
                    draw.text((nx, icon_y + 52), t_name, fill="#3e2723", font=used_font)
                except:
                    draw.text((cx, icon_y + 52), t_name[:3], fill="#3e2723", font=font_small)
        
        # User Name (Top Center)
        if char.get('user_name'):
             u_text = f"User: {char['user_name']}"
             try:
                 uw = draw.textlength(u_text, font=font_small)
                 ux = (800 - uw) / 2
                 draw.text((ux, 10), u_text, fill="#555", font=font_small)
             except:
                 pass
                 
        # Footer (Center)
        footer_text = "Legend of Crystarosh"
        try:
            fw = draw.textlength(footer_text, font=font_small)
            fx = (800 - fw) / 2
        except:
            fx = 300
        draw.text((fx, 570), footer_text, fill="#8d6e63", font=font_small)
        return img

    # Generate
