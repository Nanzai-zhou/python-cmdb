#!/bin/python3
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from django.core.management import BaseCommand
from django.conf import settings

import json
import shutil
import os.path

# 导入ansible需要的一些模块
import ansible.constants as C
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible import context

# 从models导入create_or_replace
from asset.models import Host

# 创建一个回调插件类用于捕获ansible的输出
class ResultsCollectorJSONCallback(CallbackBase):
    # 在回调插件实例化时，添加三个字典属性，分别用于保存ansible执行成功、失败、主机不可达的三种结果
    # 在调用回调插件对象的时候，会自动根据result的结果，执行对应的实例方法。
    # 在这里我们只修改v2_runner_on_ok，让其调用create_or_replace
    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        print(result._host)
        print(result._result)
        

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result

    def collect_host(self, result):
        facts = result.get('ansible_facts', {})
        ip = facts.get('ansible_default_ipv4', {}).get('address', '0.0.0.0')
        hostname = facts.get('ansible_hostname', '')
        arch = facts.get('ansible_architecture', '')
        os = facts.get('ansible_distribution_file_variety', '') + ' ' + facts.get('ansible_distribution_version', '')
        mac = facts.get('ansible_default_ipv4', {}).get('macaddress', '')
        mem = facts.get('ansible_memtotal_mb', 0) / 1024
        cpu = facts.get('ansible_processor_count', 0)
        disk = json.dumps([ {"name": i.get('mount', ''), "total": i.get('size_total', 0), "free": i.get('size_available', 0)} for i in facts.get('ansible_mounts', {}) ])
        Host.create_or_replace(hostname=hostname, ip=ip, mac=mac, os=os, arch=arch, mem=mem, cpu=cpu, disk=disk)


class Command(BaseCommand):
    def handle(self, **options):
        #host_list为需要执行ansible命令的主机列表，按需修改
        #host_list = ['124.160.12.243']
        # 由于API的使用被构造成了一个CLI客户端，需要为CLI提供一些上下文环境参数，如
        # connection='smart' 为连接时自动判断使用原生的OpenSSH还是使用paramiko
        # module_path为ansible模块的路径，为一个列表，可以包含自己的插件路径
        # forks=10表示执行时，并发量为10
        # become=None表示不进行切换用户
        # become_method为切换用户的方式，如su，sudo等
        context.CLIARGS = ImmutableDict(connection='smart', module_path=['/usr/share/ansible'], forks=10, become=None,
                                        become_method=None, become_user=None, check=False, diff=False, verbosity=1)
        # 将主机列表拼接成字符串，之间用逗号隔开
        #sources = ','.join(host_list)
        #if len(host_list) == 1:
        #    sources += ','
    
        # 实例化一个DataLoder()对象
        loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files
        # passwords为连接远程主机的时，需要提供的密码，
        passwords = dict()
    
        # 实例化一个回调插件对象
        results_callback = ResultsCollectorJSONCallback()
    
        # 实例化一个InventoryManager仓库管理对象，参数loader为DataLoader对象，sources为需要执行命令的主机列表字符串
        inventory = InventoryManager(loader=loader, sources=os.path.join(settings.BASE_DIR, "etc","hosts"))
    
        # 实例化一个变量管理VariableManager对象，参数loader为DataLoader对象，inventory为InventoryManager对象
        variable_manager = VariableManager(loader=loader, inventory=inventory)
    
        # 实例化一个任务队列管理TaskQueueManager对象，参数inventory为InventoryManager对象，variable_manager为VariableManager对象，loader为DataLoader对象，passwords为密码字典
        # stdout_callback为回调插件对象
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=passwords,
            stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
        )
    
        # 构造一个playbook剧本字典，包含剧本任务的名称，需要执行剧本的主机列表，是否要收集主机信息，以及一个要执行的任务task的列表，元素task为一个字典
        # 在这里使用setup模块来收集主机的信息
        play_source = dict(
            name="collect_host",
            hosts="all",
            gather_facts='no',
            tasks=[dict(action=dict(module='script', user="zhouhn", args="collect_usage.py"), name="collect_host")]
        )
    
        # 创建一个Play对象，使用load的方法，将需要执行的剧本playbook，变量管理对象和loader传递进去
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    
        # Actually run it
        try:
            # 使用任务队列管理对象的run方法执行这个Play对象
            result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
        finally:
            # 不管结果如何，都清理任务管理对象
            tqm.cleanup()
            if loader:
                loader.cleanup_all_tmp_files()
    
        # 删除临时文件
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
