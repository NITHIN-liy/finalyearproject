import sqlite3
import os

db_path = 'instance/legal_ai.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    current = conn.cursor()
    current.execute("PRAGMA table_info(chat)")
    columns = current.fetchall()
    print("Chat table columns:")
    for col in columns:
        print(col)
    conn.close()
else:
    print("Database file NOT found.")
