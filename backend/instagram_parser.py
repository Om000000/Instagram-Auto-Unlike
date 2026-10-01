from datetime import datetime, timezone
from urllib.parse import urlparse

ALLOWED_HOSTS = {"instagram.com", "www.instagram.com"}

def is_instagram_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme == "https"
            and parsed.hostname in ALLOWED_HOSTS
            and parsed.path.startswith("/")
        )
    except (TypeError, ValueError):
        return False

def parse_liked_posts(data):
    # Supports the commonly seen likes_media_likes export structure.
    records = data.get("likes_media_likes", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise ValueError("Unsupported JSON structure: expected a list of liked posts.")

    parsed_posts = []
    for record in records:
        if not isinstance(record, dict):
            continue
        title = record.get("title") or "Instagram post"
        for item in record.get("string_list_data", []):
            if not isinstance(item, dict):
                continue
            url = item.get("href", "")
            if not is_instagram_url(url):
                continue
            timestamp = item.get("timestamp")
            liked_at = None
            if isinstance(timestamp, (int, float)):
                liked_at = datetime.fromtimestamp(
                    timestamp, tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S")
            parsed_posts.append({
                "post_url": url,
                "post_title": title,
                "liked_at": liked_at,
            })
    return parsed_posts
