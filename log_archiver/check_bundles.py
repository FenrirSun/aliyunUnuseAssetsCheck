import os
from datetime import datetime
from typing import Dict, List, Tuple

class BundleChecker:
    def __init__(self, db_path: str):
        self.base_dir = os.path.abspath("Check")
        os.makedirs(self.base_dir, exist_ok=True)

    def parse_bundle_file(self, file_path: str) -> Tuple[Dict[int, str], List[int]]:
        """
        解析文件并返回:
        - 索引到名称的映射 {index: name}
        - 所有索引列表 [index1, index2, ...]
        """
        index_to_name = {}
        all_indices = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            in_bundles = False
            for line in f:
                line = line.strip()
                if line.startswith('[Bundles]'):
                    in_bundles = True
                    continue
                elif line.startswith('[') and in_bundles:
                    break
                
                if in_bundles and line:
                    # 关键修改：只取第一个逗号前的部分作为索引
                    parts = line.split(',', 1)  # 只分割第一个逗号
                    if len(parts) >= 2:
                        try:
                            index = int(parts[0])
                            name = parts[1].split(',')[0].strip()  # 取第一个逗号后的内容作为名称
                            index_to_name[index] = f"{index},{name}"
                            all_indices.append(index)
                        except ValueError:
                            continue
        return index_to_name, all_indices

    def filter_and_save(self, 
                      ver_id: int,
                      runtime: str,
                      db_indices: List[int],
                      gameres_dir: str):
        """执行过滤并保存结果"""
        # 查找gameres文件
        bundle_files = [f for f in os.listdir(gameres_dir) if 'gameres' in f.lower()]
        if not bundle_files:
            print(f"未找到gameres文件: {gameres_dir}")
            return
        
        file_path = os.path.join(gameres_dir, bundle_files[0])
        index_to_name, _ = self.parse_bundle_file(file_path)
        
        # 执行过滤
        db_index_set = set(db_indices)
        filtered_names = [
            name for index, name in index_to_name.items()
            if index not in db_index_set
        ]

        filtered_index_str = ""
        for index, name in index_to_name.items():
            if index not in db_index_set:
                filtered_index_str = f"{filtered_index_str}{index},"
        # print("filtered_index_str: ",filtered_index_str)
        
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            self.base_dir, 
            f"ver_{ver_id}_{runtime}_{timestamp}.txt"
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n[ Un Use Bundle Index List ]")
            f.write(f"\n{filtered_index_str}\n")
            f.write("\n[ Un Use Bundle Name List ]\n")
            f.write("\n".join(filtered_names))
        
        print(f"\n=== 过滤结果 ===")
        print(f"原始数据行数: {len(index_to_name)}")
        print(f"过滤索引数量: {len(db_indices)}")
        print(f"保留数据数量: {len(filtered_names)}")
        print(f"结果文件路径: {output_path}")