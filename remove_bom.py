
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

try:
    with open(target_file, 'rb') as f:
        content = f.read()

    # Check for UTF-8 BOM
    if content.startswith(b'\xef\xbb\xbf'):
        print("BOM found. Removing...")
        content = content[3:]
    else:
        print("No BOM found at start.")

    # Write back
    with open(target_file, 'wb') as f:
        f.write(content)
        
    print("File saved as clean UTF-8.")

except Exception as e:
    print(f"Error: {e}")
