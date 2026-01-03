
target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

content = None
for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'cp932', 'latin1']:
    try:
        with open(target_file, 'r', encoding=enc) as f:
            content = f.read()
        print(f"Read with {enc}")
        break
    except:
        continue

if content:
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "def create_image_1" in line:
            print(f"create_image_1 found at line {i+1}: {line.strip()}")
            # Look backwards for the function wrapping it
            for j in range(i, max(0, i-200), -1):
                if "def generate_card_zip" in lines[j]:
                    print(f"generate_card_zip found at line {j+1}: {lines[j].strip()}")
                    break
        if "def render_relation_page" in line:
            print(f"render_relation_page found at line {i+1}: {line.strip()}")
            break
