# cli.py
import argparse
from database import DatabaseManager
from storage import FileStorage
from check_bundles import BundleChecker 

def main():
    parser = argparse.ArgumentParser(description="下载ver_id关联的URL内容并解压")
    parser.add_argument("ver_id", type=int, help="要查询的版本ID")
    parser.add_argument("--playerLevel", default=35, type=int, help="要查询的等级")
    parser.add_argument("--db", default="bundle_use.db", help="数据库文件路径")
    args = parser.parse_args()

    try:
        db_manager = DatabaseManager(args.db)
        checker = BundleChecker(args.db)
        
        # 获取所有ver_id、url和runtime组合
        combinations = db_manager.get_ver_id_combinations(args.ver_id)

        if not combinations:
            print(f"没有找到ver_id={args.ver_id}的记录")
            return

        for combo in combinations:
            # 获取bundle_index列表
            indices = db_manager.get_bundle_indices(
                combo["ver_id"], 
                combo["url"], 
                combo["runtime"],
                args.playerLevel
            )
            
            print(f"处理组合: ver_id={combo['ver_id']}, url={combo['url']}, runtime={combo['runtime']}")
            
            # 下载并解压文件
            output_dir = FileStorage.download_and_extract(
                combo["url"],
                combo["ver_id"],
                combo["runtime"]
            )
            
            if not output_dir:
                print("文件处理失败")
                continue
            
            print(f"文件已解压到: {output_dir}")
            print(f"关联的bundle_index数量: {len(indices)}")

            # 自动执行索引检查
            print("\n开始检查索引差异...")
            checker.filter_and_save(
                ver_id=combo["ver_id"],
                runtime=combo["runtime"],
                db_indices=indices,
                gameres_dir=output_dir
            )

    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()