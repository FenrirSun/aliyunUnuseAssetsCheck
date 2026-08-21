import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler
from globalConfig import Config
from LogProcessor.LogProcessService import LogProcessService
from concurrent.futures import ThreadPoolExecutor
import threading
import logging

class Application:
    def __init__(self):
        self.log_service = LogProcessService()
        # 配置线程池执行器
        executors = {
            'default': {'type': 'threadpool', 'max_workers': 3}
        }
        
        # 创建调度器并配置执行器
        self.scheduler = BlockingScheduler(executors=executors)
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def process_logs_wrapper(self):
        thread_name = threading.current_thread().name
        print(f"Starting task in {thread_name}")
        self.log_service.process_logs()
        print(f"Finished task in {thread_name}")

    def start(self):
        # 设置定时任务，允许最多2个实例同时运行
        self.scheduler.add_job(
            self.process_logs_wrapper,
            'interval',
            minutes=Config.time_range,
            max_instances=3,  # 最多同时运行2个任务
            misfire_grace_time=None,  # 错过的任务会立即执行
            coalesce=True  # 不合并错过的任务
        )
        
        # 立即执行一次日志处理
        self.process_logs_wrapper()
        
        # 启动调度器
        self.scheduler.start()

if __name__ == "__main__":
    app = Application()
    try:
        app.start()
    except KeyboardInterrupt:
        print("Shutting down...")
        app.scheduler.shutdown(wait=False)