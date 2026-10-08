from datetime import datetime, timezone
from urllib.parse import urlparse

ALLOWED_HOSTS = {"instagram.com", "www.instagram.com"}


def is_instagram_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in {"http", "https"}
            and parsed.hostname in ALLOWED_HOSTS
            and parsed.path.startswith("/")
        )
    except (TypeError, ValueError):
        return False


def _label_map(record):
    result = {}
    for item in record.get("label_values", []):
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        if label:
            result[label] = item.get("value", "")
    return result


def _owner_username(record):
    for item in record.get("label_values", []):
        if not isinstance(item, dict) or item.get("title") != "Owner":
            continue
        for entry in item.get("dict", []):
            if not isinstance(entry, dict):
                continue
            for field in entry.get("dict", []):
                if isinstance(field, dict) and field.get("label") == "Username":
                    return field.get("value") or ""
    return ""


def parse_liked_posts(data):
    # Instagram's current export format is a top-level list. Each record
    # stores URL/caption in label_values and the owner under Owner.
    if isinstance(data, dict):
        records = data.get("likes_media_likes", data.get("liked_posts", data))
    else:
        records = data

    if not isinstance(records, list):
        raise ValueError("Unsupported JSON structure: expected a list of liked posts.")

    parsed_posts = []
    for record in records:
        if not isinstance(record, dict):
            continue

        labels = _label_map(record)
        url = labels.get("URL", "")
        if not is_instagram_url(url):
            continue

        timestamp = record.get("timestamp")
        liked_at = None
        if isinstance(timestamp, (int, float)):
            liked_at = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        owner = _owner_username(record)
        caption = labels.get("Caption", "")
        title = owner or (caption[:100] if caption else "Instagram post")

        parsed_posts.append({
            "post_url": url,
            "post_title": title,
            "liked_at": liked_at,
        })

    return parsed_posts
