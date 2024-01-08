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
    pip_install("prettytable")
    #subprocess.Popen("python3 -m pip3 install psutil prettytable").wait()
finally:
    import psutil
    import prettytable


@listener(is_plugin=True, outgoing=True, command=alias_command("ports"), description="检查服务器端口连接情况")
async def ports(bot: Client, context: Message):
    context_list = []

    startTime = time.time()

    port = 22

    if len(context.parameter) == 0:
        context_list.append("error：未指定端口号，比如 ,ports 22，即将检测默认端口22！")
        await context.edit("\n".join(context_list))
    else:
        try:
            port = int(context.parameter[0])
            if port < 0 or port > 65535:
                context_list.append("error：端口号范围为0-65535，比如 ,ports 22，即将检测默认端口22！")
                await context.edit("\n".join(context_list))
        except:
            context_list.append("error：端口号必须为数字，比如 ,ports 22，即将检测默认端口22！")
            await context.edit("\n".join(context_list))
        finally:
            context_list.append(" ")
    # define data structure for each connection, each ip is unique unit
    ipaddress = {
        'ipaddress': None,
        'counts': 0,
        'stat': {
            'established': 0,
            'time_wait': 0,
            'others': 0
        }
    }

    # define data structure for statistics
    statistics = {
        'portIsUsed': False,
        'portUsedCounts': 0,
        'portPeerList': [
            {
                'ipaddress': None,
                'counts': 0,
                'stat': {
                    'established': 0,
                    'time_wait': 0,
                    'others': 0
                },
            },
        ]
    }

    tmp_portPeerList = list()
    portPeerSet = set()
    netstat = psutil.net_connections()

    # get all ip address only for statistics data
    for i, sconn in enumerate(netstat):

        if port in sconn.laddr:
            statistics['portIsUsed'] = True
            if len(sconn.raddr) != 0:
                statistics['portUsedCounts'] += 1
                ipaddress['ipaddress'] = sconn.raddr[0]
                tmp_portPeerList.append(str(ipaddress))  # dict() list() set() is unhashable type, collections.Counter

    for ip in tmp_portPeerList:
        portPeerSet.add(str(ip))  # remove duplicated ip address using set()

    for member in portPeerSet:
        statistics['portPeerList'].append(eval(member))

    # add statistics data for each ip address
    for sconn in netstat:
        if port in sconn.laddr:
            if len(sconn.raddr) != 0:
                for i, item in enumerate(statistics['portPeerList']):
                    if item['ipaddress'] == sconn.raddr[0]:
                        statistics['portPeerList'][i]['counts'] += 1
                        if sconn.status == 'ESTABLISHED':
                            statistics['portPeerList'][i]['stat']['established'] += 1
                        elif sconn.status == 'TIME_WAIT':
                            statistics['portPeerList'][i]['stat']['time_wait'] += 1
                        else:
                            statistics['portPeerList'][i]['stat']['others'] += 1

    # print statistics result using prettytable
    if statistics['portIsUsed']:
        context_list.append(" %s 端口总连接数为： %d." % (port, statistics['portUsedCounts']))
        context_list.append(" ")
        for i, ip in enumerate(statistics['portPeerList']):
            if ip['ipaddress'] is not None:
                context_list.append(
                    f"来源IP：{ip['ipaddress']}，总连接数为：{ip['counts']}，已建立连接数为：{ip['stat']['established']}，等待连接数为：{ip['stat']['time_wait']}，其他连接数为：{ip['stat']['others']}")
        context_list.append(" ")
    else:
        context_list.append(' %s 端口没有连接，请确保端口正在监听或正在使用中' % port)

    endTime = time.time()
    context_list.append("耗时(s): %s" % (endTime - startTime))

    await context.edit("\n".join(context_list))
