
import os
import re

pb_path = r"C:\Users\sweet\.gemini\antigravity\conversations\e9b34a2c-98d0-48de-95e0-088596daa473.pb"

try:
    with open(pb_path, 'rb') as f:
        data = f.read()
except:
    print("Fail read")
    exit(1)

# Decode looser
text = data.decode('utf-8', errors='ignore')

print(f"Total Text Len: {len(text)}")

# Find Code Blocks
# Standard markdown
code_blocks = re.findall(r'```python(.*?)```', text, re.DOTALL)
print(f"Found {len(code_blocks)} python blocks")

found_zip_func = False

for i, code in enumerate(code_blocks):
    if "def generate_card_zip" in code:
        print(f"\n=== Found generate_card_zip in Block {i} (Len: {len(code)}) ===")
        # Print relevant parts (e.g. Card 2 section)
        if "create_card_2" in code:
            parts = code.split("create_card_2")
            if len(parts) > 1:
                print("--- Card 2 Logic ---")
                print(parts[1][:1000]) # First 1000 chars of Card 2
        
        # Check for card 1 layout
        if "create_card_1" in code:
            parts = code.split("create_card_1")
            print("--- Card 1 Logic ---")
            print(parts[1][:1000])

        found_zip_func = True

if not found_zip_func:
    print("No generation function found in markdown blocks.")
    # Search raw text for "chart_y ="
    # Case insensitive
    hits = re.findall(r'(chart_y\s*=\s*\d+)', text)
    print("Raw 'chart_y' hits:", hits)
    
    hits_dx = re.findall(r'(dx\s*=\s*\d+)', text)
    print("Raw 'dx' hits:", hits_dx)
    
    hits_dy = re.findall(r'(dy\s*=\s*\d+)', text)
    print("Raw 'dy' hits:", hits_dy)

    # Search for "create_card_1" raw
    if "create_card_1" in text:
        print("Found 'create_card_1' in raw text")
        idx = text.rfind("create_card_1") # Last occurrence
        print(text[idx:idx+500])
