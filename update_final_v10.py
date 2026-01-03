
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# V10 Code Block
new_code = r'''
def generate_card_zip(char, manager):
    import io
    import zipfile
    import os
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    import math

    CANVAS_1 = (1024, 1024)
    CANVAS_LANDSCAPE = (1024, 768)
    # Adjust path if needed, assuming relative to execution or absolute
    # Using absolute paths found in environment
    TEXTURE_PATH = "C:/Users/sweet/.gemini/antigravity/brain/f632eb69-1385-4e0a-bf7b-2cc9ec5d7899/old_paper_texture_1767013103684.png"
    CORNER_PATH = "C:/Users/sweet/.gemini/antigravity/brain/f632eb69-1385-4e0a-bf7b-2cc9ec5d7899/victorian_corner_1767013906098.png"
    FONT_PATH = "fonts/NotoSansJP-Regular.otf"

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

    def draw_text_wrapped(draw, text, x, y, max_w, font, fill, align="left", max_h=None):
        if not text: return y
        char_w = 1.0 * font.size 
        cols = int(max_w / char_w)
        if cols < 1: cols = 1
        
        lines = []
        for line in text.splitlines():
            current = ""
            for c in line:
                try:
                    bbox = draw.textbbox((0,0), current + c, font=font)
                    w = bbox[2] - bbox[0]
                except:
                    w = len(current + c) * font.size
                    
                if w > max_w:
                    lines.append(current)
                    current = c
                else:
                    current += c
            if current: lines.append(current)
            
        start_y = y
        line_height = int(font.size * 1.5)
        total_h = len(lines) * line_height
        
        if max_h:
            offset = (max_h - total_h) // 2
            start_y += offset 
            
        current_y = start_y
        for l in lines:
            draw.text((x, current_y), l, font=font, fill=fill)
            current_y += line_height
        return current_y

    def load_image_cover(path, size):
        try:
            img = Image.open(path).convert("RGBA")
            # FORCE FIT to eliminate gaps (User requirement: Zero margin)
            img = ImageOps.fit(img, size, method=Image.LANCZOS, centering=(0.5, 0.5))
            return img
        except:
            ph = Image.new('RGBA', size, (200, 200, 200, 255))
            d = ImageDraw.Draw(ph)
            d.text((size[0]//2, size[1]//2), "No Img", fill="gray", anchor="mm", font=f_small)
            return ph

    def draw_decorations(draw, w, h):
        if os.path.exists(CORNER_PATH):
            try:
                corner = Image.open(CORNER_PATH).convert("RGBA").resize((150, 150))
                # basic transparency hack for white background of corner image
                data = []
                for item in corner.getdata():
                    if item[0]>200 and item[1]>200 and item[2]>200:
                        data.append((255, 255, 255, 0))
                    else:
                        data.append(item)
                corner.putdata(data)
                
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


    # --- CARD 1: PROFILE ---
    def create_card_1():
        # DEBUG START
        print(f"DEBUG: 起動しました - キャラ名: {char.get('name')}")
        print(f"DEBUG: 画像リスト(imgs): {char.get('images', [])}")
        # DEBUG END
        
        details = char.get('details', {})
        race = details.get('race', '人間')
        
        # Color Logic
        # Holy/Other/Human -> Dark Brown. Demon -> White.
        if race == "魔族":
            txt_col = "#FFFFFF"
        else:
            txt_col = "#301b00" 
             
        img = Image.new("RGBA", CANVAS_1, (255, 255, 255, 255))
        
        # 1. IMAGES (Underlay - Sandwich Method)
        if len(char['images']) > 0:
            if char['images'][0] and os.path.exists(char['images'][0]):
                i1 = load_image_cover(char['images'][0], (400, 400))
                img.paste(i1, (110, 110))
            
        if len(char['images']) > 1:
             if char['images'][1] and os.path.exists(char['images'][1]):
                i2 = load_image_cover(char['images'][1], (250, 600))
                img.paste(i2, (700, 110))
            
        # 2. TEMPLATE (Overlay with transparency)
        template_map = {
            "人間": "sim_profile_hum.png",
            "魔族": "sim_profile_魔族.png",
            "聖族": "sim_profile_聖族.png",
            "その他": "sim_profile_hum.png"
        }
        t_file = template_map.get(race, "sim_profile_hum.png")
        t_path = os.path.join("templates", t_file)
        if os.path.exists(t_path):
            tm = Image.open(t_path).convert("RGBA").resize(CANVAS_1)
            img.paste(tm, (0, 0), mask=tm)
            
        # 3. TEXT
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
             
        # Memo Logic
        memo_col = txt_col # Match theme
        memo_raw = details.get('profile_memo', details.get('memo', ''))
        memo_text = ""
        if memo_raw:
             memo_text = "【簡易設定】\n" + memo_raw
        
        draw_text_wrapped(draw, memo_text, 80, 790, 860, get_font(22), memo_col, max_h=140)
        return img

    # --- CARD 2: STATS ---
    def create_card_2():
        # DEBUG START
        print(f"DEBUG: 起動しました - キャラ名: {char.get('name')}")
        print(f"DEBUG: 画像リスト(imgs): {char.get('images', [])}")
        # DEBUG END

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
        draw_text_wrapped(draw, bio, dx, dy+60, 900, get_font(16), "#212121")
        return bg

    # --- CARD 3: GALLERY ---
    def create_card_3():
        # DEBUG START
        print(f"DEBUG: 起動しました - キャラ名: {char.get('name')}")
        print(f"DEBUG: 画像リスト(imgs): {char.get('images', [])}")
        # DEBUG END

        # 1. Base Layer
        if os.path.exists(TEXTURE_PATH):
            bg = Image.open(TEXTURE_PATH).convert("RGBA").resize(CANVAS_LANDSCAPE)
        else:
            bg = Image.new("RGBA", CANVAS_LANDSCAPE, (250, 245, 230, 255))
            
        # 2. IMAGES LAYER (Strict Order: On BG, Under Template)
        images_list = char.get('images', [])
        
        def get_img_valid(idx):
             if idx < len(images_list) and images_list[idx] and os.path.exists(images_list[idx]):
                 return images_list[idx]
             return None
        
        p2 = get_img_valid(2)
        p3 = get_img_valid(3)
        p4 = get_img_valid(4)
        p5 = get_img_valid(5)
        
        # Draw images onto BG directly
        # Coordinates from V8 (based on User's gallery layout requirements)
        if p2: bg.paste(load_image_cover(p2, (300, 600)), (40, 100))
        if p3: bg.paste(load_image_cover(p3, (300, 290)), (360, 100))
        if p4: bg.paste(load_image_cover(p4, (300, 290)), (680, 100))
        if p5: bg.paste(load_image_cover(p5, (300, 290)), (360, 410))

        # 3. TEMPLATE OVERLAY
        gp = os.path.join("templates", "SNS-3.png")
        if os.path.exists(gp):
            tmpl = Image.open(gp).convert("RGBA").resize(CANVAS_LANDSCAPE)
            bg.paste(tmpl, (0, 0), mask=tmpl) 

        # 4. Text and Decorations
        draw = ImageDraw.Draw(bg)
        draw_decorations(draw, 1024, 768)
        
        en = char.get('name_en', '')
        if en:
            draw.text((512, 40), en, font=f_romaji, fill="#3e2723", anchor="mm")
            
        draw.text((680, 360), "【人間関係】", font=f_med, fill="#3e2723")
        rels = char.get('relations', [])[:4]
        positions = [(680, 440), (830, 440), (680, 580), (830, 580)]
        
        all_chars = {c['id']: c for c in manager.characters}
        
        for i, r in enumerate(rels):
            if i >= 4: break
            bx, by = positions[i]
            rtype = r.get('type', '').split('/')[0]
            draw.text((bx+75, by), rtype, font=get_font(14), fill="#5d4037", anchor="mm")
            
            tid = r.get('target_id')
            tgt = all_chars.get(tid)
            ic_sz = 70
            
            ic = None
            if tgt and tgt.get('images') and tgt['images'][0] and os.path.exists(tgt['images'][0]):
                 ic = load_image_cover(tgt['images'][0], (ic_sz, ic_sz))
            else:
                 ic = Image.new("RGBA", (ic_sz, ic_sz), (220, 220, 220, 255))
                 di = ImageDraw.Draw(ic)
                 di.text((ic_sz//2, ic_sz//2), "No Img", fill="gray", font=get_font(12), anchor="mm")
                 
            mask = Image.new("L", (ic_sz, ic_sz), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, ic_sz, ic_sz), fill=255)
            
            bg.paste(ic, (bx+40, by+20), mask=mask)
            
            if tgt: tname = tgt.get('first_name', tgt.get('name', ''))
            else: tname = r.get('target_name', '')
            tname = tname.split()[0]
            draw.text((bx+75, by+105), tname, font=get_font(16), fill="#3e2723", anchor="mm")
            
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

try:
    content = None
    # Try reading with different encodings
    for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'cp932', 'latin1']:
        try:
            with open(target_file, 'r', encoding=enc) as f:
                content = f.read()
            print(f"Successfully read file with encoding: {enc}")
            break
        except Exception:
            continue
            
    if content is None:
        raise Exception("Failed to read file with any known encoding.")

    # Determine what to replace.
    # We want to replace the `generate_card_zip` function essentially.
    
    # Smart replace logic
    import re
    
    # 1. Find Start
    start_idx = content.find("def generate_card_zip(char, manager):")
    if start_idx == -1:
        # Fallback: Maybe it's defined without args or different spacing?
        # Try finding the First Image Function
        start_idx = content.find("def create_image_1(char):")
        if start_idx == -1:
             start_idx = content.find("def create_card_1(char):")
        
        # If we found a start via create_image/card, we want to go back a bit to see if there's a wrapper line
        # But safely, we can just start replacing from there ONLY IF we are sure we are replacing the valid block.
        # But if we replace starting at create_image_1, we might lose the `generate_card_zip` header if it was above.
        # So we should prepend the header if we are starting at create_image_1?
        # No, new_code HAS the header. So we need to consume the old header if it exists.
        
        # Let's try to find the last function before create_image_1?
        pass

    # 2. Find End
    end_idx = content.find("def render_relation_page(manager):")
    
    if start_idx != -1 and end_idx != -1:
        # Check if there is a 'def generate_card_zip' slightly before `create_image_1` if we matched that
        if "def create_image_1" in content[start_idx:start_idx+50]:
             # Scan back for generate
             prev_chunk = content[max(0, start_idx-500):start_idx]
             g_canc = prev_chunk.rfind("def generate_card_zip")
             if g_canc != -1:
                 start_idx = max(0, start_idx-500) + g_canc
                 
        pre = content[:start_idx]
        post = content[end_idx:]
        
        final_content = pre + new_code + "\n\n" + post
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print("Updated char_app.py to V10 (Smart Replace).")
    else:
        print(f"Could not find boundaries. Start: {start_idx}, End: {end_idx}")


except Exception as e:
    print(f"Error: {e}")
