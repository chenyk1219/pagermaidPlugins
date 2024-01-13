# -*- coding: UTF-8 -*-
"""
@File    ：signal.py
@Author  ：https://t.me/iNextOpsChannel
@Date    ：2024/1/8 2:49
"""

from pyrogram import Client
from pagermaid.listener import listener
from pagermaid.utils import Message
import os
import subprocess


@listener(is_plugin=True, outgoing=True, command="baopo",
          description="查看服务器被爆破登陆的信息"
                      "\n安装方法：,install baopo"
                      "\n使用方法：,baopo"
                      "\n注意：此命令只在Linux系统下有效"
                      "\n\n作者：@inextopschannel"
                      "\n\n仓库：https://github.com/chenyk1219/pagermaidPlugins"
          )
async def baopo(bot: Client, context: Message):
    await context.edit("开始检查爆破IP...")
    templ = "%-15s %15s"
    context_list = []
    context_list.append(templ % ("爆破IP", "爆破次数"))
    if os.path.exists('/var/log/secure'):
        shell = "grep \"Invalid user\" /var/log/secure | awk -F'from' '{print $2}' | awk -F' ' '{print $1}' | sort | uniq -c | sort -nr | head -n10"
        faild_log = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT).stdout.read().decode(
            'utf-8').split('\n')
        for line in faild_log:
            if line:
                line = line.strip()
                context_list.append(templ % (line.split(' ')[1], line.split(' ')[0]))

        await context.edit("\n".join(context_list))
    elif os.path.exists('/var/log/auth.log'):
        shell = "grep \"Invalid user\" /var/log/auth.log | awk -F'from' '{print $2}' | awk -F' ' '{print $1}' | sort | uniq -c | sort -nr | head -n10"
        faild_log = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT).stdout.read().decode(
            'utf-8').split('\n')
        for line in faild_log:
            if line:
                line = line.strip()
                context_list.append(templ % (line.split(' ')[1], line.split(' ')[0]))

        await context.edit("\n".join(context_list))
    else:
        await context.edit("error：无法找到日志文件，爆破IP查询失败！")

