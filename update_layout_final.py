
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# New Logic
new_function = r'''def generate_card_zip(char, manager):
    import io
    import zipfile
    import os
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    import math

    # --- Configuration ---
    CANVAS_1 = (1024, 1024)
    CANVAS_LANDSCAPE = (1024, 768)
    FONT_PATH = os.path.join("fonts", "NotoSansJP-Regular.otf")
    TEXTURE_PATH = r"C:\Users\sweet\.gemini\antigravity\brain\f632eb69-1385-4e0a-bf7b-2cc9ec5d7899\old_paper_texture_1767013103684.png"
    CORNER_PATH = r"C:\Users\sweet\.gemini\antigravity\brain\f632eb69-1385-4e0a-bf7b-2cc9ec5d7899\victorian_corner_1767013906098.png"

    # --- Helpers ---
    def get_font(size):
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except:
            return ImageFont.load_default()

    f_small = get_font(24)
    f_med = get_font(30)
    f_large = get_font(50)
    f_romaji = get_font(40)

    def draw_text(draw, text, position, font, fill="#000000", anchor="la"):
        if text:
            draw.text(position, text, font=font, fill=fill, anchor=anchor)

    def draw_text_wrapped(draw, text, x, y, max_w, font, fill):
        if not text: return y
        char_w = font.size * 1.0 
        cols = int(max_w / char_w)
        if cols < 1: cols = 1
        
        lines = []
        for line in text.splitlines():
            current = ""
            for c in line:
                if len(current) >= cols:
                    lines.append(current)
                    current = c
                else:
                    current += c
            if current: lines.append(current)
            
        current_y = y
        for l in lines:
            draw.text((x, current_y), l, font=font, fill=fill)
            current_y += int(font.size * 1.5)
        return current_y

    def load_image_cover(path, size):
        try:
            img = Image.open(path).convert("RGBA")
            target_ratio = size[0] / size[1]
            img_ratio = img.width / img.height
            if img_ratio > target_ratio:
                new_width = int(img.height * target_ratio)
                offset = (img.width - new_width) // 2
                img = img.crop((offset, 0, offset + new_width, img.height))
            else:
                new_height = int(img.width / target_ratio)
                offset = (img.height - new_height) // 2
                img = img.crop((0, offset, img.width, offset + new_height))
            return img.resize(size, Image.Resampling.LANCZOS)
        except:
            ph = Image.new('RGBA', size, (200, 200, 200, 255))
            d = ImageDraw.Draw(ph)
            d.text((size[0]//2, size[1]//2), "No Image", fill="gray", anchor="mm", font=f_small)
            return ph

    def draw_decorations(draw, w, h):
        # Victorian Corners: Standard (TL=In looking)
        if os.path.exists(CORNER_PATH):
            try:
                corner = Image.open(CORNER_PATH).convert("RGBA").resize((150, 150))
                # Make white transparent
                data = []
                for item in corner.getdata():
                    if item[0]>200 and item[1]>200 and item[2]>200:
                        data.append((255, 255, 255, 0))
                    else:
                        data.append(item)
                corner.putdata(data)
                
                # TL (Original)
                draw._image.paste(corner, (0, 0), corner)
                # TR (Flip H)
                tr = corner.transpose(Image.FLIP_LEFT_RIGHT)
                draw._image.paste(tr, (w-150, 0), tr)
                # BL (Flip V)
                bl = corner.transpose(Image.FLIP_TOP_BOTTOM)
                draw._image.paste(bl, (0, h-150), bl)
                # BR (Flip Both)
                br = corner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
                draw._image.paste(br, (w-150, h-150), br)
            except:
                pass
        # Inner Frame
        draw.rectangle((40, 40, w-40, h-40), outline="#5d4037", width=2)

    def draw_radar(base_img, center, radius, stats, labels, color_fill, color_line):
        # Semi-Transparent Radar
        draw = ImageDraw.Draw(base_img)
        n = len(labels)
        angle_step = 2 * math.pi / n
        start_angle = -math.pi / 2
        
        # Grid
        for i in range(1, 6):
            r = radius * (i/5)
            pts = []
            for j in range(n):
                ang = start_angle + j * angle_step
                pts.append((center[0] + r*math.cos(ang), center[1] + r*math.sin(ang)))
            draw.polygon(pts, outline="#AAAAAA")
        
        # Axis & Labels (Above Chart)
        for j in range(n):
            ang = start_angle + j * angle_step
            end = (center[0] + radius*math.cos(ang), center[1] + radius*math.sin(ang))
            draw.line([center, end], fill="#AAAAAA")
            
            # Labels
            lx = center[0] + (radius+25)*math.cos(ang)
            ly = center[1] + (radius+25)*math.sin(ang)
            
            anchor = "mm"
            if math.cos(ang) > 0.2: anchor="lm"
            elif math.cos(ang) < -0.2: anchor="rm"
            
            draw.text((lx, ly), labels[j], fill="#333", font=get_font(20), anchor=anchor)

        # Values
        vals = [int(stats.get(l, 3)) for l in labels]
        pts = []
        for j in range(n):
            v = min(vals[j], 5)
            r = radius * (v/5)
            ang = start_angle + j * angle_step
            pts.append((center[0] + r*math.cos(ang), center[1] + r*math.sin(ang)))
            
        if len(pts) > 2:
            # Translucent Fill
            poly_layer = Image.new("RGBA", base_img.size, (0,0,0,0))
            pdraw = ImageDraw.Draw(poly_layer)
            pdraw.polygon(pts, fill=color_fill) 
            base_img.alpha_composite(poly_layer)
            # Outline
            draw.polygon(pts, outline=color_line, width=2)

    # --- CARD 1: Profile (1024x1024) ---
    def create_card_1():
        # New Layout: Left=Face, Right=Body.
        # Img 1 (Face): x=50, y=100, w=450, h=450 (Behind)
        # Img 2 (Body): x=550, y=100, w=400, h=650 (Behind)
        # Data Between: x=500? No, Face 50+450=500. Body 550. Gap is 50px.
        # Maybe the user implies standard layout where Face is smaller or offset?
        # "Between Image Frames" -> e.g. Face Top Left, Body Right. Data in between?
        # Let's assume there is space.
        
        # Coordinates based on user: "Left Large Square", "Right Vertical".
        # We will maximize coverage.
        
        img = Image.new("RGBA", CANVAS_1, (255, 255, 255, 255))
        
        # Images (Bottom Layer)
        # Img 1: Face (Left)
        if len(char['images']) > 0:
            i1 = load_image_cover(char['images'][0], (450, 450))
            img.paste(i1, (50, 120)) # Slight offset Y
            
        # Img 2: Full (Right)
        if len(char['images']) > 1:
            i2 = load_image_cover(char['images'][1], (400, 650))
            img.paste(i2, (570, 120)) # x=570 to leave room?
            
        # Template (Top Layer)
        details = char.get('details', {})
        race = details.get('race', '人間')
        template_map = {
            "人間": ("sim_profile_hum.png", "#333333"),
            "魔族": ("sim_profile_魔族.png", "#FFFFFF"),
            "聖族": ("sim_profile_聖族.png", "#444444"),
            "その他": ("sim_profile_hum.png", "#333333")
        }
        t_file, txt_col = template_map.get(race, ("sim_profile_hum.png", "#333333"))
        t_path = os.path.join("templates", t_file)
        if os.path.exists(t_path):
            tm = Image.open(t_path).convert("RGBA").resize(CANVAS_1)
            img.paste(tm, (0, 0), mask=tm)
            
        draw = ImageDraw.Draw(img)
        
        # Data Draw
        # "Between Images" -> Top area between?
        # Gap is approx x=500~570. very narrow (70px).
        # Maybe layout is: Face (50,120) ... Body (670, 120)?
        # Let's assume the template has designated holes.
        # Actually user said: "Between Image Frames: Age, Race, Eye, Hair".
        # This implies a central column? Or Vertical stack between them?
        # If the gap is small, maybe it overlaps?
        # I'll put them in a safe box x=520, y=120?
        
        # Actually, let's use the layout:
        # Left Frame: x=50, w=450. Right Frame: x=600, w=350?
        # Let's guess spacing.
        
        # Data: Between
        cx = 530
        cy = 130
        h_step = 60
        
        draw_text(draw, f"Age: {details.get('age','-')}", (cx, cy), get_font(20), txt_col)
        draw_text(draw, f"Race: {race}", (cx, cy+h_step), get_font(20), txt_col)
        
        # Eye
        draw_text(draw, "Eye:", (cx, cy+h_step*2), get_font(20), txt_col)
        ec = details.get('eye_color', '-')
        if ec.startswith('#'):
            draw.rectangle((cx, cy+h_step*2+30, cx+30, cy+h_step*2+60), fill=ec, outline="black")
            draw_text(draw, ec, (cx+40, cy+h_step*2+30), get_font(16), txt_col)
        
        # Hair
        draw_text(draw, "Hair:", (cx, cy+h_step*3+30), get_font(20), txt_col)
        hc = details.get('hair_color', '-')
        if hc.startswith('#'):
            draw.rectangle((cx, cy+h_step*3+60, cx+30, cy+h_step*3+90), fill=hc, outline="black")
            draw_text(draw, hc, (cx+40, cy+h_step*3+60), get_font(16), txt_col)
            
        # Data: Below Left Frame (y > 570)
        lx = 80
        ly = 600
        
        # Name (First Last)
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname} {lname}".strip() or char.get('name', '')
        draw_text(draw, f"Name: {full}", (lx, ly), get_font(30), txt_col)
        
        # Class
        draw_text(draw, f"Class: {details.get('role','-')}", (lx, ly+50), get_font(24), txt_col)
        
        # Height/Weight
        draw_text(draw, f"H/W: {details.get('height_weight','-')}", (lx, ly+90), get_font(24), txt_col)
        
        # Affiliation
        draw_text(draw, f"Affiliation: {details.get('origin','-')}", (lx, ly+130), get_font(24), txt_col)
        
        # Memo (Bottom)
        # New Field "memo_profile" ? Or just use 'memo'. User said "Simple Setting (Profile Memo)".
        # I'll look for 'memo' in details.
        
        memo = details.get('memo', '')
        # Counter? Handled in UI. Here just draw.
        # Box: Bottom x=80, w=860
        draw_text_wrapped(draw, memo, 80, 800, 860, get_font(22), txt_col)
        
        return img

    # --- CARD 2: Stats (1024x768) ---
    def create_card_2():
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
            
        draw = ImageDraw.Draw(bg)
        draw_decorations(draw, 1024, 768)
        
        # Layout: Left = Basic, Right = Personality.
        # Padding 40px all around.
        
        # User Name: Above Top Line.
        un = char.get('user_name', '')
        if un: draw.text((512, 30), f"User: {un}", font=f_small, fill="gray", anchor="mm")
        
        # Char Name: Inside Frame (y=80?)
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname} {lname}".strip() or char.get('name', '')
        draw.text((512, 80), full, font=f_med, fill="#3e2723", anchor="mm") # Smaller font
        
        # Charts
        # Left Center: x=256. Right Center: x=768.
        # But padding 40px?
        # Just use 25% and 75%.
        
        lbl_b = ["知力", "体力", "魔力", "防御力", "行動力", "攻撃力", "自信"]
        # Title Above Chart (y=150)
        draw.text((256, 150), "基礎能力", font=f_med, fill="#3e2723", anchor="mm")
        # Chart (y=300)
        draw_radar(bg, (256, 300), 120, char.get('stats', {}), lbl_b, (30, 136, 229, 80), (30, 136, 229, 255))
        
        lbl_p = ["積極性", "協調性", "慎重さ", "適応力", "精神力", "寛容さ", "道徳・倫理観", "社交性"]
        draw.text((768, 150), "性格傾向", font=f_med, fill="#3e2723", anchor="mm")
        draw_radar(bg, (768, 300), 120, char.get('personality_stats', {}), lbl_p, (229, 57, 53, 80), (229, 57, 53, 255))
        
        # Bottom Text: "Detail Summary"
        # y=500
        dx = 60
        dy = 500
        draw.text((dx, dy), "【詳細概要】", font=f_med, fill="#3e2723")
        
        bio = char.get('bio_short', '') or char.get('bio', '')[:250]
        draw_text_wrapped(draw, bio, dx, dy+40, 900, f_small, "#212121")
        
        return bg

    # --- CARD 3: Gallery (1024x768) ---
    def create_card_3():
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
            
        draw = ImageDraw.Draw(bg)
        draw_decorations(draw, 1024, 768) # Decorations on background
        
        # Romaji Name (Top Center)
        en = char.get('name_en', '')
        if en:
            draw.text((512, 40), en, font=f_romaji, fill="#3e2723", anchor="mm")
            
        # Images (Below Header, Above Body)
        # Layout: 1024 width.
        # Img3 (Left), Img4 (Center), Img5 (Right) all top?
        # Or mixed?
        # User said: "Img 3... Left Large? Right Vertical?" No that was Card 1.
        # Previous Card 3 was: Img 3 (L), Img 4 (C), Img 5 (R), Img 6 (Bot).
        # Let's stick to that but ensure loading.
        
        imgs = char.get('images', [])
        
        # Img 3
        if len(imgs) > 2 and imgs[2]:
            p = load_image_cover(imgs[2], (300, 500))
            bg.paste(p, (40, 120))
            
        # Img 4
        if len(imgs) > 3 and imgs[3]:
            p = load_image_cover(imgs[3], (300, 240))
            bg.paste(p, (360, 120))
            
        # Img 6 (Center Bot)
        if len(imgs) > 5 and imgs[5]:
            p = load_image_cover(imgs[5], (300, 240))
            bg.paste(p, (360, 380))
            
        # Img 5 (Right Top)
        if len(imgs) > 4 and imgs[4]:
            p = load_image_cover(imgs[4], (300, 240))
            bg.paste(p, (680, 120))
            
        # Template Overlay (Top)
        gp = os.path.join("templates", "SNS-3.png")
        if os.path.exists(gp):
            tmpl = Image.open(gp).convert("RGBA").resize(CANVAS_LANDSCAPE)
            bg.paste(tmpl, (0, 0), mask=tmpl)
            
        # Draw Context again for Text on Top
        draw = ImageDraw.Draw(bg)
        
        # Relations (Bottom Right)
        # 4 Slots
        # Area: x=680, y=380 (Below Img 5)
        # Grid 2x2.
        
        rels = char.get('relations', [])[:4]
        positions = [(680, 400), (830, 400), (680, 560), (830, 560)]
        
        all_chars = {c['id']: c for c in manager.characters}
        
        for i, r in enumerate(rels):
            bx, by = positions[i]
            
            # 1. Type (Top)
            rtype = r.get('type', '').split('/')[0]
            draw.text((bx+75, by+10), rtype, font=get_font(16), fill="#5d4037", anchor="mm")
            
            # 2. Icon (Middle)
            tid = r.get('target_id')
            tgt = all_chars.get(tid)
            
            ic_sz = 80
            if tgt and tgt.get('images'):
                ic = load_image_cover(tgt['images'][0], (ic_sz, ic_sz))
            else:
                ic = Image.new("RGBA", (ic_sz, ic_sz), (220, 220, 220, 255))
                di = ImageDraw.Draw(ic)
                di.text((40, 40), "Now", fill="gray", font=get_font(14), anchor="mm")
            
            mask = Image.new("L", (ic_sz, ic_sz), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, ic_sz, ic_sz), fill=255)
            
            bg.paste(ic, (bx+35, by+30), mask=mask)
            
            # 3. Name (Bottom) - First Only
            if tgt:
                tname = tgt.get('first_name', tgt.get('name', ''))
            else:
                tname = r.get('target_name', '')
                
            tname = tname.split()[0] # Force first
            draw.text((bx+75, by+120), tname, font=get_font(18), fill="#3e2723", anchor="mm")
            
        return bg

    # Execution
    try:
        i1 = create_card_1()
        i2 = create_card_2()
        i3 = create_card_3()
        
        b = io.BytesIO()
        with zipfile.ZipFile(b, "a", zipfile.ZIP_DEFLATED, False) as z:
            bu = io.BytesIO(); i1.convert("RGB").save(bu, "JPEG"); z.writestr(f"{char['name']}_profile.jpg", bu.getvalue())
            bu2 = io.BytesIO(); i2.convert("RGB").save(bu2, "JPEG"); z.writestr(f"{char['name']}_stats.jpg", bu2.getvalue())
            bu3 = io.BytesIO(); i3.convert("RGB").save(bu3, "JPEG"); z.writestr(f"{char['name']}_gallery.jpg", bu3.getvalue())
        b.seek(0)
        return b
    except Exception as e:
        print(e)
        return None
'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

s_mark = "def generate_card_zip(char, manager):"
e_mark = "def render_relation_page(manager):"

s_idx = content.find(s_mark)
e_idx = content.find(e_mark)

if s_idx != -1 and e_idx != -1:
    new_c = content[:s_idx] + new_function + "\n\n" + content[e_idx:]
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_c)
    print("Updated")
else:
    print("Markers not found")
