import argparse
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from log_archiver.database import DatabaseManager

def generate_output_filename():
    """生成带时间戳的输出文件名"""
    return f"level_bundleIndex_pairs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def main():
    parser = argparse.ArgumentParser(
        description="获取小于等于指定等级的所有player_level和bundle_index组合并保存为JSON"
    )
    parser.add_argument("runtime", type=int, help="要查询的版本平台")
    parser.add_argument("--db", default="bundle_use.db", help="数据库文件路径")
    # parser.add_argument("--output", default="level_bundleIndex_pairs.json", 
    #                    help="输出JSON文件路径")
    args = parser.parse_args()

    try:
        output_dir = Path("LevelJson")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / generate_output_filename()

        db_manager = DatabaseManager(args.db)
        
        # 获取所有ver_id、url和runtime组合
        combinations = db_manager.get_ver_id_combinations(args.runtime)

        if not combinations:
            print(f"没有找到ver_id={args.ver_id}的记录")
            return

        # 最终结果字典 {player_level: [bundle_indices]}
        final_result: Dict[int, List[int]] = {}

        for combo in combinations:
            print(f"处理组合: ver_id={combo['ver_id']}, "
                  f"url={combo['url']}, runtime={combo['runtime']}")
            
            # 获取该组合下所有<=max_player_level的记录
            level_bundles = db_manager.get_bundle_indices(
                ver_id=combo["ver_id"],
                url=combo["url"],
                runtime=combo["runtime"],
            )
            
            # 合并到最终结果中
            for level, indices in level_bundles.items():
                if level not in final_result:
                    final_result[level] = []
                
                # 添加不重复的bundle_index
                final_result[level].extend(
                    idx for idx in indices 
                    if idx not in final_result[level]
                )
        
        # 按player_level排序并整理bundle_index列表
        sorted_result = {
            str(level): sorted(indices) 
            for level, indices in sorted(final_result.items())
        }
        
        # 确保输出目录存在
        # output_path = Path(args.output)
        # output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存为JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_result, f, ensure_ascii=False, indent=2)
        
        print(f"成功生成结果，已保存到 {output_path.absolute()}")
        print(f"包含 {len(sorted_result)} 个不同等级的数据")

    except Exception as e:
        print(f"错误: {str(e)}")
        raise  # 调试时可取消注释以查看完整堆栈跟踪

if __name__ == "__main__":
    main()