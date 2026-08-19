"""
AURA — Local SQLite Schema Migrator
Ensures local development SQLite database is updated with all latest columns and tables.
"""
import sqlite3
from pathlib import Path

db_file = Path(__file__).resolve().parent.parent / "data" / "aura.db"
if not db_file.exists():
    print(f"Database {db_file} does not exist yet. It will be created on startup.")
    exit(0)

con = sqlite3.connect(str(db_file))
cur = con.cursor()

# Relationships columns
cols = [r[1] for r in cur.execute("PRAGMA table_info(relationships)").fetchall()]
if "evidence" not in cols:
    cur.execute("ALTER TABLE relationships ADD COLUMN evidence TEXT DEFAULT ''")
    print("Added 'evidence' column to relationships table.")

if "updated_at" not in cols:
    cur.execute("ALTER TABLE relationships ADD COLUMN updated_at DATETIME")
    print("Added 'updated_at' column to relationships table.")

# Ensure agent checkpoint tables exist
cur.execute("""
CREATE TABLE IF NOT EXISTS agent_checkpoints (
    thread_id TEXT,
    checkpoint_ns TEXT DEFAULT '',
    checkpoint_id TEXT,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at DATETIME,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS agent_checkpoint_blobs (
    thread_id TEXT,
    checkpoint_ns TEXT DEFAULT '',
    channel TEXT,
    version TEXT,
    type TEXT,
    blob TEXT,
    created_at DATETIME,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS agent_checkpoint_writes (
    thread_id TEXT,
    checkpoint_ns TEXT DEFAULT '',
    checkpoint_id TEXT,
    task_id TEXT,
    idx INTEGER,
    channel TEXT NOT NULL,
    type TEXT,
    blob TEXT,
    created_at DATETIME,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
)
""")

con.commit()
con.close()
print("SQLite migration script completed successfully.")
