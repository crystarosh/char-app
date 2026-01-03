
import os
import textwrap

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# Unique identifier for the start of the table block
start_marker = 'table_html = f"""'
end_marker = 'st.markdown(table_html, unsafe_allow_html=True)'

# Replacement block using textwrap.dedent
new_block = """            import textwrap
            table_html = textwrap.dedent(f\"\"\"
            <table class="info-table">
                <tr><td>表記名</td><td>{char.get('name_en', '-')}</td></tr>
                <tr><td>年齢</td><td>{details.get('age', '-')}</td></tr>
                <tr><td>種族</td><td>{details.get('race', '-')}</td></tr>
                <tr><td>地位</td><td>{details.get('class_rank', '-')}</td></tr>
                <tr><td>職業</td><td>{details.get('role', '-')}</td></tr>
                <tr><td>出身/所属</td><td>{details.get('origin', '-')}</td></tr>
                <tr><td>身長/体重</td><td>{details.get('height_weight', '-')}</td></tr>
                <tr><td>容姿/外見</td><td>{details.get('appearance', '-')}</td></tr>
                <tr><td>目の色</td><td>{color_chip(details.get('eye_color'))}</td></tr>
                <tr><td>髪の色</td><td>{color_chip(details.get('hair_color'))}</td></tr>
                <tr><td>イメージカラー</td><td>{color_chip(details.get('image_color'))}</td></tr>
                <tr><td>性格</td><td>{details.get('personality', '-')}</td></tr>
            </table>
            \"\"\")
            st.markdown(table_html, unsafe_allow_html=True)"""

try:
    with open(target_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except:
    with open(target_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

new_lines = []
skip = False
inserted = False

for line in lines:
    if start_marker in line and not inserted:
        # Found the start
        skip = True
        new_lines.append(new_block + "\n")
        inserted = True
    
    if skip:
        if end_marker in line:
            # Found the end, stop skipping (but don't include this line as it's part of replacement)
            skip = False
        continue
    
    new_lines.append(line)

with open(target_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Table fix applied.")
