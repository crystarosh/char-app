
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# THE V16 FUNCTION
v16_code = r'''def generate_card_zip(char, manager):
    import io
    import zipfile
    import os
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    import math

    # --- DEBUG LOGS ---
    print(f"DEBUG: 起動しました - キャラ名: {char.get('name')}")
    print(f"DEBUG: 画像リスト(imgs): {char.get('images', [])}")

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

    def draw_text_wrapped(draw, text, x, y, max_h, max_w, font, fill, align="left"):
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
        start_y = y + (max_h - total_h) // 2   
        current_y = start_y
        for l in lines:
            draw.text((x, current_y), l, font=font, fill=fill)
            current_y += line_height
        return current_y

    def load_image_masked(path, size, radius=0, centering=(0.5, 0.5)):
        try:
            img = Image.open(path).convert("RGBA")
            img = ImageOps.fit(img, size, method=Image.LANCZOS, centering=centering)
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


    # --- 1. PROFILE CARD ---
    def create_card_1():
        print(f"DEBUG: Creating Card 1 for {char.get('name')}")
        details = char.get('details', {})
        race = details.get('race', '人間')
        
        # COLOR LOGIC (Separated)
        if race == "魔族":
            txt_col = "#FFFFFF" # White for Top Info
        else:
            txt_col = "#333333" # Dark Gray for Top Info

        # Memo is ALWAYS Dark Gray
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
            
        if len(char['images']) > 0:
            if char['images'][0] and os.path.exists(char['images'][0]):
                i1 = load_image_masked(char['images'][0], (400, 400), radius=0, centering=(0.5, 0.5))
                img.paste(i1, (110, 110), i1)
        if len(char['images']) > 1:
             if char['images'][1] and os.path.exists(char['images'][1]):
                i2 = load_image_masked(char['images'][1], (240, 600), radius=0, centering=(0.5, 0.2))
                img.paste(i2, (720, 110), i2)
            
        # Top Text using txt_col
        draw = ImageDraw.Draw(img)
        lx = 80
        curr_y = 520 
        fname = char.get('first_name', '')
        lname = char.get('last_name', '')
        full = f"{fname} {lname}".strip() or char.get('name', '')
        
        draw_text(draw, f"Name: {full}", (lx, curr_y), get_font(30), txt_col)
        curr_y += 50
        draw_text(draw, f"Class: {details.get('role','-')}", (lx, curr_y), get_font(24), txt_col)
        curr_y += 40
        draw_text(draw, f"H/W: {details.get('height_weight','-')}", (lx, curr_y), get_font(24), txt_col)
        curr_y += 40
        draw_text(draw, f"Affiliation: {details.get('origin','-')}", (lx, curr_y), get_font(24), txt_col)
        
        cx = 530
        cy = 130
        step = 60
        draw_text(draw, f"Age: {details.get('age','-')}", (cx, cy), get_font(20), txt_col)
        draw_text(draw, f"Race: {race}", (cx, cy+step), get_font(20), txt_col)
        draw_text(draw, "Eye:", (cx, cy+step*2), get_font(20), txt_col)
        ec = details.get('eye_color', '-')
        if ec.startswith('#'):
             draw.rectangle((cx, cy+step*2+30, cx+30, cy+step*2+60), fill=ec, outline="black")
             draw_text(draw, ec, (cx+40, cy+step*2+30), get_font(16), txt_col)
        draw_text(draw, "Hair:", (cx, cy+step*3+30), get_font(20), txt_col)
        hc = details.get('hair_color', '-')
        if hc.startswith('#'):
             draw.rectangle((cx, cy+step*3+60, cx+30, cy+step*3+90), fill=hc, outline="black")
             draw_text(draw, hc, (cx+40, cy+step*3+60), get_font(16), txt_col)
             
        # Memo using memo_col (Dark Gray)
        memo_raw = details.get('profile_memo', details.get('memo', ''))
        memo = ""
        if memo_raw:
             memo = "【簡易設定】\n" + memo_raw
        
        draw_text_wrapped(draw, memo, 80, 790, 140, 860, get_font(22), memo_col)
        return img

    # --- 2. STATS CARD ---
    def create_card_2():
        print("DEBUG: Creating Card 2")
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
        full = f"{fname} {lname}".strip() or char.get('name', '')
        draw.text((512, 60), full, font=f_med, fill="#3e2723", anchor="mm")
        
        chart_y = 300
        lbl_b = ["知力", "体力", "魔力", "防御力", "行動力", "攻撃力", "自信"]
        draw.text((256, 100), "基礎能力", font=f_med, fill="#3e2723", anchor="mm")
        draw_radar(bg, (256, chart_y), 120, char.get('stats', {}), lbl_b, (30, 136, 229, 80), (30, 136, 229, 255))
        
        lbl_p = ["積極性", "協調性", "慎重さ", "適応力", "精神力", "寛容さ", "道徳・倫理観", "社交性"]
        draw.text((768, 100), "性格傾向", font=f_med, fill="#3e2723", anchor="mm")
        draw_radar(bg, (768, chart_y), 120, char.get('personality_stats', {}), lbl_p, (229, 57, 53, 80), (229, 57, 53, 255))
        
        dx = 60
        dy = 500
        draw.text((dx, dy), "【詳細概要】", font=f_med, fill="#3e2723")
        bio = char.get('bio_short', '') or char.get('bio', '')[:250]
        draw_text_wrapped(draw, bio, dx, dy+60, 200, 900, get_font(16), "#212121")
        
        draw.text((512, 750), "Legend of Crystarosh", font=get_font(12), fill="#5d4037", anchor="mm")
        return bg

    # --- 3. GALLERY CARD ---
    def create_card_3():
        print("DEBUG: Creating Card 3")
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
            
        imgs = char.get('images', [])
        def gv(i):
             if i<len(imgs) and imgs[i] and os.path.exists(imgs[i]): return imgs[i]
             return None
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
             
        gp = os.path.join("templates", "SNS-3.png")
        if os.path.exists(gp):
            tmpl = Image.open(gp).convert("RGBA").resize(CANVAS_LANDSCAPE)
            tmpl = make_transparent(tmpl)
            bg.paste(tmpl, (0, 0), mask=tmpl)
            
        draw = ImageDraw.Draw(bg)
        draw_decorations(draw, 1024, 768)
        
        en = char.get('name_en', '')
        if en: draw.text((512, 30), en, font=f_med, fill="#3e2723", anchor="mm")
        
        draw.text((680, 360), "【人間関係】", font=f_med, fill="#3e2723")
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
            bu = io.BytesIO(); i1.convert("RGB").save(bu, "JPEG"); z.writestr(f"{char['name']}_profile.jpg", bu.getvalue())
            bu2 = io.BytesIO(); i2.convert("RGB").save(bu2, "JPEG"); z.writestr(f"{char['name']}_stats.jpg", bu2.getvalue())
            bu3 = io.BytesIO(); i3.convert("RGB").save(bu3, "JPEG"); z.writestr(f"{char['name']}_gallery.jpg", bu3.getvalue())
        b.seek(0)
        return b
    except Exception as e:
        print(f"Gen Error: {e}")
        return None
'''

# 1. Read
content = None
for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'cp932', 'latin1']:
    try:
        with open(target_file, 'r', encoding=enc) as f:
            content = f.read()
            break
    except:
        continue
if not content: raise Exception("Fail read")

# 2. Replace
start_markers = ["def generate_card_zip"]
start_pos = -1
for sm in start_markers:
    pos = content.find(sm)
    if pos != -1:
        start_pos = pos
        break
end_pos = content.find("def render_relation_page")

if start_pos != -1 and end_pos != -1:
    pre = content[:start_pos]
    post = content[end_pos:]
    new_content = pre + v16_code + "\n\n" + post
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("V16 Profile Color Update Applied.")
else:
    print("Boundaries error")
