import requests
from typing import List

class FileDownloader:
    @staticmethod
    def download_url(url: str) -> str:
        """下载URL内容"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"下载失败: {str(e)}")