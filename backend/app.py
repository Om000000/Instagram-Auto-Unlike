import json
from flask import Flask, jsonify, request, send_from_directory
from config import MAX_CONTENT_LENGTH
from database import init_db, get_db
from instagram_parser import parse_liked_posts

app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
init_db()
LOCAL_USER_ID = 1

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/api/health")
def health():
    return jsonify(success=True, service="python-api", message="Backend is running")

@app.get("/api/stats")
def stats():
    with get_db() as conn:
        row = conn.execute("""
            SELECT COUNT(*) AS total,
                   SUM(status = 'pending') AS pending,
                   SUM(status = 'unliked') AS unliked,
                   SUM(status = 'skipped') AS skipped
            FROM liked_posts WHERE user_id = ?
        """, (LOCAL_USER_ID,)).fetchone()
    return jsonify({key: (row[key] or 0) for key in row.keys()})

@app.get("/api/posts")
def posts():
    limit = min(max(request.args.get("limit", default=50, type=int), 1), 200)
    offset = max(request.args.get("offset", default=0, type=int), 0)
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, post_url, post_title, liked_at, status
            FROM liked_posts WHERE user_id = ?
            ORDER BY liked_at DESC, id DESC LIMIT ? OFFSET ?
        """, (LOCAL_USER_ID, limit, offset)).fetchall()
    return jsonify([dict(row) for row in rows])

@app.post("/api/import")
def import_likes():
    if "file" not in request.files:
        return jsonify(error="Upload a JSON file using the 'file' field."), 400
    uploaded = request.files["file"]
    if not uploaded.filename.lower().endswith(".json"):
        return jsonify(error="Only .json files are accepted."), 400
    try:
        data = json.load(uploaded.stream)
        parsed = parse_liked_posts(data)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        return jsonify(error=str(exc)), 400

    inserted = 0
    with get_db() as conn:
        for post in parsed:
            cursor = conn.execute("""
                INSERT OR IGNORE INTO liked_posts
                    (user_id, post_url, post_title, liked_at)
                VALUES (?, ?, ?, ?)
            """, (LOCAL_USER_ID, post["post_url"], post["post_title"], post["liked_at"]))
            inserted += cursor.rowcount

    return jsonify(
        success=True,
        found=len(parsed),
        imported=inserted,
        duplicates_or_existing=len(parsed) - inserted
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
