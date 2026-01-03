
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# THE V23 CODE
v23_code = r'''def generate_card_zip(char, manager):
    import io
    import zipfile
    import os
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
    import math
    import string

    # --- V23 FINAL ADJUSTMENTS ---
    print(f"DEBUG: V23 - {char.get('name')}")

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

    def draw_text_wrapped(draw, text, x, y, max_h, max_w, font, fill, align="left", valign="top"):
        if not text: return y
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
        
        start_y = y
        if valign == "center":
            # Center within max_h
            start_y = y + (max_h - total_h) // 2
        
        current_y = start_y
        for l in lines:
            draw.text((x, current_y), l, font=font, fill=fill)
            current_y += line_height
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
        
    def draw_radar(base_img, center, radius, stats, labels, color_fill, color_line):
        draw = ImageDraw.Draw(base_img)
        n = len(labels)
        angle_step = 2 * math.pi / n
        start_angle = -math.pi / 2
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
            lx = center[0] + (radius+25)*math.cos(ang)
            ly = center[1] + (radius+25)*math.sin(ang)
            anchor = "mm"
            if math.cos(ang) > 0.2: anchor="lm"
            elif math.cos(ang) < -0.2: anchor="rm"
            draw.text((lx, ly), labels[j], fill="#333", font=get_font(20), anchor=anchor)

        vals = [int(stats.get(l, 3)) for l in labels]
        pts = []
        for j in range(n):
            v = min(vals[j], 5)
            r = radius * (v/5)
            if v > 5: r = radius * (6/5)
            ang = start_angle + j * angle_step
            pts.append((center[0] + r*math.cos(ang), center[1] + r*math.sin(ang)))
        if len(pts) > 2:
            poly_layer = Image.new("RGBA", base_img.size, (0,0,0,0))
            pdraw = ImageDraw.Draw(poly_layer)
            pdraw.polygon(pts, fill=color_fill) 
            base_img.alpha_composite(poly_layer)
            draw.polygon(pts, outline=color_line, width=2)
            
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

    # --- 1. PROFILE CARD (V23) ---
    def create_card_1():
        print(f"DEBUG: Creating Card 1 for {char.get('name')}")
        details = char.get('details', {})
        race = details.get('race', '人間')
        
        if race == "魔族":
            txt_col = "#FFFFFF"
        else:
            txt_col = "#333333"
        memo_col = "#333333"
            
        template_map = {
            "人間": "sim_profile_hum.png",
            "魔族": "sim_profile_魔族.png",
            "聖族": "sim_profile_聖族.png",
            "その他": "sim_profile_hum.png"
        }
        t_file = template_map.get(race, "sim_profile_hum.png")
        t_path = os.path.join("templates", t_file)
        if os.path.exists(t_path):
            img = Image.open(t_path).convert("RGBA").resize(CANVAS_1)
        else:
            img = Image.new("RGBA", CANVAS_1, (255, 255, 255, 255))
            
        img1_box = (125, 107, 360, 360)
        
        # ALIGNED IMAGE 2:
        # Memo block: 80 + 864 = 944 Right Edge.
        # Image 2 Width: 320.
        # New X = 944 - 320 = 624.
        img2_box = (624, 107, 320, 520)
        
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
        # Separator Added
        full = f"{fname}・{lname}" if fname and lname else char.get('name', '')
        
        font_lbl = get_font(16)
        font_val = get_font(22)
        font_name = get_font(30)
        font_code = get_font(14)
        
        # LEFT COL: Name -> Age -> Class -> H/W -> Affil
        # Name
        draw.text((lx, ly), "Name:", font=font_lbl, fill=txt_col, anchor="la")
        draw.text((lx+60, ly-5), full, font=font_name, fill=txt_col, anchor="la")
        ly += 50
        
        # Age (Moved here from Center)
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
        
        
        # CENTER COL: Race -> Eye -> Hair -> Image Color (Added)
        # Shifted X to avoid overlapping Name? 
        # cx = 564. Name is at lx=125.
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
        
        # Image Color (Added)
        draw_color_row("Image Color", details.get('image_color', '-'), cy)

        # User Name: NO @ prefix independently. 
        un = char.get('user_name', '')
        if un: draw_text(draw, un, (950, 40), get_font(24), fill=txt_col, anchor="ra")
             
        # Memo: Centered Vertically in block
        # Block Y: 780. Bottom: ? 
        # Template usually has bottom margin? 
        # Let's say block height is approx 1024 - 780 - 40 = ~200.
        memo_y = 780
        draw.text((80, memo_y), "【簡易設定】", font=get_font(20), fill=memo_col, anchor="la")
        
        # Use valign="center" with explicit max_h
        # Canvas H = 1024. Memo start ~820 (text)
        max_h = 1024 - (memo_y + 40) - 20 # 184px
        draw_text_wrapped(draw, details.get('memo', ''), 80, memo_y+40, max_h, 864, get_font(18), memo_col, valign="center")
        
        return img

    # --- 2. STATS CARD (V23) ---
    def create_card_2():
        print("DEBUG: Creating Card 2 (V23)")
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
        
        # V23: Radar Shrink (130 -> 110) & Move Up (380 -> 350)
        chart_y = 350 
        chart_r = 110 
        
        lbl_b = ["知力", "体力", "魔力", "防御力", "行動力", "攻撃力", "自信"]
        draw.text((256, 120), "基礎能力", font=f_med, fill="#3e2723", anchor="mm") 
        draw_radar(bg, (256, chart_y), chart_r, char.get('stats', {}), lbl_b, (30, 136, 229, 80), (30, 136, 229, 255))
        
        lbl_p = ["積極性", "協調性", "慎重さ", "適応力", "精神力", "寛容さ", "道徳・倫理観", "社交性"]
        draw.text((768, 120), "性格傾向", font=f_med, fill="#3e2723", anchor="mm")
        draw_radar(bg, (768, chart_y), chart_r, char.get('personality_stats', {}), lbl_p, (229, 57, 53, 80), (229, 57, 53, 255))
        
        # V23: Bio Margins Increased (Avoid Corners)
        # Using X=130 (V21 value, safer)
        # Y moved down for "yutori" (Space from radar). Radar Bottom = 350+110+Labels = ~500.
        # Set Title Y = 540.
        dx = 130
        dy = 540
        draw.text((dx, dy), "【詳細概要】", font=f_med, fill="#3e2723") 
        bio = char.get('bio_short', '') or char.get('bio', '')[:250]
        
        # Gap 45px (V21)
        max_w = 1024 - (dx * 2) # Centered
        draw_text_wrapped(draw, bio, dx, dy+45, 200, max_w, get_font(16), "#212121")
        
        draw.text((512, 750), "Legend of Crystarosh", font=get_font(12), fill="#5d4037", anchor="mm")
        
        return bg

    # --- 3. GALLERY CARD (V23) ---
    def create_card_3():
        print("DEBUG: Creating Card 3 (V23)")
        # Design: Stats Same (Texture + Corners)
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
            
        imgs = char.get('images', [])
        def gv(i): return imgs[i] if i<len(imgs) and imgs[i] and os.path.exists(imgs[i]) else None
        p2, p3, p4, p5 = gv(2), gv(3), gv(4), gv(5)
        
        R = 30
        if p2:
             i = load_image_masked(p2, (300, 600), radius=R, centering=(0.7, 0.5))
             bg.paste(i, (40, 100), i)
        if p3:
             i = load_image_masked(p3, (300, 290), radius=R)
             bg.paste(i, (360, 100), i)
        if p4:
             i = load_image_masked(p4, (300, 290), radius=R)
             bg.paste(i, (680, 100), i)
        if p5:
             i = load_image_masked(p5, (300, 290), radius=R)
             bg.paste(i, (360, 410), i)
             
        # Template: NOT USED (Design = Stats)
        # But user said "refer to SNS-3.png for placement".
        # We are using placement derived from it.
            
        draw = ImageDraw.Draw(bg)
        draw_decorations(draw, 1024, 768)
        
        en = char.get('name_en', '')
        if en: draw.text((512, 30), en, font=f_med, fill="#3e2723", anchor="mm")
        
        # Header: Name. avoid border. Y=80 -> Y=60 (Moved Up)
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname}・{lname}" if fname and lname else char.get('name', '')
        draw.text((512, 60), full, font=f_med, fill="#3e2723", anchor="mm")
        
        draw.text((830, 395), "【メイン人間関係】", font=get_font(20), fill="#3e2723", anchor="mm") 
        
        rels = char.get('relations', [])[:4]
        positions = [(680, 440), (830, 440), (680, 580), (830, 580)]
        all_chars = {c['id']: c for c in manager.characters}
        
        for i, r in enumerate(rels):
            if i>=4: break
            bx, by = positions[i]
            rtype = r.get('type', '').split('/')[0]
            draw.text((bx+75, by), rtype, font=get_font(14), fill="#5d4037", anchor="mm")
            
            tid = r.get('target_id')
            tgt = all_chars.get(tid)
            ic_sz = 70
            
            ic = None
            if tgt and tgt.get('images') and tgt['images'][0] and os.path.exists(tgt['images'][0]):
                 ic = load_image_masked(tgt['images'][0], (ic_sz, ic_sz), radius=10)
            else:
                 ic = Image.new("RGBA", (ic_sz, ic_sz), (220, 220, 220, 255))
            
            bg.paste(ic, (bx+40, by+20), ic)
            
            if tgt: tname = tgt.get('first_name', tgt.get('name', ''))
            elif r.get('target_name'): tname = r.get('target_name', '')
            else: tname = "Unknown"
            
            tname = tname.split()[0]
            draw.text((bx+75, by+105), tname, font=get_font(16), fill="#3e2723", anchor="mm")

        draw.text((512, 750), "Legend of Crystarosh", font=get_font(12), fill="#5d4037", anchor="mm")
            
        return bg

    try:
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
    except Exception as e:
        print(f"Gen Error: {e}")
        return None
'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

import re
pattern = re.compile(r"^def generate_card_zip.*?^(?=def |if __name__)", re.MULTILINE | re.DOTALL)
match = pattern.search(content)

if match:
    new_content = content[:match.start()] + v23_code + "\n\n" + content[match.end():]
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("V23 Applied.")
else:
    print("Error finding block.")
