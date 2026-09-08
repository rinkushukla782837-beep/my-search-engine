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
            timeout=15
        )

        if response.status_code != 200:
            print("Page open nahi hua:", response.status_code)
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Script aur style hata do
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        title = ""

        if soup.title:
            title = soup.title.get_text(
                strip=True
            )

        content = soup.get_text(
            " ",
            strip=True
        )

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO pages
            (url, title, content)
            VALUES (?, ?, ?)
        """, (
            url,
            title,
            content
        ))

        conn.commit()
        conn.close()

        print("Indexed:", title)
        print("URL:", url)

        links = []

        for link in soup.find_all(
            "a",
            href=True
        ):

            new_url = urljoin(
                url,
                link["href"]
            )

            parsed = urlparse(new_url)

            if parsed.scheme in [
                "http",
                "https"
            ]:

                links.append(new_url)

        return links

    except Exception as e:

        print(
            "Crawler error:",
            e
        )

        return []


if __name__ == "__main__":

    create_database()

    # Testing ke liye ek website
    start_url = "https://example.com"

    print("")
    print("==============================")
    print("     GyanKosh Crawler")
    print("==============================")
    print("")

    links = crawl(start_url)

    print("")
    print(
        "Total links found:",
        len(links)
    )
