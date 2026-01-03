
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

try:
    with open(target_file, 'rb') as f:
        content = f.read()

    # The BOM bytes
    bom = b'\xef\xbb\xbf'
    
    if bom in content:
        print(f"BOM found {content.count(bom)} time(s). Removing globally.")
        content = content.replace(bom, b'')
    else:
        print("No BOM found anywhere in file.")

    with open(target_file, 'wb') as f:
        f.write(content)
        
    print("File cleaned.")

except Exception as e:
    print(f"Error: {e}")
