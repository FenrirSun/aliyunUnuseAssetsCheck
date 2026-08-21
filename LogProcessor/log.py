import os
import time
from aliyun.log import *
from globalConfig import Config
import json

class logFetcher:
  def __init__(self):
     self.client = LogClient(Config.endpoint, Config.access_key_id, Config.access_key_secret)

  # def fetchLogs(self, query, from_time, to_time):
  #   request = GetLogsRequest(project, logStore, from_time, to_time, '', query=query, line=100, offset=0, reverse=False)
  #   response = self.client.get_logs(request)
  #   return response.get_logs(), from_time, to_time
  
  def fetchErrorOnce(self):
    print("ready to query logs from logstore %s" % Config.logStore)
    # from_time和to_time表示查询日志的时间范围，UNIX时间戳格式。
    now = time.time()
    from_time = now - Config.time_range * 60
    to_time = now

    print('now time:', to_time)
    # 本示例中，query参数用于设置查询语句；line参数用于控制返回日志条数，line取值为100。
    request = GetLogsRequest(Config.project, Config.logStore, from_time, to_time, '', query=Config.query, line=Config.max_query_logs, offset=0, reverse=False)
    response = self.client.get_logs(request)
    # 打印查询结果。
    print('-------------Query is started.-------------')
    logs = response.get_logs()
    # log数量
    print('The number of logs is:', len(logs))
    # 将logs转换成json格式
    log_jsons = []
    for log in logs:
      log_content = log.get_contents()
      # # 过滤掉有deviceId，但不以_n3d结尾的日志
      # if 'deviceId' in log_content and not log_content['deviceId'].endswith('_n3d'):
      #   # 打印出来
      #   print("不是真实玩家的日志，设备ID为：", log_content['deviceId'],"uid为：",log_content.get('uid',''))
      #   continue
      log_jsons.append(log_content)
    # 将log保存在本地
    # with open('log.json', 'w', encoding='utf-8') as f:
    #   json.dump(log_jsons, f, ensure_ascii=False, indent=4)
    print('-------------Query is finished.-------------')
    return log_jsons,from_time,to_time