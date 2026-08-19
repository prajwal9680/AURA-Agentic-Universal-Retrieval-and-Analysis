"""
AURA — SQLite Schema Migration for OS Context & Clipboard Memory
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "aura.db"

def migrate():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(memories)")
    existing_cols = [row[1] for row in cursor.fetchall()]

    new_cols = [
        ("window_title", "TEXT DEFAULT ''"),
        ("source_type", "TEXT DEFAULT 'upload'"),
        ("clipboard_context", "TEXT DEFAULT ''"),
        ("captured_at", "DATETIME"),
    ]

    for col_name, col_def in new_cols:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE memories ADD COLUMN {col_name} {col_def}")
            print(f"Added column {col_name} to memories table.")
        else:
            print(f"Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Schema migration successfully completed.")

if __name__ == "__main__":
    migrate()
