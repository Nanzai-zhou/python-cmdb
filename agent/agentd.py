# -*- encoding: utf-8 -*-
import logging
import configparser
from queue import Queue
from plugins.producter import collect_hostinfo, collect_resource, heartbeat
from plugins.consumer import consumer
from threading import Thread
import time

def main():
    # 初始化agentd
    # 读取配置
    config = configparser.ConfigParser()
    config.read('agent.ini')

    # 初始化日志
    log_path = config['log']['path']
    log_level = config['log']['level']
    log_format = '%(asctime)s %(module)s [%(levelname)s]: %(message)s'
    logging.basicConfig(filename=log_path, format=log_format)
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 获得上报server的ip和端口
    server_ip = config['server']['ip']
    server_port = config['server']['port']
    logger.info(f'server_ip: {server_ip}, server_port: {server_port}')
    # 创建队列
    q = Queue(maxsize=10)
    logger.info('create queue')

    # 创建线程
    th_host = Thread(target=collect_hostinfo, kwargs={"queue": q}, daemon=True)
    th_resource = Thread(target=collect_resource, kwargs={"queue": q}, daemon=True)
    th_heartbeat = Thread(target=heartbeat, kwargs={"queue": q}, daemon=True)
    th_consumer = Thread(target=consumer, kwargs={"queue": q, "server_ip": server_ip, "server_port": server_port}, daemon=True)
    th_host.start()
    th_resource.start()
    th_heartbeat.start()
    th_consumer.start()
    while True:
        time.sleep(3)


if __name__ == '__main__':
    main()