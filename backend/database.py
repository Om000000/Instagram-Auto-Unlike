import sqlite3
from contextlib import contextmanager
from config import DATABASE_PATH

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS app_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS liked_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    post_url TEXT NOT NULL,
    post_title TEXT,
    liked_at TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'unliked', 'kept', 'skipped')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, post_url)
);
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES liked_posts(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def _migrate_liked_posts(conn):
    info = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='liked_posts'").fetchone()
    if not info or "'kept'" in (info[0] or ""):
        return
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("""CREATE TABLE liked_posts_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
        post_url TEXT NOT NULL,
        post_title TEXT,
        liked_at TEXT,
        status TEXT NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending', 'unliked', 'kept', 'skipped')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, post_url)
    )""")
    conn.execute("""INSERT INTO liked_posts_new
        (id, user_id, post_url, post_title, liked_at, status, created_at)
        SELECT id, user_id, post_url, post_title, liked_at, status, created_at
        FROM liked_posts""")
    conn.execute("DROP TABLE liked_posts")
    conn.execute("ALTER TABLE liked_posts_new RENAME TO liked_posts")
    conn.execute("PRAGMA foreign_keys = ON")

def init_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.executescript(SCHEMA)
        _migrate_liked_posts(conn)
        conn.execute("INSERT OR IGNORE INTO app_users (id, username) VALUES (1, 'local-user')")

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
