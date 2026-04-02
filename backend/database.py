import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "listings.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT NOT NULL,
                description TEXT NOT NULL,
                category  TEXT NOT NULL,
                price_pln REAL NOT NULL,
                condition TEXT NOT NULL,
                confidence REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_listing(
    title: str,
    description: str,
    category: str,
    price_pln: float,
    condition: str,
    confidence: float | None,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO listings (title, description, category, price_pln, condition, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, description, category, price_pln, condition, confidence),
        )
        return cursor.lastrowid


def get_listings() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM listings ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]