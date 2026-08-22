import sqlite3, json

conn = sqlite3.connect('data/aura.db')
cursor = conn.cursor()
cursor.execute("SELECT id, original_filename, category, summary, ocr_text, entities, topics FROM memories WHERE original_filename LIKE '%mushroom%'")
rows = cursor.fetchall()
print(f"Found {len(rows)} mushroom rows:")
for r in rows:
    print(f"ID: {r[0]} | File: {r[1]} | Cat: {r[2]}")
    print(f"Summary: {r[3]}")
    print(f"OCR: {r[4]}")
    print(f"Topics: {r[6]}")
    print()

cursor.execute("SELECT original_filename FROM memories WHERE category = 'recipe'")
recipes = [x[0] for x in cursor.fetchall()]
print(f"All recipes ({len(recipes)}): {recipes[:10]}")
conn.close()
