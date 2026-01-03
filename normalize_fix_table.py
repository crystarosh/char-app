
import os
import re

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

try:
    with open(target_file, 'rb') as f:
        raw = f.read()
    
    # Simple decode
    content = raw.decode('utf-8')
    
    # 1. Normalize Newlines: Remove double blank lines if pervasive
    # Replace \r\n\r\n with \n, etc.
    # First normalize all to \n
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Collapsing multiple newlines -> single newline is risky for intentionally blank lines.
    # But looking at the file, every line has a blank line after it.
    # "import streamlit as st\n\nimport json\n\n"
    # We want "import streamlit as st\nimport json\n"
    # Heuristic: If we see a pattern of line + \n\n + line, collapse.
    # But safe approach: Just fix the Table Logic first. The double spacing is ugly but functional.
    # The user complained about Table Tags.
    
    # 2. Fix Table HTML Construction
    # Find the block starting with "import textwrap" and ending at "st.markdown(table_html..."
    # or the previous version.
    
    # We will replace the whole block with a cleaner version.
    
    iframe_block = r'''            import textwrap
            table_html = textwrap.dedent(f"""
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
            """)
            st.markdown(table_html, unsafe_allow_html=True)'''

    # Robust replacement: Use single line construction
    new_block = r'''            # HTML Table (Flattened to avoid Markdown CodeBlock)
            table_rows = [
                f"<tr><td>表記名</td><td>{char.get('name_en', '-')}</td></tr>",
                f"<tr><td>年齢</td><td>{details.get('age', '-')}</td></tr>",
                f"<tr><td>種族</td><td>{details.get('race', '-')}</td></tr>",
                f"<tr><td>地位</td><td>{details.get('class_rank', '-')}</td></tr>",
                f"<tr><td>職業</td><td>{details.get('role', '-')}</td></tr>",
                f"<tr><td>出身/所属</td><td>{details.get('origin', '-')}</td></tr>",
                f"<tr><td>身長/体重</td><td>{details.get('height_weight', '-')}</td></tr>",
                f"<tr><td>容姿/外見</td><td>{details.get('appearance', '-')}</td></tr>",
                f"<tr><td>目の色</td><td>{color_chip(details.get('eye_color'))}</td></tr>",
                f"<tr><td>髪の色</td><td>{color_chip(details.get('hair_color'))}</td></tr>",
                f"<tr><td>イメージカラー</td><td>{color_chip(details.get('image_color'))}</td></tr>",
                f"<tr><td>性格</td><td>{details.get('personality', '-')}</td></tr>"
            ]
            table_html = '<table class="info-table">' + "".join(table_rows) + '</table>'
            st.markdown(table_html, unsafe_allow_html=True)'''

    # Attempt to locate the block. Since indentation/newlines vary, we might need fuzzy match.
    # Or just Find "import textwrap" inside `render_list_page`?
    # Actually, I know the exact content of `iframe_block` because I wrote it in Step 486.
    # BUT, if `textwrap` import line has extra newline...
    
    # Let's try to replace the previous version logic if it exists.
    # "table_html = f\"\"\"" ...
    
    # We will search for a unique start and end.
    start_anchor = '<table class="info-table">'
    end_anchor = 'st.markdown(table_html, unsafe_allow_html=True)'
    
    # Locate indices
    idx_start = content.find(start_anchor)
    if idx_start != -1:
        # scan back to `table_html = ...`
        # scan forward to `st.markdown...`
        # Use regex to find the variable assignment block.
        
        # Regex: table_html\s*=\s*.*?st\.markdown\(table_html,\s*unsafe_allow_html=True\)
        # DOTALL
        
        pattern = re.compile(r'table_html\s*=\s*.*?(?<!st\.)st\.markdown\(table_html,\s*unsafe_allow_html=True\)', re.DOTALL)
        
        # Check if we have `import textwrap` before it?
        # Just replace the matches.
        
        # Note: Previous script put `import textwrap` right before.
        
        # Let's try replacing the specific `textwrap.dedent` block first.
        content = content.replace(iframe_block, new_block)
        
        # Also try replacing the ORIGINAL indented block if `textwrap` wasn't applied or reverted.
        orig_block = r'''            table_html = f"""
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
            """
            st.markdown(table_html, unsafe_allow_html=True)'''
            
        content = content.replace(orig_block, new_block)
        
        # Also minimal regex replacement if exact string fails due to whitespace
        # Find: table_html = .*?</table>.*?st.markdown
        pattern = re.compile(r'table_html\s*=\s*(?:textwrap\.dedent\(f?"""|f""").*?</table>\s*(?:""")?\)?\s*st\.markdown\(table_html,\s*unsafe_allow_html=True\)', re.DOTALL)
        
        if pattern.search(content):
            content = pattern.sub(new_block, content)
            print("Replaced via Regex")
        else:
             print("Regex match failed (maybe already fixed or different format)")

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Table rendering fix applied.")
    
except Exception as e:
    print(f"Error: {e}")
