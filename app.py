
from flask import Flask, request, jsonify, render_template
import sqlite3
import re

app = Flask(__name__)

DB_NAME = "search.db"


@app.route("/")
def home():
    return render_template("index.html")


def search_database(query):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Search words को अलग करना
    words = re.findall(r"\w+", query.lower())

    if not words:
        conn.close()
        return []

    conditions = []
    values = []

    for word in words:
        conditions.append(
            "(LOWER(title) LIKE ? OR LOWER(content) LIKE ?)"
        )

        values.append(f"%{word}%")
        values.append(f"%{word}%")

    sql = f"""
        SELECT url, title, content
        FROM pages
        WHERE {" OR ".join(conditions)}
        LIMIT 50
    """

    cursor.execute(sql, values)
    rows = cursor.fetchall()

    conn.close()

    results = []

    for row in rows:
        content = row["content"] or ""
        title = row["title"] or row["url"]

        # Search words की संख्या के आधार पर simple ranking
        score = 0

        text = (title + " " + content).lower()

        for word in words:
            score += text.count(word)

        # छोटा description
        snippet = content[:300]

        results.append({
            "title": title,
            "text": snippet,
            "url": row["url"],
            "score": score
        })

    # सबसे relevant result ऊपर
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Score user को नहीं दिखाना
    for result in results:
        result.pop("score", None)

    return results[:10]


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Search query is required"
        }), 400

    try:
        results = search_database(query)

        return jsonify({
            "query": query,
            "results": results
        })

    except Exception as e:
        return jsonify({
            "error": "Search failed",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
