# storage.py
import os
import zipfile
import tempfile
from datetime import datetime
from typing import Optional

class FileStorage:
    @staticmethod
    def download_and_extract(url: str, ver_id: int, runtime: str) -> Optional[str]:
        """下载并解压文件到目标目录"""
        try:
            import requests
            from io import BytesIO
            
            # 下载文件
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            # 解压到目标目录
            output_dir = os.path.abspath(os.path.join("Download/"+ runtime, str(ver_id)))
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            
            # 清理临时文件
            os.unlink(tmp_path)
            
            return output_dir
        except Exception as e:
            print(f"下载或解压失败: {str(e)}")
            return None