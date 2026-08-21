import json
# import pandas as pd
import numpy as np
from globalConfig import Config
import time
import re
import zlib
from typing import Union
# from sentence_transformers import SentenceTransformer
# from nltk.stem import WordNetLemmatizer

# lemmatizer = WordNetLemmatizer()
# def lemmatize_text(text):
#         return " ".join([lemmatizer.lemmatize(word) for word in text.split()])

class Processor:

    def receive_data(self, logs):
        # 定时搜索日志后直接传入
        return logs

    # 数据预处理
    def process(self, text):
        try:
            log_json = text
            
            data_list = []
            log_num = 0
            for log in text:
                resp = log[Config.resp_id_name]
                # 资源版本号
                ver = log[Config.bundle_version]
                ver_match = re.search(r'^(\d+)\.', ver) 
                bundle_ver = -1
                if ver_match:
                    bundle_ver = ver_match.group(1)
                
                runtime = log[Config.runtime_id]
                if runtime is None or not runtime.strip():
                    runtime = "Unknown"

                # 解压缩 
                remove_flag_resp = resp.removeprefix("BundleUseIndex:") #去掉日志关键词

                origin_resp = self.decompress(remove_flag_resp)
                if not origin_resp:
                    continue
                # 解析 bundle 的 id 列表
                # bundle_ids = re.findall(r'\d+', origin_resp)
                # for id in bundle_ids:
                #     print("bundle Id: ", id)
                #     data_list.append({"ver_id":bundle_ver, "bundle_index":id})
                
                parts = origin_resp.split('|')
                # print("parts:", parts)
                
                if len(parts) > 3:  # 确保有至少4个部分  url,level,serverId,indexList
                    url = parts[0].strip()
                    print(" # log ")
                    print(" ------- manifest url: ", url)
                    length = max(0, len(parts) - 3) if len(parts) > 3 else 0
                    print(" ------- parts len: ", length)
                    playerLevel = parts[1]
                    print(" ------- player level: ", parts[1])
                    serverId = parts[2]
                    print(" ------- player serverId: ", parts[2])

                    for id_str in parts[3:]:
                        # 去除可能的空白字符
                        clean_id = id_str.strip()
                        if clean_id:  # 确保非空
                            # print("bundle Id: ", clean_id)
                            data_list.append(
                                {
                                    "ver_id": bundle_ver, 
                                    "bundle_index": clean_id,
                                    "url": url,
                                    "runtime": runtime,
                                    "playerLevel": playerLevel,
                                    "serverId": serverId,
                                }
                            )
                log_num = log_num + 1
            print("共处理日志数量：", log_num)
            return data_list
        except json.JSONDecodeError:
            return None

    def decompress(self, compressed_str: str) -> str:
        """
        解压缩经过 Ascii85 编码和 Deflate 压缩的字符串
        
        输出: 原始解压后的字符串
        """
        # 步骤1: Ascii85 解码
        def ascii85_decode(encoded: str) -> bytes:
            if not encoded:
                return b""
            
            block_count = (len(encoded) + 4) // 5
            decoded = bytearray(block_count * 4)
            decoded_index = 0
            value = 0
            count = 0
            
            for c in encoded:
                if c == 'z' and count == 0:
                    decoded[decoded_index:decoded_index+4] = b"\0\0\0\0"
                    decoded_index += 4
                    continue
                
                if ord(c) < 33 or ord(c) > 117:
                    print("[Error] 无效的 Ascii85 字符:", c)
                    return None
                
                char_value = ord(c) - 33
                value = value * 85 + char_value
                count += 1
                
                if count == 5:
                    decoded[decoded_index] = (value >> 24) & 0xFF
                    decoded[decoded_index+1] = (value >> 16) & 0xFF
                    decoded[decoded_index+2] = (value >> 8) & 0xFF
                    decoded[decoded_index+3] = value & 0xFF
                    decoded_index += 4
                    count = 0
                    value = 0
            
            if count > 0:
                for _ in range(5 - count):
                    value = value * 85 + 84
                
                decoded[decoded_index] = (value >> 24) & 0xFF
                decoded[decoded_index+1] = (value >> 16) & 0xFF
                decoded[decoded_index+2] = (value >> 8) & 0xFF
                decoded[decoded_index+3] = value & 0xFF
                decoded_index += 4
            
            return bytes(decoded[:decoded_index])
        
        # 步骤2: Deflate 解压 (使用原始 DEFLATE 格式)
        deflate_data = ascii85_decode(compressed_str)
        if not deflate_data:
            return
        # 使用 zlib 解压原始 DEFLATE 数据 (wbits=-15 表示无头尾的原始 DEFLATE)
        decompressed_bytes = zlib.decompress(deflate_data, wbits=-15)
        # 步骤3: 将字节解码为 UTF-8 字符串
        return decompressed_bytes.decode('utf-8')
    
    def run_data(self,logs):
        # 读取本地文件log.json
        # with open('log.json', 'r', encoding='utf-8') as f:
        #     logs = json.load(f)
        step1Time = time.time()
        # _logs = self.receive_data(logs)
        result = self.process(logs)
        step3Time = time.time()
        print(f"process time: {step3Time - step1Time}")
        return result