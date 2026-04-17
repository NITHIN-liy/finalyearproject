import os
import time

db_path = 'instance/legal_ai.db'
for i in range(5):
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Successfully deleted {db_path}")
        else:
            print(f"{db_path} does not exist.")
        break
    except Exception as e:
        print(f"Attempt {i+1} failed: {e}")
        time.sleep(1)
