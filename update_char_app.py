
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

new_function_code = r'''def generate_card_zip(char, manager):
    import io
    import zipfile
    import os
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
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
            return ImageFont.truetype(FONT_PATH, int(size))
        except:
            return ImageFont.load_default()

    f_small = get_font(24)
    f_med = get_font(30)
    f_large = get_font(50)
    f_romaji = get_font(40)

    def draw_text(draw, text, position, font, fill="#333333", anchor="la"):
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

    def draw_decorations(draw, w, h):
        if os.path.exists(CORNER_PATH):
            try:
                # Load Source (Assume TL)
                src = Image.open(CORNER_PATH).convert("RGBA").resize((150, 150))
                data = []
                for item in src.getdata():
                    if item[0]>200 and item[1]>200 and item[2]>200:
                        data.append((255, 255, 255, 0))
                    else:
                        data.append(item)
                src.putdata(data)
                
                # Logic: Clockwise Shift
                tl = src.rotate(90)
                tr = src
                br = src.rotate(270) 
                bl = src.rotate(180)
                
                draw._image.paste(tl, (0, 0), tl)
                draw._image.paste(tr, (w-150, 0), tr)
                draw._image.paste(bl, (0, h-150), bl)
                draw._image.paste(br, (w-150, h-150), br)
                
            except:
                pass
        
        draw.rectangle((40, 40, w-40, h-40), outline="#5d4037", width=2)
        draw.text((w//2, h-30), "Legend of Crystarosh", font=get_font(16), fill="#333333", anchor="mm")

    def draw_radar(base_img, center, radius, stats, labels, color_fill, color_line, title):
        draw = ImageDraw.Draw(base_img)
        n = len(labels)
        angle_step = 2 * math.pi / n
        start_angle = -math.pi / 2
        
        draw.text((center[0], center[1] - radius - 70), title, font=get_font(24), fill="#3e2723", anchor="mm")
        
        for i in range(1, 6):
            r = radius * (i/5)
            pts = []
            for j in range(n):
                ang = start_angle + j * angle_step
                pts.append((center[0] + r*math.cos(ang), center[1] + r*math.sin(ang)))
            draw.polygon(pts, outline="#AAAAAA")
        
        for j in range(n):
            ang = start_angle + j * angle_step
            end = (center[0] + radius*math.cos(ang), center[1] + radius*math.sin(ang))
            draw.line([center, end], fill="#AAAAAA")
            lx = center[0] + (radius+20)*math.cos(ang)
            ly = center[1] + (radius+20)*math.sin(ang)
            anchor = "mm"
            if math.cos(ang) > 0.2: anchor="lm"
            elif math.cos(ang) < -0.2: anchor="rm"
            draw.text((lx, ly), labels[j], fill="#333", font=get_font(16), anchor=anchor)

        vals = [int(stats.get(l, 3)) for l in labels]
        pts = []
        for j in range(n):
            v = min(vals[j], 5)
            r = radius * (v/5)
            ang = start_angle + j * angle_step
            pts.append((center[0] + r*math.cos(ang), center[1] + r*math.sin(ang)))
            
        if len(pts) > 2:
            poly_layer = Image.new("RGBA", base_img.size, (0,0,0,0))
            pdraw = ImageDraw.Draw(poly_layer)
            pdraw.polygon(pts, fill=color_fill)
            base_img.alpha_composite(poly_layer)
            draw.polygon(pts, outline=color_line, width=2)

    # --- CARD 1: Profile (1024x1024) ---
    def create_card_1():
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
            img = Image.open(t_path).convert("RGBA").resize(CANVAS_1)
        else:
            img = Image.new("RGBA", CANVAS_1, (255, 255, 255, 255))
            
        # Images: Up another 10px -> Y = 117 - 10 = 107.
        if len(char['images']) > 0:
            draw_shadowed_rounded_image(img, char['images'][0], (125, 107, 360, 360), radius=20)
        if len(char['images']) > 1:
            draw_shadowed_rounded_image(img, char['images'][1], (644, 107, 320, 520), radius=20, centering=(0.5, 0.2))

        draw = ImageDraw.Draw(img)
        
        # Left Column (Under Square)
        # Y Offset: 502 - 10 = 492.
        lx = 125
        ly = 492
        
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        # Separator '・'
        full = f"{fname}・{lname}" if fname and lname else char.get('name', '')
        
        font_lbl = get_font(16)
        font_val = get_font(22)
        font_name = get_font(30)
        font_code = get_font(14)
        
        # Name
        draw.text((lx, ly), "Name:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly-5), full, font=font_name, fill=txt_col, anchor="la")
        ly += 50
        
        # Age
        draw.text((lx, ly), "Age:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly), details.get('age', '-'), font=font_val, fill=txt_col, anchor="la")
        ly += 40

        # Class
        draw.text((lx, ly), "Class:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly), details.get('role', '-'), font=font_val, fill=txt_col, anchor="la")
        ly += 40
        
        # H/W
        draw.text((lx, ly), "H/W:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly), details.get('height_weight', '-'), font=font_val, fill=txt_col, anchor="la")
        ly += 40
        
        # Affil
        draw.text((lx, ly), "Affil:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly), details.get('origin', '-'), font=font_val, fill=txt_col, anchor="la")

        # Center Gap (Race, Eye, Hair, Image)
        # Start Y = 190 -> 180 (Move up 10px? User said images up. Texts usually follow. I will move up 10px.)
        # Y=180.
        cx = 564
        cy = 180
        step_y = 65
        
        # Race
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

        # Eye
        draw_color_row("Eye", details.get('eye_color', '-'), cy)
        cy += step_y
        
        # Hair
        draw_color_row("Hair", details.get('hair_color', '-'), cy)
        cy += step_y
        
        # Image Color
        draw_color_row("Image Color", details.get('image_color', '-'), cy)

        # User Name: Remove @ (Just {un})
        un = char.get('user_name', '')
        if un: draw_text(draw, f"{un}", (950, 40), get_font(24), fill=txt_col, anchor="ra")
            
        # Memo: Y=780. Keep same.
        memo_col = "#333333"
        memo_y = 780
        draw.text((80, memo_y), "【簡易設定】", font=get_font(20), fill=memo_col, anchor="la")
        draw_text_wrapped(draw, details.get('memo', ''), 80, memo_y+40, 864, get_font(18), memo_col)
        
        return img

    # --- CARD 2: Stats (1024x768) ---
    def create_card_2():
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
        draw = ImageDraw.Draw(bg)
        
        # User Name: Move Above Frame (Y=25)
        un = char.get('user_name', '')
        if un: draw.text((512, 25), f"User: {un}", font=get_font(18), fill="gray", anchor="mm")
        
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname}・{lname}" if fname and lname else char.get('name', '')
        draw.text((512, 90), full, font=get_font(40), fill="#3e2723", anchor="mm")

        draw_decorations(draw, 1024, 768) 
        
        lbl_b = ["知力", "体力", "魔力", "防御力", "行動力", "攻撃力", "自信"]
        draw_radar(bg, (256, 330), 104, char.get('stats', {}), lbl_b, (30, 136, 229, 80), (30, 136, 229, 255), "基礎能力")
        
        lbl_p = ["積極性", "協調性", "慎重さ", "適応力", "精神力", "寛容さ", "道徳・倫理観", "社交性"]
        draw_radar(bg, (768, 330), 104, char.get('personality_stats', {}), lbl_p, (229, 57, 53, 80), (229, 57, 53, 255), "性格傾向")
        
        draw.text((90, 500), "【詳細概要】", font=get_font(24), fill="#3e2723", anchor="la")
        bio = char.get('bio_short', '') or char.get('bio', '')[:250]
        draw_text_wrapped(draw, bio, 90, 540, 844, get_font(14), "#212121")

        return bg

    # --- CARD 3: Gallery (1024x768) ---
    def create_card_3():
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
        draw = ImageDraw.Draw(bg)
        
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname}・{lname}" if fname and lname else char.get('name', '')
        draw.text((512, 80), full, font=get_font(35), fill="#3e2723", anchor="mm")

        draw_decorations(draw, 1024, 768) 
        
        imgs = char.get('images', [])
        
        start_x = 112
        y_pos = 120
        
        if len(imgs) > 2 and imgs[2]:
            draw_shadowed_rounded_image(bg, imgs[2], (start_x, y_pos, 240, 480), radius=15, centering=(0.5, 0.2))
            
        sq_x1 = start_x + 280
        sq_x2 = sq_x1 + 280
        
        if len(imgs) > 3 and imgs[3]:
             draw_shadowed_rounded_image(bg, imgs[3], (sq_x1, y_pos, 240, 240), radius=15)
        if len(imgs) > 4 and imgs[4]:
             draw_shadowed_rounded_image(bg, imgs[4], (sq_x2, y_pos, 240, 240), radius=15)
        if len(imgs) > 5 and imgs[5]:
             draw_shadowed_rounded_image(bg, imgs[5], (sq_x1, y_pos + 280, 240, 240), radius=15)
             
        rel_x = sq_x2
        rel_y = y_pos + 280 
        
        draw.text((rel_x, rel_y), "【人間関係】", font=get_font(20), fill="#3e2723", anchor="lt")
        
        rels = char.get('relations', [])[:4]
        for i, r in enumerate(rels):
             col = i % 2
             row = i // 2
             bx = rel_x + col * 110
             by = rel_y + 40 + row * 110
             
             tid = r.get('target_id')
             all_chars = {c['id']: c for c in manager.characters}
             tgt = all_chars.get(tid)
             
             icon_sz = 60
             if tgt and tgt.get('images'):
                 ic = Image.open(tgt['images'][0]).convert("RGBA")
                 ic = ImageOps.fit(ic, (icon_sz, icon_sz))
             else:
                 ic = Image.new("RGBA", (icon_sz, icon_sz), (220, 220, 220, 255))
            
             mask = Image.new("L", (icon_sz, icon_sz), 0)
             ImageDraw.Draw(mask).ellipse((0, 0, icon_sz, icon_sz), fill=255)
            
             bg.paste(ic, (bx, by), mask=mask)
             
             if tgt:
                tname = tgt.get('first_name', tgt.get('name', ''))
             else:
                tname = r.get('target_name', '')
             tname = tname.split()[0]
             
             draw.text((bx+30, by+70), tname, font=get_font(12), fill="#3e2723", anchor="mm")

        return bg

    # --- Execution ---
    try:
        img1 = create_card_1()
        img2 = create_card_2()
        img3 = create_card_3()
        
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False) as zf:
             b1 = io.BytesIO(); img1.convert("RGB").save(b1, "JPEG"); 
             zf.writestr(f"{char['name']}_profile.jpg", b1.getvalue())
             b2 = io.BytesIO(); img2.convert("RGB").save(b2, "JPEG");
             zf.writestr(f"{char['name']}_stats.jpg", b2.getvalue())
             b3 = io.BytesIO(); img3.convert("RGB").save(b3, "JPEG");
             zf.writestr(f"{char['name']}_gallery.jpg", b3.getvalue())
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Error generating cards: {e}")
        return None
'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "def generate_card_zip(char, manager):"
end_marker = "def render_relation_page(manager):"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_function_code + "\n\n" + content[end_idx:]
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced generate_card_zip")
else:
    print("Could not find markers")
