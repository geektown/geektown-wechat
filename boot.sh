#!/bin/bash

kill -9 $(ps -ef | grep "/usr/bin/python wechatservice.py" | grep -v grep | awk '{print $2}')
cd /home/xiaoi/geektown-wechat
export PYTHONPATH=/home/xiaoi/robot
nohup python wechatservice.py >/dev/null 2>&1 &