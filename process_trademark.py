
import os
import re
from PIL import Image

# 1. Image Processing
src_path = r"C:/Users/sweet/.gemini/antigravity/brain/cc994841-9428-49b8-8589-a50351dd0573/uploaded_image_1767284868946.jpg"
dest_dir = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\images"
dest_path = os.path.join(dest_dir, "logo_shield.png")

print(f"Processing image from {src_path}...")
try:
    img = Image.open(src_path)
    # Resize to icon friendly size (e.g. 128x128 for favicon, but user wants it visible)
    # We save a high-res version for the Header and a small one for Icon?
    # Streamlit resizes favicon automatically.
    # We'll save one master PNG.
    img.save(dest_path)
    print(f"Saved logo to {dest_path}")
except Exception as e:
    print(f"Error processing image: {e}")

# 2. Code Update
target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"
with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Update Page Icon
content = content.replace('page_icon="images/favicon.png"', 'page_icon="images/logo_shield.png"')

# Update Header to include Image
# Current: st.header("The Legend of Crystarosh Characters List")
# Desired: Layout with Image + Title
# We use columns.

old_header_code = 'st.header("The Legend of Crystarosh Characters List")'

new_header_code = r'''
    # Header with Logo
    h_logo, h_title = st.columns([1, 10])
    with h_logo:
        st.image("images/logo_shield.png", use_container_width=True)
    with h_title:
        st.markdown("# The Legend of Crystarosh Characters List")
'''

if old_header_code in content:
    content = content.replace(old_header_code, new_header_code)
    print("Updated Header layout with Logo.")
else:
    # Try regex if exact string match fails (e.g. formatting)
    pass 

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
