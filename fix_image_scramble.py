
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# Fixes:
# 1. Image Upload Order Scramble in render_register_page.
# 2. Card 3 Gallery Indexing (Ensure we use available images 2,3,4 for the slots).

# I will rewrite the image upload section to be robust.

image_fix_code = r'''    st.markdown("### 🖼️ 画像")
    current_images = existing_data.get('images', []) if edit_char_id else []
    if current_images:
        st.image(current_images, width=100, caption=[f"No.{i+1}" for i in range(len(current_images))])

    img_col1, img_col2 = st.columns(2)
    # Define vars first
    u1, u2, u3, u4, u5 = None, None, None, None, None
    
    with img_col1:
        u1 = st.file_uploader("画像1 (バストショット - 必須)", type=["png", "jpg"], key="u1")
        u3 = st.file_uploader("画像3 (Gallery A)", type=["png", "jpg"], key="u3")
        u5 = st.file_uploader("画像5 (Gallery C)", type=["png", "jpg"], key="u5") 
    with img_col2:
        u2 = st.file_uploader("画像2 (全身 - 推奨)", type=["png", "jpg"], key="u2")
        u4 = st.file_uploader("画像4 (Gallery B)", type=["png", "jpg"], key="u4")

    st.markdown("---")
'''

# And the Submit section needs to use the correct list order.
submit_fix_code = r'''        if lb_target != "(なし)":
             new_char['stats'][lb_target] = lb_value

        # FIX: Ensure order is [u1, u2, u3, u4, u5]
        ordered_uploads = [u1, u2, u3, u4, u5]
        
        updated_paths = []
        for i in range(5): 
            old_path = current_images[i] if i < len(current_images) else None
            new_file = ordered_uploads[i] if i < len(ordered_uploads) else None
            if new_file:
                saved_path = manager.save_image(new_file)
                if saved_path:
                    updated_paths.append(saved_path)
            else:
                if old_path:
                    updated_paths.append(old_path)
        new_char['images'] = updated_paths
'''

# And update create_card_3 to map Image 5 (Index 4) to p5 (Bottom Slot) if p4 is mapped to Top.
# Wait, if p4 is Top Right and p5 is Bottom Center.
# If I change p4 to take Index 4.
# It seems the Layout intended:
# p2 (Index 2) -> Tall Left
# p3 (Index 3) -> Mid Top
# p4 (Index 4) -> Top Right
# p5 (Index 5) -> Mid Bottom

# If user only has 3 gallery images (Indices 2,3,4).
# They fill p2, p3, p4.
# p5 is empty.
# If "Right Lower" is empty, it means p5 (Mid Bottom) or a missing p6 (Right Bottom).

# Maybe I should map Index 4 (Image 5) to the "Bottom" slot if only 3 exist?
# Or just accept that Image 5 goes to Top Right.
# But "Right Lower" missing implies they expect something there.
# I'll update `create_card_3` to use indices 2,3,4,4? No.

# Let's just fix the upload order first. That is a provable bug.
# The user might be confused because the upload for "Image 5" went to "Image 3" slot (Left Tall) due to scramble,
# and "Image 4" went to "Image 5" slot? No.
# u1, u3, u5, u2, u4.
# Img3 (Index 2) got u5.
# Img4 (Index 3) got u2 (Full Body).
# Img5 (Index 4) got u4.
# So "Image 5" appeared on Left. "Full Body" appeared in Center. "Image 4" appeared on Right.
# So "Lower" was empty (because Index 5 was empty).
# The user probably uploaded 5 images.
# If I fix the order:
# Img3 (Index 2) = u3
# Img4 (Index 3) = u4
# Img5 (Index 4) = u5
# Then:
# Left = u3
# Center = u4
# Right = u5 (Top Right)
# Bottom = Empty?

# If the user wants 4 images in gallery, they need "Image 6" (Index 5).
# But there is no uploader for Image 6.
# I should Add Uploader for Image 6?
# Or change `p5` to use `gv(4)` (Img5) and move `p4` somewhere else?
# If the previous design (V25) was "Two Square Images Side by Side".
# Maybe `p3` and `p4`?
# And `p2`?

# I'll Stick to fixing the upload order. The scramble explains weird behavior.
# I will apply the two blocks.

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Block 1: The Upload UI
# Locate the block starting `st.markdown("### 🖼️ 画像")` to `st.markdown("---")`
# Note: I added `st.markdown("---")` in previous step? No, it's before relations.
p1 = re.compile(r'st\.markdown\("### 🖼️ 画像"\).*?(?=st\.markdown\("### 🤝 人間関係"\))', re.DOTALL)

m1 = p1.search(content)
if m1:
    # Need to keep the initial part and replace the uploaders
    # My replacement code includes the header.
    # But `st.markdown("---")` is NOT in the capture if I look for `human_relations`.
    # Actually `st.markdown("---")` is before `st.markdown("### 🤝 人間関係")` in `restore_memo_input.py`.
    # Let's expand the regex to include the `---`.
    p1 = re.compile(r'st\.markdown\("### 🖼️ 画像"\).*?(?=st\.markdown\("### 🤝 人間関係"\))', re.DOTALL)
    m1 = p1.search(content)
    if m1:
        # My `image_fix_code` ends with `st.markdown("---")`.
        # The captured block likely includes `st.markdown("---")` at the end or valid overlap.
        # Let's just replace.
        content = content[:m1.start()] + image_fix_code + "\n    " + content[m1.end():]
        print("Fixed Upload UI Logic.")
    else:
        print("Block 1 not found.")
else:
    print("Block 1 search failed.")

# Block 2: The Submit Logic
# Look for `if lb_target != "(なし)":` ... down to `new_char['images'] = updated_paths`
p2 = re.compile(r'if lb_target != "\(なし\)":.*?new_char\[\'images\'\] = updated_paths', re.DOTALL)
m2 = p2.search(content)
if m2:
    content = content[:m2.start()] + submit_fix_code + content[m2.end():]
    print("Fixed Submit Save Logic.")
else:
    print("Block 2 not found.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
