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
import subprocess
import time

try:
    import psutil
except:
    from pagermaid.utils import pip_install

    pip_install("psutil")
finally:
    import psutil


def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9.8 K'
    >>> bytes2human(100001221)
    '95.4 M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)


def poll(interval):
    """Retrieve raw stats within an interval window."""
    tot_before = psutil.net_io_counters()
    pnic_before = psutil.net_io_counters(pernic=True)
    # sleep some time
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)
    return (tot_before, tot_after, pnic_before, pnic_after)


def get_net_top(tot_before, tot_after, pnic_before, pnic_after):
    # totals
    context_list = []

    context_list.append("total bytes:           sent: %-10s   received: %s" % (
        bytes2human(tot_after.bytes_sent),
        bytes2human(tot_after.bytes_recv))
                        )
    context_list.append("total packets:         sent: %-10s   received: %s" % (
        tot_after.packets_sent, tot_after.packets_recv))

    # per-network interface details: let's sort network interfaces so
    # that the ones which generated more traffic are shown first
    context_list.append("")
    nic_names = list(pnic_after.keys())
    nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
    for name in nic_names:
        stats_before = pnic_before[name]
        stats_after = pnic_after[name]
        templ = "%-15s %15s %15s"
        context_list.append(templ % (name, "TOTAL", "PER-SEC"))
        context_list.append(templ % (
            "bytes-sent",
            bytes2human(stats_after.bytes_sent),
            bytes2human(
                stats_after.bytes_sent - stats_before.bytes_sent) + '/s',
        ))
        context_list.append(templ % (
            "bytes-recv",
            bytes2human(stats_after.bytes_recv),
            bytes2human(
                stats_after.bytes_recv - stats_before.bytes_recv) + '/s',
        ))
        context_list.append(templ % (
            "pkts-sent",
            stats_after.packets_sent,
            stats_after.packets_sent - stats_before.packets_sent,
        ))
        context_list.append(templ % (
            "pkts-recv",
            stats_after.packets_recv,
            stats_after.packets_recv - stats_before.packets_recv,
        ))
        context_list.append("")
    return context_list


@listener(is_plugin=True, outgoing=True, command="nettop",
          description="查看服务器所有网卡流量信息"
                      "\n安装方法：,install nettop"
                      "\n使用方法：,nettop"
                      "\n注意：此命令只在Linux系统下有效"
                      "\n\n作者：@inextopschannel"
                      "\n\n仓库：https://github.com/chenyk1219/pagermaidPlugins"
          )
async def get_net(bot: Client, context: Message):
    interval = 0
    args = poll(interval)
    context_list = get_net_top(*args)
    await context.edit("\n".join(context_list))
