import os
import requests
from datetime import datetime  # 1. 引入 datetime 模組
from google import genai
from google.genai import types

def fetch_hn_stories(limit=10):
    """抓取 Hacker News 前 N 大熱門文章及其熱門留言概況"""
    print("正在擷取 Hacker News 熱門趨勢...")
    top_ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    top_ids = requests.get(top_ids_url).json()[:limit]
    
    stories = []
    for sid in top_ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
        item = requests.get(item_url).json()
        
        hn_discussion_url = f"https://news.ycombinator.com/item?id={sid}"
        
        stories.append({
            "title": item.get("title", ""),
            "url": item.get("url", hn_discussion_url),
            "hn_discussion_url": hn_discussion_url,
            "score": item.get("score", 0),
            "by": item.get("by", ""),
            "comments_count": item.get("descendants", 0)
        })
    return stories

def generate_notebook_style_slides(stories):
    """呼叫 Gemini API 生成 NotebookLM 風格的結構化簡報"""
    print("正在使用 Gemini 生成 NotebookLM 結構化簡報...")
    
    client = genai.Client()

    # 2. 取得今日真實日期 (例如: 2026年08月09日)
    today_str = datetime.now().strftime("%Y年%m月%d日")

    formatted_input = "\n".join([
        f"- 標題: {s['title']}\n"
        f"  原文連結: {s['url']}\n"
        f"  HN討論區連結: {s['hn_discussion_url']}\n"
        f"  熱度: {s['score']} points | 討論數: {s['comments_count']} | 作者: {s['by']}"
        for s in stories
    ])

    prompt = f"""
你是一位頂級的科技趨勢分析師，請模仿 Google NotebookLM 簡報的摘要風格，將以下今日 Hacker News 熱門話題製作成一份單頁 HTML Presentation 簡報。

輸入資料：
{formatted_input}

【簡報內容結構要求】
1. 封面頁 (Slide 1)：
   - 主標題：Hacker News 每日科技熱點摘要
   - 副標題：基於最新社群討論自動生成
   - 生成日期：【請務必精確顯示此日期：{today_str}】
   - 包含概括全篇的 3 個關鍵字標籤 (Tags)。

2. 文章內容頁 (Slide 2 ~ N)：每篇文章獨立一張投影片/卡片，包含：
   - 文章標題（附帶跳轉至原文的連結）。
   - 核心摘要 (Core Insight)：用 2-3 句正體中文精準說明這篇文章或專案在解決什麼問題。
   - 關鍵要點 (Key Takeaways)：以 3 個 Bullet Points 條列技術亮點或產業影響。
   - 社群觀點與連結 (Community Reaction)：
     * 分析為什麼這篇文章能在 Hacker News 獲得高討論度。
     * 【關鍵要求】：請務必在卡片下方放上一個明顯的連結按鈕，超連結導向該文章的「HN討論區連結」，按鈕文字請依據該文章實際的討論數顯示為「前往 Hacker News 討論區 (含 N 則討論)」。

3. 總結頁 (Final Slide)：
   - 今日技術趨勢歸納 (Today's Tech Pulse)：用一小段話總結今天熱門文章反映出的技術轉變或開發者關注焦點。

【視覺設計要求 (CSS inline)】
- 請使用現代感、深色科技風格 (Dark Mode UI, 深灰色背景 #0f172a，搭配高對比白字與藍/紫漸層 accent color)。
- 每張投影片以卡片化 (Card-based UI) 呈現，具備清楚的 padding、邊框圓角與陰影。
- 「前往 Hacker News 討論區」的按鈕請使用醒目的按鈕樣式 (例如藍色背景 #2563eb，白字，圓角邊框，帶有 hover 效果)。
- 輸出必須為單一獨立的 HTML 檔案，包含完整的 html, head, style, body 標籤。
- 僅輸出純 HTML 程式碼，不要包含任何 Markdown 標記 (如 ```html) 或開場白。
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    content = response.text.strip()
    if "```html" in content:
        content = content.split("```html")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
        
    return content

def main():
    stories = fetch_hn_stories(10)
    slides_html = generate_notebook_style_slides(stories)
    
    output_filename = "index.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(slides_html)
        
    print(f"簡報已成功生成至 {output_filename}")

if __name__ == "__main__":
    main()
