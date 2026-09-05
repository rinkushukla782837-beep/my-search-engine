
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query is required"}), 400

    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        results = []

        if data.get("AbstractText"):
            results.append({
                "title": data.get("Heading", query),
                "text": data.get("AbstractText"),
                "url": data.get("AbstractURL", "")
            })

        for item in data.get("RelatedTopics", []):
            if "Text" in item:
                results.append({
                    "title": item.get("Text", "")[:100],
                    "text": item.get("Text", ""),
                    "url": item.get("FirstURL", "")
                })

        return jsonify({
            "query": query,
            "results": results[:10]
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
