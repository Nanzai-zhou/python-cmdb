import socket
import uuid
import platform
import psutil
from datetime import datetime

# 获取主机名hostname
def get_hostname():
    hostname = socket.gethostname()
    return hostname

# 获取本机ip
def get_ip():
    hostname = get_hostname()
    ip = socket.gethostbyname(hostname)
    return ip

# 获取本机网卡mac地址
def get_mac():
    node = uuid.getnode()
    m = uuid.UUID(int=node).hex[-12:]
    mac = ':'.join([ m[i:i+2] for i in range(0, 12, 2) ])
    return mac

# 获取操作系统信息
def get_platform():
    os = platform.platform()
    return os

# 获取主机架构
def get_arch():
    arch = platform.machine()
    return arch

def get_cpu():
    cpu = psutil.cpu_count()
    return cpu

def get_mem():
    mem_info = psutil.virtual_memory()
    mem_total = round(mem_info.total / 1024 / 1024 / 1024, 2)
    return mem_total

def get_time():
    time = datetime.now()
    return time

def get_cpu_usage():
    cpu_usage = psutil.cpu_percent()
    return cpu_usage

def get_mem_usage():
    mem_usage = psutil.virtual_memory().percent
    return mem_usage
