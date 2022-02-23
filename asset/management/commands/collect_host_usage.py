#!/bin/python3
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from django.core.management import BaseCommand
from django.conf import settings

import json
import shutil
import os.path
import time

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

from asset.models import Host, Resource

# 创建一个回调插件类用于捕获ansible的输出
class ResultsCollectorJSONCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        # 使用setpup模块建立host和ip对应的字典
        if result.task_name == "collect_ip":
            facts = result._result.get('ansible_facts', {})
            ip = facts.get('ansible_default_ipv4', {}).get('address', '0.0.0.0')
            host = result._host
            self.host_ok[host.get_name()] = ip
        # 根据host取出ip，然后在Resource表中插入该ip的cpu和内存利用率
        if result.task_name == "collect_usage":
            print(result._result['stdout_lines'])
            ip = self.host_ok[result._host.get_name()]
            usage_list = result._result['stdout_lines']
            cpu_usage = round(float(usage_list[0]), 2)
            mem_usage = round(float(usage_list[1]), 2)
            Resource.create(ip, cpu_usage, mem_usage)


    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result


class Command(BaseCommand):
    def handle(self, **options):
        while True:
            # 由于API的使用被构造成了一个CLI客户端，需要为CLI提供一些上下文环境参数，如
            # connection='smart' 为连接时自动判断使用原生的OpenSSH还是使用paramiko
            # module_path为ansible模块的路径，为一个列表，可以包含自己的插件路径
            # forks=10表示执行时，并发量为10
            # become=None表示不进行切换用户
            # become_method为切换用户的方式，如su，sudo等
            context.CLIARGS = ImmutableDict(connection='smart', module_path=['/usr/share/ansible'], forks=10, become=None,
                                            become_method=None, become_user=None, check=False, diff=False, verbosity=1)

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
            # 在这里使用setup模块来收集主机的ip
            # 使用script模块在远程主机上执行本地脚本收集主机资源利用率。
            script_path = os.path.join(settings.BASE_DIR, 'script', 'collect_usage.py')
            play_source = dict(
                name="collect_host",
                hosts="all",
                gather_facts='no',
                tasks=[
                    dict(action=dict(module='setup'), name="collect_ip"),
                    dict(action=dict(module='script', user="zhouhn", args=script_path), name="collect_usage"),
                    ]
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
            time.sleep(60)