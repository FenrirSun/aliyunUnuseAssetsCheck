import sqlite3
from typing import List, Dict


class LogArchiver:

    def store_sensor_data(self, data, db_path):
        """
        存储传感器数据到SQLite数据库
        
        每个ver_id对应一张表，表结构为:
            bundle_index INTEGER PRIMARY KEY
        
        参数:
        data -- 传感器数据列表，每个字典包含ver_id和bundle_index
        db_path -- SQLite数据库文件路径 (默认: 'sensor_data.db')
        
        功能:
        1. 为每个ver_id创建单独的表（如果不存在）
        2. 只插入表中不存在的bundle_index值
        """
        # 验证数据格式
        if not data:
            print("警告: 没有数据可存储")
            return
        
        # 检查数据格式
        # print("data : ", data)
        # print("db_path : ", db_path)
        
        required_fields = {"ver_id", "bundle_index", "url"}
        for item in data:
            if not required_fields.issubset(item.keys()):
                raise ValueError(f"每个数据项必须包含{required_fields}")
        
        conn = None
        try:
            # 连接数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 创建主表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ver_id INTEGER NOT NULL,
                runtime TEXT NOT NULL,
                url TEXT NOT NULL,
                UNIQUE(ver_id, runtime, url)  -- 3个字段组合唯一
            )
            """)
            
            # 统计信息
            tables_created = 0
            new_records = 0
            existing_records = 0
            
            # 处理每个数据项
            for item in data:
                ver_id = int(item["ver_id"])
                bundle_index = int(item["bundle_index"])
                url = str(item["url"])
                runtime = str(item["runtime"]) 
                playerLevel = int(item["playerLevel"])
                
                cursor.execute(
                    "INSERT OR IGNORE INTO versions (ver_id, runtime, url) VALUES (?, ?, ?)",
                    (ver_id, runtime, url)
                )
                
                cursor.execute(
                    "SELECT id FROM versions WHERE ver_id = ? AND runtime = ? AND url = ?",
                    (ver_id, runtime, url)
                )
                version_id = cursor.fetchone()[0]
                #print("version_id: ", version_id)
                # 为每个ver_id创建表名
                table_name = f"ver_{ver_id}_{runtime}"
                #print("table_name: ", table_name)
                
                # 创建表（如果不存在）
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    bundle_index INTEGER NOT NULL,
                    playerLevel INTEGER NOT NULL,
                    PRIMARY KEY (bundle_index, playerLevel)
                )
                """
                cursor.execute(create_table_sql)
                if cursor.rowcount != -1:  # 如果表是新创建的
                    tables_created += 1
                    print("创建新表 table_name: ", table_name)
                
                # # 检查bundle_index是否已存在
                # check_sql = f"SELECT 1 FROM {table_name} WHERE bundle_index = ?"
                # cursor.execute(check_sql, (bundle_index,))
                # exists = cursor.fetchone()

                insert_sql = f"""
                INSERT OR IGNORE INTO {table_name} (bundle_index, playerLevel) 
                VALUES (?, ?)
                """
                cursor.execute(insert_sql, (bundle_index, playerLevel))
                
                # if exists:
                #     existing_records += 1
                # else:
                #     # 插入新记录
                #     insert_sql = f"INSERT INTO {table_name} (bundle_index) VALUES (?)"
                #     cursor.execute(insert_sql, (bundle_index,))
                #     new_records += 1

                if cursor.rowcount > 0:
                    new_records += 1
                else:
                    existing_records += 1
            
            # 提交事务
            conn.commit()
            
            # 打印统计信息
            print(f"数据存储完成: "
                f"创建了 {tables_created} 个新表, "
                f"添加了 {new_records} 条新记录, "
                f"跳过了 {existing_records} 条已存在记录")
        
        except sqlite3.Error as e:
            print(f"数据库错误: {str(e)}")
            if conn:
                conn.rollback()
        
        finally:
            if conn:
                conn.close()