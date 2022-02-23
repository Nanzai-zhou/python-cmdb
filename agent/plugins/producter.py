# -*- encoding: utf-8 -*-
import time
from  agent.utils import sysutils
import json
import logging
logger = logging.getLogger()

# 采集主机信息，默认每3600秒上报一次
def collect_hostinfo(queue=None, interval=3600, type='client'):
    while True:
        _dict =  {
            "type": type,
            "ip": sysutils.get_ip(),
            "msg": {
                "hostname": sysutils.get_hostname(),
                "mac": sysutils.get_mac(),
                "platform": sysutils.get_platform(),
                "arch": sysutils.get_arch(),
                "cpu": sysutils.get_cpu(),
                "mem": sysutils.get_mem(),
            }
        }
        logger.info(f"host: {_dict}")
        q = queue
        q.put(_dict)
        logger.info(f"put host into queue")
        time.sleep(interval)

# 采集主机资源利用率，默认60s上报一次
def collect_resource(queue=None, interval=60, type='resource'):
    while True:
        _dict = {
            "type": type,
            "ip": sysutils.get_ip(),
            "msg": {
                "cpu_usage": sysutils.get_cpu_usage(),
                "mem_usage": sysutils.get_mem_usage()
            }
        }
        logger.info(f"resource: {_dict}")
        q = queue
        q.put(_dict)
        logger.info(f"put resource into queue")
        time.sleep(interval)

# 发送心跳包，默认30s上报一次
def heartbeat(queue=None, interval=30, type='heartbeat'):
    while True:
        _dict = {
            "type": type,
            "ip": sysutils.get_ip(),
            "msg": {
                "ip": sysutils.get_ip()
            }
        }
        q = queue
        q.put(_dict)
        logger.info(f"put heartbeat into queue")
        time.sleep(interval)
