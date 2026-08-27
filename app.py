from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "My Search Engine API is running!"

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query is required"}), 400

    return jsonify({
        "query": query,
        "message": "Search API is working!"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
