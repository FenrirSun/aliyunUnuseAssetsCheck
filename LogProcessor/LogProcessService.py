from apscheduler.schedulers.blocking import BlockingScheduler
from LogProcessor.log import logFetcher
from LogProcessor.processor import Processor
from LogProcessor.sender import LogSender
from globalConfig import Config
import datetime
import time
import pytz

# 将原有的日志处理逻辑移到单独的服务类中
class LogProcessService:
    def __init__(self):
        self.processor = Processor()
        self.fetcher = logFetcher()
        self.sender = LogSender()
        self.prev = None
        self.last_full_summary_time = datetime.datetime.fromtimestamp(0, pytz.timezone('Asia/Shanghai'))
        
    def process_logs(self):
        # 原 fetchErrorTask 的逻辑
        Config.reload_config_from_local()
        startTime = time.time()
        logs, from_time, error_time = self.fetcher.fetchErrorOnce()
        stepTime = time.time()
        print("获取日志耗时：",stepTime-startTime)
        # 处理日志
        processed_logs = self.processor.run_data(logs)
        step2Time = time.time()
        print("处理日志耗时：",step2Time-stepTime)
        # # # 发送数据
        self.sender.send(processed_logs,from_time,error_time)
        # 保存上次数据
        # self.prev = processed_logs
