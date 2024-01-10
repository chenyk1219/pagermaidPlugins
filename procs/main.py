# -*- coding: UTF-8 -*-
"""
@File    ：signal.py
@Author  ：https://t.me/iNextOpsChannel
@Date    ：2024/1/8 2:49
"""

from pyrogram import Client
from pagermaid.listener import listener
from pagermaid.utils import Message

try:
    import psutil
except:
    from pagermaid.utils import pip_install

    pip_install("psutil")
finally:
    import psutil


def convert_bytes(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def main():
    ad_pids = []
    procs = []
    context_list = []
    for p in psutil.process_iter():
        try:
            mem = p.memory_full_info()
            cpu = p.cpu_percent()
            info = p.as_dict(attrs=["cmdline", "username"])
        except psutil.AccessDenied:
            ad_pids.append(p.pid)
        except psutil.NoSuchProcess:
            pass
        else:
            p._uss = mem.uss
            p._rss = mem.rss
            if not p._uss:
                continue
            p._pss = getattr(mem, "pss", "")
            p._swap = getattr(mem, "swap", "")
            p._info = info
            p._cpu = cpu
            procs.append(p)

    procs.sort(key=lambda p: p.pid)
    templ = "%-13s %-30s %7s %7s %s"
    context_list.append(templ % ("PID", "Cmdline", "CPU", "内存", "Swap"))
    context_list.append(" ")
    for p in procs:
        line = templ % (
            p.pid,
            " ".join(p._info["cmdline"])[:20],
            p._cpu,
            convert_bytes(p._rss),
            convert_bytes(p._swap) if p._swap != "" else "",
        )
        context_list.append(str(line))
    if ad_pids:
        context_list.append("warning: access denied for %s pids" % (len(ad_pids)))

    return context_list


@listener(is_plugin=True, outgoing=True, command="procs",
          description="\n功能：查看服务器所有服务进程，看看有没有异常进程"
                      "\n安装方法：,install procs"
                      "\n使用方法：,procs"
                      "\n注意：此命令只在Linux系统下有效"
                      "\n\n作者：@inextopschannel"
                      "\n\n仓库：https://github.com/chenyk1219/pagermaidPlugins"
          )
async def procs(bot: Client, context: Message):
    context_list = main()
    await context.edit("\n".join(context_list))
