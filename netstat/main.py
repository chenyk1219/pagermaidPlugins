# -*- coding: UTF-8 -*-
"""
@File    ：signal.py
@Author  ：https://t.me/iNextOpsChannel
@Date    ：2024/1/8 2:49
"""

from pyrogram import Client
from pagermaid.listener import listener
from pagermaid.utils import Message
from pagermaid.utils import alias_command
import time
import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM

try:
    import psutil
except:
    from pagermaid.utils import pip_install

    pip_install("psutil")
finally:
    import psutil

AD = "-"
AF_INET6 = getattr(socket, 'AF_INET6', object())
proto_map = {
    (AF_INET, SOCK_STREAM): 'tcp',
    (AF_INET6, SOCK_STREAM): 'tcp6',
    (AF_INET, SOCK_DGRAM): 'udp',
    (AF_INET6, SOCK_DGRAM): 'udp6',
}


def get_netstat():
    context_list = []
    templ = "%-5s %-20s %-20s %-13s %-6s %s"
    context_list.append(templ % (
        "协议", "本地端口", "请求端", "状态", "PID", "进程名"))
    proc_names = {}
    for p in psutil.process_iter():
        try:
            proc_names[p.pid] = p.name()
        except psutil.Error:
            pass
    for c in psutil.net_connections(kind='inet'):
        laddr = "%s:%s" % c.laddr
        raddr = ""
        if c.raddr:
            raddr = "%s:%s" % c.raddr
        context_list.append(templ % (
            proto_map[(c.family, c.type)],
            laddr,
            raddr or AD,
            c.status,
            c.pid or AD,
            proc_names.get(c.pid, '?')[:15],
        ))

    return context_list


@listener(is_plugin=True, outgoing=True, command="netstat",
          description="功能：1. 查看服务器所有启动的端口 2. 这些端口的连接情况，看看有没有异常连接"
                      "\n安装方法：,install netstat"
                      "\n使用方法：,netstat"
                      "\n注意：此命令只在Linux系统下有效"
                      "\n\nports命令只能查看单一端口，这个算是plus版本吧，查所有端口，会显示具体的ip，建议私发"
                      "\n\n作者：@inextopschannel"
                      "\n\n仓库：https://github.com/chenyk1219/pagermaidPlugins"
          )
async def netstat(bot: Client, context: Message):
    context_list = get_netstat()
    await context.edit("\n".join(context_list))
