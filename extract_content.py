import sqlite3
import requests

DB_PATH = "articles.db"
JINA_API_KEY = ""

headers = {
    'Authorization': f'Bearer {JINA_API_KEY}',
    'X-Remove-Selector': 'header, .menu, .advertisement, .ad, .related, .comments',
    'X-Retain-Images': 'none'
}

def extract_content(url):
    """Fetches article content from Jina AI"""
    response = requests.get(f"https://r.jina.ai/{url}", headers=headers)
    
    if response.status_code != 200:
        print(f"⚠️ Jina AI request failed for {url}. Status Code: {response.status_code}")
        return None

    print(f"🔍 Extracted content from {url}: {response.text[:500]}...")  # Print first 500 characters for debugging
    return response.text

def update_articles():
    """Updates database with extracted content"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT url FROM articles WHERE article_text IS NULL")
    urls = cursor.fetchall()

    for (url,) in urls:
        content = extract_content(url)
        if content:
            cursor.execute("UPDATE articles SET article_text = ? WHERE url = ?", (content, url))
    
    conn.commit()
    conn.close()
    print("✅ Articles updated with extracted content!")

if __name__ == "__main__":
    update_articles()
