
import os
import codecs

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

try:
    # Try reading as UTF-16LE since the tool reported it
    with codecs.open(target_file, 'r', encoding='utf-16le') as f:
        content = f.read()
    print("Read as UTF-16LE")
except Exception as e:
    print(f"UTF-16LE failed: {e}")
    try:
        # Try UTF-8 (maybe with BOM?)
        with codecs.open(target_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        print("Read as UTF-8-SIG")
    except Exception as e2:
        print(f"UTF-8-SIG failed: {e2}")
        # One last try with loose utf-8
        with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        print("Read as UTF-8 (loose)")

# Check if declaration exists
if "# -*- coding: utf-8 -*-" not in content[:100]:
    content = "# -*- coding: utf-8 -*-\n" + content

# Write back as strict UTF-8
with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Converted to UTF-8 with encoding declaration.")
