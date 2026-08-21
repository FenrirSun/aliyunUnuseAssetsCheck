# database.py
import sqlite3
import time
from typing import List, Dict
import os

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock_file = f"{db_path}.lock"

    def _wait_for_lock(self, timeout=30):
        """等待数据库锁释放"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with open(self.lock_file, 'x'):
                    return True
            except FileExistsError:
                time.sleep(0.5)
        return False

    def _release_lock(self):
        """释放锁"""
        try:
            os.remove(self.lock_file)
        except:
            pass

    def get_ver_id_combinations(self, runtime: int) -> List[Dict[str, str]]:
        """获取ver_id关联的所有url和runtime组合"""
        if not self._wait_for_lock():
            raise Exception("无法获取数据库锁，操作超时")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建主表（如果不存在）
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ver_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                runtime TEXT NOT NULL,
                UNIQUE(ver_id, url, runtime)
            )""")
            
            cursor.execute(
                "SELECT runtime, url, runtime FROM versions WHERE runtime = ?",
                (runtime,)
            )

            return [
                {"ver_id": row[0], "url": row[1], "runtime": row[2]} 
                for row in cursor.fetchall()
            ]
        finally:
            self._release_lock()
            conn.close()

    def get_bundle_indices(self, ver_id: int, url: str, runtime: str, playerLevel: int) -> List[int]:
        """获取ver_id、url和runtime组合的bundle_index列表"""
        if not self._wait_for_lock():
            raise Exception("无法获取数据库锁，操作超时")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM versions WHERE ver_id = ? AND url = ? AND runtime = ?",
                (ver_id, url, runtime)
            )
            result = cursor.fetchone()
            
            if not result:
                return []
            
            # version_id = result[0]
            table_name = f"ver_{ver_id}_{runtime}"

            cursor.execute(f"""
                SELECT bundle_index FROM {table_name} 
                ORDER BY bundle_index
                """, (playerLevel,)
            )
            
            #cursor.execute(f"SELECT bundle_index FROM {table_name} ORDER BY bundle_index")
            return [row[0] for row in cursor.fetchall()]
        finally:
            self._release_lock()
            conn.close()