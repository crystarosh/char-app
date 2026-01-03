             base_texture = Image.open(bg_path).convert("RGBA")
             base_texture = base_texture.resize((800, 600))
        except:
             pass
    
    # Fallback if no texture
    if not base_texture:
        base_texture = Image.new('RGBA', (800, 600), (250, 245, 230, 255))

    # --- Helper: Draw Decoration (Victorian) ---
    def draw_decorations(draw, w, h):
        # Load Victorian Corner
        corner_path = r"C:\Users\sweet\.gemini\antigravity\brain\f632eb69-1385-4e0a-bf7b-2cc9ec5d7899\victorian_corner_1767013906098.png"
        if os.path.exists(corner_path):
            try:
                corner = Image.open(corner_path).convert("RGBA")
                corner = corner.resize((150, 150))
                
                # Make Transparent (White -> Transparent)
                # This is a bit expensive in pure Python but OK for 150x150
                datas = corner.getdata()
                new_data = []
                for item in datas:
                    # Check for near white
                    if item[0] > 200 and item[1] > 200 and item[2] > 200:
                        new_data.append((255, 255, 255, 0)) # Transparent
                    else:
                        new_data.append(item)
                corner.putdata(new_data)

                # Correct Orientation Logic based on User Feedback
                # User said: "Right is Left, Left is Right".
                # Standard Corner (Top-Left pointing IN) usually needs:
                # TL: Original
                # TR: Flip Left-Right
                # BL: Flip Top-Bottom
                # BR: Flip Both
                # If User says it's reversed, maybe the source image is NOT Top-Left?
                # Or maybe I just need to swap them as requested.
                
                # Requested: "Put Right things on Left, Left things on Right" relative to previous state.
                # Previous state was:
                # TL: Flipped LR
                # TR: Original
                
                # So New State should be (Standard):
                # TL: Original
                # TR: Flipped LR
                # BL: Flipped TB
                # BR: Flipped Both
                
                # Correct Orientation Logic (User Feedback: "Reversed again")
                # Previously: TL=Original, TR=FlipLR.
                # User says: "Corner is reversed again".
                # New Logic: SWAP Left and Right.
                
                # Top-Left: Flip Left-Right
                corner_tl = corner.transpose(Image.FLIP_LEFT_RIGHT)
                draw._image.paste(corner_tl, (0, 0), corner_tl)

                # Top-Right: Original
                draw._image.paste(corner, (w-150, 0), corner)

                # Bottom-Left: Flip Both (Rotate 180)
                corner_bl = corner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
                draw._image.paste(corner_bl, (0, h-150), corner_bl)

                # Bottom-Right: Flip Top-Bottom
                corner_br = corner.transpose(Image.FLIP_TOP_BOTTOM)
                draw._image.paste(corner_br, (w-150, h-150), corner_br)
                
            except:
                pass
        
        # Inner thin border
        draw.rectangle([40, 40, w-40, h-40], outline="#5d4037", width=2)

    # --- Helper: Draw Radar for Pillow (Filled with Alpha) ---
    def draw_radar_pil(base_img, center_x, center_y, radius, stats, color_fill_rgba, color_line):
        import math
        draw = ImageDraw.Draw(base_img) # Draw on base for lines
        
        if not stats: return
        
        keys = list(stats.keys())
        values = list(stats.values())
        num_vars = len(keys)
        
        angle_step = 2 * math.pi / num_vars
        
        # Clip values to 5 for drawing
        draw_values = [min(v, 5) for v in values]
        max_scale_val = 5.0
        
        # 1. Background Grid
        for step in [1, 2, 3, 4, 5]:
            r_grid = (step / max_scale_val) * radius
            points_grid = []
            for i in range(num_vars):
                angle = i * angle_step - math.pi / 2
                px = center_x + r_grid * math.cos(angle)
                py = center_y + r_grid * math.sin(angle)
                points_grid.append((px, py))
            draw.polygon(points_grid, outline="#999", width=1)
        
        # 2. Axis Lines
        for i in range(num_vars):
            angle = i * angle_step - math.pi / 2
            end_x = center_x + radius * math.cos(angle)
            end_y = center_y + radius * math.sin(angle)
            draw.line((center_x, center_y, end_x, end_y), fill="#bbb", width=1)
            
            # Label
            lbl_r = radius + 25
            lbl_x = center_x + lbl_r * math.cos(angle)
            lbl_y = center_y + lbl_r * math.sin(angle)
            draw.text((lbl_x-15, lbl_y-10), keys[i], fill="#3e2723", font=font_small)

        # 3. Data Polygon (Filled)
        points = []
        for i, v in enumerate(draw_values):
            r = (v / max_scale_val) * radius
            angle = i * angle_step - math.pi / 2
            p_x = center_x + r * math.cos(angle)
            p_y = center_y + r * math.sin(angle)
            points.append((p_x, p_y))
        
        if len(points) > 2:
            # Create a separate layer for alpha fill
            poly_layer = Image.new("RGBA", base_img.size, (0,0,0,0))
            p_draw = ImageDraw.Draw(poly_layer)
            p_draw.polygon(points, fill=color_fill_rgba, outline=None)
            
            # Composite
            base_img.alpha_composite(poly_layer)
            
            # Draw outline on top in base
            draw.polygon(points, outline=color_line, width=2)

    # --- Helper: Text Wrap with Kinsoku ---
    def draw_text_wrapped(draw, text, x, y, max_w, font, fill, center_align=False):
        import textwrap
        
        # Estimate char width (approx)
        # Using a dummy call to get length would be better but expensive in loop.
        # Simple heuristic: 18px font -> avg 18 width?
        # Actually we need robust measurement or simple `textwrap` with strict width character count.
        # Assuming Japanese chars are 2 bytes width roughly... 
        
        # Better Approach:
        # Build lines word by word? Japanese doesn't have spaces.
        # We'll stick to a char count based wrap for simplicity, but add Kinsoku.
        
        # Determine chars per line based on font size.
        # This is strictly heuristic if we don't Measure.
        # Let's Measure max width of 'あ'
        try:
             bbox = draw.textbbox((0,0), "あ", font=font)
             char_w = bbox[2] - bbox[0]
        except:
             char_w = 20 # Fallback
        
        cols = int(max_w / char_w)
        if cols < 1: cols = 1
        
        # Pre-process text to remove newlines if it's meant to be block text, 
        # OR split by newlines first. Assuming input 'text' might have paragraphs.
        # But 'textwrap' treats newlines as paragraphs.
        
        raw_lines = text.splitlines()
        final_lines = []
        
        kinsoku_head = "、。，．・？！゛゜ヽヾゝゞ々ー）］｝」』】" # Chars that shouldn't start a line
        
        for r_line in raw_lines:
            # Use textwrap to split initially
            wrapped = textwrap.wrap(r_line, width=cols)
            
            # Kinsoku Processing
            # If a line starts with kinsoku char, move it to previous line end.
            i = 0
            while i < len(wrapped):
                line = wrapped[i]
                if i > 0 and len(line) > 0 and line[0] in kinsoku_head:
                    # Move char to previous
                    prev = wrapped[i-1]
                    char_to_move = line[0]
                    wrapped[i-1] = prev + char_to_move
                    wrapped[i] = line[1:]
                    
                    # If current line becomes empty, remove it
                    if len(wrapped[i]) == 0:
                        wrapped.pop(i)
                        i -= 1 # re-check same index (next line shifted)
                i += 1
            final_lines.extend(wrapped)
            
        current_y = y
        for line in final_lines:
            if center_align:
                # Calculate X to center
                try:
                    bbox = draw.textbbox((0,0), line, font=font)
                    lw = bbox[2] - bbox[0]
                except:
                    lw = len(line) * char_w
                start_x = x + (max_w - lw) / 2
                draw.text((start_x, current_y), line, fill=fill, font=font)
            else:
                draw.text((x, current_y), line, fill=fill, font=font)
            current_y += int(char_w * 1.5) # Line height
        return current_y

     # --- Image 1: Basic Info ---
    def create_image_1(char):
        from PIL import ImageOps # Ensure import
        img = base_texture.copy()
        draw = ImageDraw.Draw(img)
        draw_decorations(draw, 800, 600)
        
        # Main Image (Left) - Force Fixed Size (Rubeus Size)
        # Assuming 350x400 is the target standard.
        if char['images']:
            try:
                char_img = Image.open(char['images'][0]).convert("RGBA")
                # Use ImageOps.fit to force crop/resize to exact 350x400
                char_img = ImageOps.fit(char_img, (350, 400), method=Image.LANCZOS)
                img.paste(char_img, (50, 60), char_img) 
            except:
                pass
        
        # User Name/PL Name (Top Right, Outside Border)
        # Use simple text, maybe smaller font?
        # User Name/PL Name (Top Center, Outside Border)
        # User Name/PL Name (Top Center, Outside Border)
        if char.get('user_name'):
             u_text = f"User: {char['user_name']}"
             try:
                 uw = draw.textlength(u_text, font=font_small)
                 # Center at 400
                 ux = (800 - uw) / 2
                 # Move slightly up from 20 to 15 to create gap from border (which starts at 40)
                 # Border rect: 40,40 to 760,560. Top edge is 40.
                 # Text at 20 (top-left of text). Height approx 18. Bottom of text ~38. Close.
                 # Let's move to 10.
                 draw.text((ux, 10), u_text, fill="#555", font=font_small)
             except:
                 pass

        # Appearance text below image
        app_text = char['details'].get('appearance', '詳細なし')
        
        lbl_y = 470
        draw.text((50, lbl_y), "【容姿・外見】", fill="#3e2723", font=font_small)
        
        # Color Chips next to Title
        # Title starts at 50. Length approx 140-150px.
        # Place chips starting at x=220
        chip_x = 220
        chip_y = lbl_y + 2 # Align with text baseline approx
        chip_size = 20
        
        colors_to_draw = [
            char['details'].get('image_color'),
            char['details'].get('eye_color'),
            char['details'].get('hair_color')
        ]
        
        for i, c_code in enumerate(colors_to_draw):
            if c_code and c_code.startswith('#') and len(c_code) == 7:
                 try:
                     # Parse hex
                     rgb = tuple(int(c_code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                     draw.rectangle([chip_x, chip_y, chip_x+chip_size, chip_y+chip_size], fill=rgb, outline="#555")
                     
                     # Draw Hex Code (Add space)
                     draw.text((chip_x + chip_size + 8, chip_y + 2), c_code, fill="#555", font=font_small)
                     
                     # Shift X (Increased spacing to avoid overlap)
                     chip_x += 120 
                 except:
                     pass

        text_y = lbl_y + 25
        # Align text x=160.
        current_y = draw_text_wrapped(draw, app_text, 160, text_y, 450, font_small, "#000")
        
        # REMOVED DUPLICATE CHIP LOOP HERE
        
        # Text Info (Right)
        x_base = 420
        y = 60
        
        # Name: First Last order
        # Dynamic Font Size for Long Names
        jp_full = ""
        if char.get('first_name') and char.get('last_name'):
            jp_full = f"{char['first_name']} {char['last_name']}"
        else:
            jp_full = char['name']
            
        # Check width
        name_font = font_medium
        try:
            # Check length against available width (approx 340px)
            if draw.textlength(jp_full, font=font_medium) > 340:
                name_font = font_small
                # If still too long? (Optional: use smaller or truncate)
        except:
            if len(jp_full) > 10: name_font = font_small
            
        draw.text((x_base, y), jp_full, fill="#3e2723", font=name_font)
        y += 40
        
        # English/Romaji Name
        name_en = char.get('name_en', '')
        if name_en:
             draw.text((x_base, y), name_en, fill="#5d4037", font=font_romaji)
             y += 30
        
        # If no explicit name_en, checking for fallback logic (existing data)
        # But User said "If distinct input is better, fix it". We did add field.
        # So we trust 'name_en' primarily.

        y += 10 
        role = char['details'].get('role', '')
        draw.text((x_base, y), role, fill="#5d4037", font=font_small) 
        y += 30
        
        # Details Table-like
        # Draw Start items
        items_first = [
            ("年齢", char['details'].get('age')),
            ("身長/体重", char['details'].get('height_weight')),
        ]
        
        for k, v in items_first:
            if v:
                draw.text((x_base, y), f"【{k}】", fill="#4e342e", font=font_small) 
                y += 20
                y = draw_text_wrapped(draw, str(v), x_base + 20, y, 300, font_small, "#000")
                y += 5

        # Origin/Affiliation (Custom handling for label and wrapping)
        origin_val = char['details'].get('origin')
        if origin_val:
            draw.text((x_base, y), "【出身/所属】", fill="#3e2723", font=font_small)
            y += 25
            # Use font_small for content to match other fields
            y = draw_text_wrapped(draw, origin_val, x_base+20, y, 300, font_small, "#000")
            y += 10

        # Personality
        pers_val = char['details'].get('personality')
        if pers_val:
            draw.text((x_base, y), "【性格】", fill="#4e342e", font=font_small)
            y += 20
            y = draw_text_wrapped(draw, str(pers_val), x_base + 20, y, 300, font_small, "#000")
            y += 5
        
        # Footer (Center)
        footer_text = "Legend of Crystarosh"
        try:
            fw = draw.textlength(footer_text, font=font_small)
            fx = (800 - fw) / 2
        except:
            fx = 300
        draw.text((fx, 570), footer_text, fill="#8d6e63", font=font_small)
        return img

    # --- Helper: High Quality Radar Chart ---
    def draw_hq_radar(stats_dict, labels, title, color_fill, color_line):
        import math
        # Create Hi-Res Canvas (4x size)
        size = 600
        center = size // 2
        radius = 200 
        
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Data Prep
        values = [int(stats_dict.get(l, 3)) for l in labels]
        num_vars = len(labels)
        angles = [n / float(num_vars) * 2 * math.pi - math.pi/2 for n in range(num_vars)]
        angles += angles[:1]
        values += values[:1]
        
        # Draw Grid (1 to 5, and 6)
        for i in range(1, 7):
            r = radius * (i / 5.0)
            if i == 6: 
                grid_color = (150, 150, 150, 100) # Boundary
            else:
                grid_color = (200, 200, 200, 100)
                
            pts = []
            for a in angles[:-1]:
                x = center + r * math.cos(a)
                y = center + r * math.sin(a)
                pts.append((x, y))
            draw.polygon(pts, outline=grid_color, width=2)
            
        # Draw Axes
        for a in angles[:-1]:
            x = center + (radius * 1.2) * math.cos(a)
            y = center + (radius * 1.2) * math.sin(a)
            draw.line((center, center, x, y), fill=(220, 220, 220, 255), width=2)

        # Draw Data Polygon
        data_pts = []
        for i, v in enumerate(values[:-1]):
            val_vis = min(v, 6)
            r = radius * (val_vis / 5.0)
            x = center + r * math.cos(angles[i])
            y = center + r * math.sin(angles[i])
            data_pts.append((x, y))
            
        if len(data_pts) > 2:
            draw.polygon(data_pts, fill=color_fill, outline=color_line)
            draw.line(data_pts + [data_pts[0]], fill=color_line, width=4)

        # Draw Labels
        try:
             font_path = os.path.join("fonts", "NotoSansJP-Regular.otf")
             if not os.path.exists(font_path): font_path = "meiryo.ttc"
             l_font = ImageFont.truetype(font_path, 32)
        except:
             try:
                 l_font = ImageFont.truetype("meiryo.ttc", 32)
             except:
                 l_font = ImageFont.load_default()
             
        for i, label in enumerate(labels):
            a = angles[i]
            dist = radius * 1.35
            
            lx = center + dist * math.cos(a)
            ly = center + dist * math.sin(a)
            
            # Simple centering calc
            try:
                lw = draw.textlength(label, font=l_font)
            except:
                lw = len(label) * 20
            
            draw.text((lx - lw/2, ly - 16), label, fill="#333", font=l_font)

        return img.resize((30, 30), Image.Resampling.LANCZOS).resize((240, 240), Image.Resampling.NEAREST) if False else img.resize((240, 240), Image.Resampling.LANCZOS)

    # --- Image 2: Chart & Bio ---
    def create_image_2(char):
        img = base_texture.copy()
        draw = ImageDraw.Draw(img)
        draw_decorations(draw, 800, 600)

        # Name: Top Center Outside Border
        # Name: Top Center Outside Border
        # Format: First Last
        char_name = char['name']
        if char.get('first_name') and char.get('last_name'):
             char_name = f"{char['first_name']} {char['last_name']}"
             
        try:
            # Use smaller font
            nw = draw.textlength(char_name, font=font_medium)
            nx = (800 - nw) / 2
            # Add margin (from 15 to 20 or more? Border is at 40. User said "margin above decor line".
            # Decor line top is 40.
            # If text is at 10, it's above.
            # "Add margin/space above the decorative border line from the top edge."
            # Maybe keep it at 10-15 but ensure font is smaller to create space.
            draw.text((nx, 10), char_name, fill="#3e2723", font=font_medium)
        except:
            pass
            
        # User Name: Below Name? Or remove? 
        if char.get('user_name'):
             u_text = f"User: {char['user_name']}"
             try:
                 uw = draw.textlength(u_text, font=font_small)
                 ux = (800 - uw) / 2
                 draw.text((ux, 60), u_text, fill="#555", font=font_small)
             except:
                 pass

        # 1. Radar Charts (High Quality)
        # Position: Left (Basic), Right (Personality)
        # y=100
        
        # 1. Radar Charts (High Quality)
        # Position: Left (Basic), Right (Personality)
        # Shift Up: from y=100 to y=80
        # Shrink: done in draw_hq_radar (300->240)
        
        y_chart = 80
        
        # Basic Stats
        labels_basic = ["知力", "体力", "魔力", "防御力", "行動力", "攻撃力", "自信"]
        chart_basic = draw_hq_radar(char.get('stats', {}), labels_basic, "基礎ステータス", (30, 136, 229, 80), (30, 136, 229, 255))
        img.paste(chart_basic, (110, y_chart), chart_basic) # Adjusted x for smaller size centering (Original 80, size 300->240. Delta 60. +30)
        
        # Title (Smaller font)
        # Original title pos: 230-40=190, 90.
        # Check title draw manually or rely on chart internal title? Chart doesn't draw title internally.
        # We draw title relative.
        # Let's use font_small.
        # new center of chart: 110 + 120 = 230.
        draw.text((230 - 30, y_chart - 15), "基礎能力", fill="#3e2723", font=font_small)

        # Personality Stats
        labels_pers = ["積極性", "協調性", "慎重さ", "適応力", "精神力", "寛容さ", "道徳・倫理観", "社交性"]
        chart_pers = draw_hq_radar(char.get('personality_stats', {}), labels_pers, "性格傾向", (229, 57, 53, 80), (229, 57, 53, 255))
        img.paste(chart_pers, (450, y_chart), chart_pers) # Original 420 + 30
        
        # Title
        # new center 450 + 120 = 570
        draw.text((570 - 30, y_chart - 15), "性格傾向", fill="#3e2723", font=font_small)

        # 2. Bio
        # Change Title: "【設定抜粋】"
        # y=350 (Moved up from 420 due to chart shrink)
        y = 350
        x_base = 100
        
        draw.text((x_base, y), "【設定抜粋】", fill="#3e2723", font=font_medium)
        y += 30
        
        bio = char.get('bio_short', '')
        if not bio:
            bio = char.get('bio', '')
            if len(bio) > 150: bio = bio[:150] + "..." # Allow more chars
            bio = "(Auto-Summary) " + bio

        # Smaller font for bio content
        try:
             # Try to load size 14
             font_path = os.path.join("fonts", "NotoSansJP-Regular.otf")
             if not os.path.exists(font_path): font_path = "meiryo.ttc"
             bio_font = ImageFont.truetype(font_path, 14)
        except:
             bio_font = font_small

        y = draw_text_wrapped(draw, bio, x_base, y, 600, bio_font, "#212121", center_align=False)
            
        # Center Footer
        footer_text = "Legend of Crystarosh"
        try:
            fw = draw.textlength(footer_text, font=font_small)
            fx = (800 - fw) / 2
        except:
            fx = 300
        draw.text((fx, 570), footer_text, fill="#8d6e63", font=font_small)
        return img

    # --- Image 3: Full Body & Gallery & Relations ---
