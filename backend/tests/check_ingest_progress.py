import sqlite3
con = sqlite3.connect("data/aura.db")
cur = con.cursor()
cur.execute("SELECT original_filename, category, sensitivity_level, processing_status FROM memories WHERE original_filename LIKE '%swiggy%' OR original_filename LIKE '%amazon_india%' OR original_filename LIKE '%vscode%' OR original_filename LIKE '%mumbai%' OR original_filename LIKE '%pasta%' OR original_filename LIKE '%irctc%' OR original_filename LIKE '%github%' OR original_filename LIKE '%dashboard%'")
rows = cur.fetchall()
print(f"Matched {len(rows)} real screenshots in DB:")
for r in rows:
    print(" ", r)
con.close()
