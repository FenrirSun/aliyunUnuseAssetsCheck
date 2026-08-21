
import time
from globalConfig import Config
from archiver import LogArchiver
import copy

MIN_CLUSTER_CHANGE = 4
MIN_USER_CHANGE = 2

class LogSender:

    def send(self, curr, startTime, endTime):
       LogArchiver().store_sensor_data(curr, "bundle_use.db")

    