
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

try:
    with open(target_file, 'rb') as f:
        content_bytes = f.read()
        
    try:
        content = content_bytes.decode('utf-8')
    except:
        content = content_bytes.decode('utf-8', errors='ignore')

    # The broken pattern is likely `("【簡易設定】` followed by an actual newline
    # because of the raw string regex replacement issue in V8.
    
    # We want to replace valid newlines inside this specific string with `\n` (escaped).
    
    if '("【簡易設定】\n' in content:
        print("Found broken newline (LF). Fixing...")
        content = content.replace('("【簡易設定】\n', '("【簡易設定】\\n')
        
    if '("【簡易設定】\r\n' in content:
        print("Found broken newline (CRLF). Fixing...")
        content = content.replace('("【簡易設定】\r\n', '("【簡易設定】\\n')

    # Also check if there are any other weirdnesses
    # V8 logic might have introduced other newlines?
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Syntax fix applied.")

except Exception as e:
    print(f"Error: {e}")
