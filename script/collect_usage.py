#!/bin/python3
# -*- coding: utf-8 -*-

import os

if __name__ == '__main__':
    with os.popen('top -n 1') as f:
        result = f.readlines()
        cpu_usage = result[2].split()[1]
    with os.popen('free -g') as f:
        result = f.readlines()
        mem_usage = float(int(result[1].split()[2]) / int(result[1].split()[1]))
    print(cpu_usage)
    print(mem_usage)
