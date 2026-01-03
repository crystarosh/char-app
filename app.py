import streamlit as st
import feedparser
import urllib.parse
from datetime import datetime
import time

# --- Configuration ---
st.set_page_config(
    page_title="Global News Dashboard",
    page_icon="📰",
    layout="wide",
)

# --- Custom CSS for Card Design ---
st.markdown("""
<style>
    .news-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        color: #333333;
    }
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .news-title {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 10px;
        color: #1E88E5;
        text-decoration: none;
    }
    .news-date {
        font-size: 0.85em;
        color: #666;
        margin-bottom: 15px;
        font-style: italic;
    }
    .news-summary {
        font-size: 0.95em;
        line-height: 1.5;
        margin-bottom: 15px;
        color: #444;
        flex-grow: 1; /* Pushes button to bottom */
    }
    .read-more-btn {
        display: inline-block;
        padding: 8px 16px;
        background-color: #1E88E5;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        text-align: center;
        font-size: 0.9em;
        align-self: flex-start;
    }
    .read-more-btn:hover {
        background-color: #1565C0;
    }
    
    /* Dark mode adjustments (simple override if user system is dark) */
    @media (prefers-color-scheme: dark) {
        .news-card {
            background-color: #262730;
            color: #ffffff;
            box-shadow: 0 4px 6px rgba(255,255,255,0.05);
        }
        .news-title {
            color: #90CAF9;
        }
        .news-date {
            color: #aaa;
        }
        .news-summary {
            color: #ddd;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_news(query):
    """Fetches news from Google News RSS for a given query."""
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(rss_url)
    return feed.entries

def display_news_card(entry):
    """Displays a single news entry as a styled card."""
    # Clean up summary (sometimes contains HTML)
    # Using simple text extraction or just displaying as is if it's safeish. 
    # Feedparser sanitizes somewhat, but Google News summaries are often HTML with images.
    # For a clean card, we might strip tags or just show the title/date/link if summary is messy.
    # Google News RSS summary is often just a duplicate of title or a link list.
    # Let's check if summary exists and is different from title.
    
    soup_summary = entry.get('summary', '')
    # Simple tag stripping could be added here if needed, but sticking to basic for now.
    
    published_parsed = entry.get('published_parsed')
    if published_parsed:
        date_str = datetime(*published_parsed[:6]).strftime('%Y-%m-%d %H:%M')
    else:
        date_str = "日付不明"

    # Use HTML for the card
    card_html = f"""
    <div class="news-card">
        <a href="{entry.link}" target="_blank" class="news-title">{entry.title}</a>
        <div class="news-date">{date_str}</div>
        <div class="news-summary">{soup_summary}</div>
        <a href="{entry.link}" target="_blank" class="read-more-btn">元記事を読む</a>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# --- Main App ---
def main():
    st.title("📰 News Dashboard")
    st.caption("最新のニュースをGoogle Newsから収集・表示します")

    # --- Sidebar ---
    st.sidebar.header("検索設定")
    
    # Preset selection
    topic = st.sidebar.radio(
        "トピックを選択",
        ("🇹🇼 台湾関連", "🇰🇬 キルギス・中央アジア", "🔍 カスタム検索")
    )

    query = ""
    if topic == "🇹🇼 台湾関連":
        query = "台湾"
        st.sidebar.success(f"検索ワード: **{query}**")
    elif topic == "🇰🇬 キルギス・中央アジア":
        query = "キルギス OR 中央アジア"
        st.sidebar.success(f"検索ワード: **{query}**")
    else:
        query = st.sidebar.text_input("検索キーワードを入力", placeholder="例: 生成AI")

    # --- Content Area ---
    if query:
        st.subheader(f"「{query}」のニュース")
        
        with st.spinner('ニュースを取得中...'):
            entries = get_news(query)

        if not entries:
            st.warning("ニュースが見つかりませんでした。")
        else:
            # Layout: Grid with 2 columns
            cols = st.columns(2)
            for i, entry in enumerate(entries):
                with cols[i % 2]:
                    display_news_card(entry)
    else:
        st.info("サイドバーからトピックを選択するか、検索ワードを入力してください。")

if __name__ == "__main__":
    main()
