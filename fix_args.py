
target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

content = None
encoding_used = 'utf-8'

# Read with detection
for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'cp932', 'latin1']:
    try:
        with open(target_file, 'r', encoding=enc) as f:
            content = f.read()
        print(f"Read with {enc}")
        encoding_used = enc
        break
    except:
        continue

if content:
    # Replace the call
    old_call = "generate_card_zip(char)"
    new_call = "generate_card_zip(char, manager)"
    
    if old_call in content:
        new_content = content.replace(old_call, new_call)
        
        # Write back as utf-8 signature to be safe or just utf-8
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print("Fixed generate_card_zip call arguments.")
    else:
        print("Could not find 'generate_card_zip(char)' to fix.")
else:
    print("Failed to read file.")
