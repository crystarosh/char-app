
import os

target_file = r"d:\Users\sweetbeast\Pictures\work\sameway\AI\char_app.py"

# 1. Update Register Page with Char Counts
# 2. Update Detail View to show 'memo'

update_code = r'''    st.markdown("### 📝 詳細設定")
    
    # RESTORED: Char Counts
    
    st.markdown("##### プロフィール画像用テキスト (Card 1)")
    st.caption("Card 1 (Profile) の下部ベージュエリアに表示されるテキストです。約150文字程度推奨。")
    memo_val = details.get('memo', '')
    memo_in = st.text_area("プロフィール用簡易設定", value=memo_val, height=100, key="memo_input_area")
    st.caption(f"現在の文字数: {len(memo_in)} 文字")

    st.markdown("##### SNS用（短文） (Card 2)")
    st.caption("Card 2 (Stats) 右下のエリアに表示されるテキストです。約250文字以内で入力してください。")
    bio_short_val = existing_data.get('bio_short', '')
    bio_short = st.text_area("SNS用短文", value=bio_short_val, height=150, max_chars=250, key="bio_short_input")
    st.caption(f"現在の文字数: {len(bio_short)} 文字")
    
    st.markdown("##### 詳細用（長文） (Web詳細)")
    st.caption("Webの詳細画面で表示される全文です。画像には使用されません。")
    bio_long_val = existing_data.get('bio', '')
    bio_in = st.text_area("詳細設定・裏設定など", value=bio_long_val, height=300, key="bio_input_area")
    st.caption(f"現在の文字数: {len(bio_in)} 文字")
'''

# Code to insert into Detail View (render_list_page)
detail_view_update = r'''            # Bio Display
            st.markdown("**詳細設定・経歴**")
            
            # SHOW MEMO (Profile Text)
            memo_txt = details.get('memo', '')
            if memo_txt:
                with st.expander("プロフィール画像用テキストを確認", expanded=False):
                    st.info(memo_txt)
                    st.caption(f"{len(memo_txt)}文字")
            
            # Show Short Bio openly if exists
            if char.get('bio_short'):
                st.info(char['bio_short'], icon="📝")
'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 1. Apply Register Page Update
# Find the block from "st.markdown("### 📝 詳細設定")" to "st.markdown("### 📊 基礎ステータス")"
# This captures the bio inputs area.
pattern_reg = re.compile(r'st\.markdown\("### 📝 詳細設定"\).*?(?=st\.markdown\("### 📊 基礎ステータス"\))', re.DOTALL)
match_reg = pattern_reg.search(content)

if match_reg:
    # Replace the bio inputs block with the version having counters
    content = content[:match_reg.start()] + update_code + content[match_reg.end():]
    print("Updated Register Page with Char Counts.")
else:
    print("Error finding Register Page block.")

# 2. Apply Detail View Update
# Find "# Bio Display" and replace the logic following it up to "# Show Long Bio" or similar
# Current code in render_list_page:
#             # Bio Display
#             st.markdown("**詳細設定・経歴**")
#             
#             # Show Short Bio openly if exists

pattern_detail = re.compile(r'# Bio Display\s+st\.markdown\("\*\*詳細設定・経歴\*\*"\)\s+(?=# Show Short Bio)', re.DOTALL)
match_detail = pattern_detail.search(content)

if match_detail:
    # Replace just the header and insert the memo view before the Short Bio
    # Actually, simply injecting the memo view code is safer.
    content = content[:match_detail.end()] + "\n            # SHOW MEMO (Profile Text)\n            memo_txt = details.get('memo', '')\n            if memo_txt:\n                with st.expander('プロフィール画像用テキストを確認', expanded=False):\n                    st.info(memo_txt)\n                    st.caption(f'{len(memo_txt)}文字')\n            \n" + content[match_detail.end():]
    print("Updated Detail View to show Profile Memo.")
else:
    print("Error finding Detail View block.")

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
