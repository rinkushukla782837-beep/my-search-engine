import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sqlite3
import time

DB_NAME = "search.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()


def crawl(url):
    try:
        headers = {
            "User-Agent": "GyanKoshBot/1.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = soup.title.string.strip() if soup.title else ""

        content = soup.get_text(
            " ",
            strip=True
        )

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO pages
            (url, title, content)
            VALUES (?, ?, ?)
        """, (
            url,
            title,
            content
        ))

        conn.commit()
        conn.close()

        links = []

        for link in soup.find_all("a", href=True):
            new_url = urljoin(url, link["href"])

            if urlparse(new_url).scheme in ["http", "https"]:
                links.append(new_url)

        return links

    except Exception as e:
        print("Error:", e)
        return []


if __name__ == "__main__":

    create_database()

    start_url = "https://example.com"

    print("GyanKosh Crawler started...")

    links = crawl(start_url)

    print("Page saved!")
    print("Links found:", len(links))
