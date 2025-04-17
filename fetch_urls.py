import sqlite3
import requests
import time

DB_PATH = "/Workspace/Users/ag95@cdc.gov/Llama index test/Safe reporting guidelines/articles.db"
API_KEY = "AIzaSyC6eIbdhP0b5XUaaUsQfoN8uOO4lohlTe8"
CX = "37c37a4a44e6d4d11"
# QUERY = "tWitch Boss suicide news after: 2024-09-19 before 2024-10-04"

def google_search(query, api_key, cx, max_results=10):
    """Fetches search results from Google API"""
    urls = []
    start = 1  

    while start <= max_results:
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}&start={start}"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            print(f"Error: {data['error']['message']}")
            break

        new_urls = [item["link"] for item in data.get("items", [])]
        if not new_urls:
            break  

        urls.extend(new_urls)
        start += 10  
        time.sleep(1)  

    return urls

def store_urls(urls, name_of_deceased, date_of_death):
    """Inserts URLs into the database while avoiding duplicates, linking them to the deceased person."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for url in urls:
        try:
            cursor.execute("""
                INSERT INTO articles (url, name_of_deceased, date_of_death) 
                VALUES (?, ?, ?)
            """, (url, name_of_deceased, date_of_death))
        except sqlite3.IntegrityError:
            pass  # URL already exists, skip insertion

    conn.commit()
    conn.close()
    print(f"✅ URLs stored successfully for {name_of_deceased} (Died on {date_of_death})")


if __name__ == "__main__":
    urls = google_search(QUERY, API_KEY, CX)
    store_urls(urls)
