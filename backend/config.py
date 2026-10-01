from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get(
    "INSTAUNLIKE_DB", BASE_DIR / "data" / "insta_unlike.sqlite3"
))
MAX_CONTENT_LENGTH = 10 * 1024 * 1024
