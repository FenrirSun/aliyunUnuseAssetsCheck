# db_init.py
import sqlite3

def init_db(db_path="bundle_use.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建主表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ver_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        runtime TEXT NOT NULL,
        UNIQUE(ver_id, url, runtime)
    )""")
    
    # 提交并关闭
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()