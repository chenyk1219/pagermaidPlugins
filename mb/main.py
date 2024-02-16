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
import random
import os
import time
import re
import pathlib
from configparser import ConfigParser
import datetime

try:
    import psutil
except:
    from pagermaid.utils import pip_install

    pip_install("psutil")
finally:
    import psutil

try:
    import matplotlib
except:
    from pagermaid.utils import pip_install

    pip_install("matplotlib")
finally:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import fontManager

try:
    from PIL import Image, ImageDraw, ImageFont
except:
    from pagermaid.utils import pip_install

    pip_install("Pillow")
finally:
    from PIL import Image, ImageDraw, ImageFont

try:
    import requests
except:
    from pagermaid.utils import pip_install

    pip_install("requests")
finally:
    import requests

BASE_DIR = pathlib.Path(__file__).resolve().parent
KEY_FILE = BASE_DIR / "mb.ini"


def load_key_secret():
    try:
        conf = ConfigParser()
        conf.read(KEY_FILE, encoding="utf-8")
        TOP = conf["MB"]["TOP"]

        return TOP
    except:
        return 1024


def set_key_secret(key, value):
    conf = ConfigParser()
    if not os.path.exists(KEY_FILE):
        os.system(r"touch {}".format(KEY_FILE))
        if "MB" in conf.sections():
            conf.set("MB", option=key, value=value)
            conf.write(open(KEY_FILE, "a", encoding="utf-8"))
        else:
            conf.add_section("MB")
            conf.set("MB", option=key, value=value)
            conf.write(open(KEY_FILE, "w", encoding="utf-8"))
    else:
        conf.read(KEY_FILE, encoding="utf-8")
        if "MB" in conf.sections():
            conf.set("MB", option=key, value=value)
            conf.write(open(KEY_FILE, "r+", encoding="utf-8"))
        else:
            conf.add_section("MB")
            conf.set("MB", option=key, value=value)
            conf.write(open(KEY_FILE, "r+", encoding="utf-8"))


def get_isp_info():
    url = 'http://208.95.112.1/json'
    response = requests.get(url)
    data = response.json()
    return data


def bytes2human(n):
    symbols = ('K', 'M', 'G')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)


def poll(interval):
    tot_before = psutil.net_io_counters()
    pnic_before = psutil.net_io_counters(pernic=True)
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)
    return (tot_before, tot_after, pnic_before, pnic_after)


def get_net_top(tot_before, tot_after, pnic_before, pnic_after):
    # totals
    top = bytes2human(tot_after.bytes_sent + tot_after.bytes_recv)
    return top


@listener(is_plugin=True, outgoing=True, command="mb",
          description="服务器面板\n"
                      "使用方法：,mb\n"
                      "使用需要先设置流量信息：,mbcf 500 (单位GB)\n"
                      "每月流量到期日需要手动重置一下网卡流量：sudo ifdown eth0 && sudo ifup eth0\n"
                      "作者：@chenyk1219\n"
                      "仓库：https://github.com/chenyk1219/pagermaidPlugins"
          )
async def mb(bot: Client, context: Message):
    final_msg = await context.edit("正在获取服务器资源使用情况...")
    if not os.path.isfile('./SimHei.ttf'):
        # await context.edit("正在下载微软雅黑字体依赖...")
        os.system('wget https://raw.githubusercontent.com/chenyk1219/pagermaidPlugins/main/fonts/SimHei.ttf')

    fontManager.addfont('./SimHei.ttf')
    # final_msg = await context.edit("正在检查脚本依赖情况...")

    matplotlib.rc('font', family='SimHei', weight='bold')
    plt.rcParams['axes.unicode_minus'] = False

    labels = ['CPU', 'MEM', 'DISK', 'NET']

    interval = 0
    args = poll(interval)
    net_top = get_net_top(*args)

    net_numbers = re.findall(r'\d+', net_top)

    net_user = int(net_numbers[0]) if net_numbers else 0
    net_top = load_key_secret()
    net_left = int(net_top) - net_user if net_top else 1024 - net_user

    # 获取所有网卡的流量信息
    net_io = psutil.net_io_counters(pernic=True)

    # 初始化总流量统计变量
    total_bytes_sent = 0
    total_bytes_recv = 0

    # 遍历所有网卡，累加发送和接收的字节数
    for nic, counters in net_io.items():
        total_bytes_sent += counters.bytes_sent
        total_bytes_recv += counters.bytes_recv

    total_bytes_sent = bytes2human(total_bytes_sent)
    total_bytes_recv = bytes2human(total_bytes_recv)

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory().percent
    memory_total = bytes2human(psutil.virtual_memory().total)
    memory_used = bytes2human(psutil.virtual_memory().used)
    disk_usage = psutil.disk_usage('/')
    disk_total = bytes2human(disk_usage.total)
    disk_used = bytes2human(disk_usage.used)
    disk_usage_percent = disk_usage.percent
    run_time = datetime.datetime.now().timestamp() - psutil.boot_time()
    run_day = int(run_time / 86400)
    run_hour = int(run_time % 86400 / 3600)
    run_minute = int(run_time % 86400 % 3600 / 60)

    cpu_cores_physical = psutil.cpu_count(logical=False) or '无法获取（可能是因为当前环境的限制）'
    cpu_cores_logical = psutil.cpu_count(logical=True)
    cpu_freq = round(psutil.cpu_freq().current, 2)

    data1 = [cpu_usage * 100, memory_info, disk_usage_percent, net_user]
    data2 = [100 - cpu_usage * 100, 100 - memory_info, 100 - disk_usage_percent, net_left]
    data3 = [data1, data2]
    bottom_x = [0] * len(labels)
    sums = [sum(i) for i in zip(data1, data2)]

    fig, ax = plt.subplots()
    fig.set_size_inches(5, 3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(False)

    for i in data3:
        y = [a / b for a, b in zip(i, sums)]
        ax.barh(range(len(labels)), y, height=0.5, left=bottom_x,
                color=[random.random(), random.random(), random.random()])
        bottom_x = [round(a + b, 2) for a, b in zip(bottom_x, y)]

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    plt.title('服务器资源使用占比', loc='center', fontsize='18',
              fontweight='bold', color='#6699CC')

    plt.savefig('./vps.png')
    plt.show()
    overlay_image_path = './vps.png'

    overlay = Image.open(overlay_image_path).resize((500, 300))

    background = Image.new('RGB', (500, 400), color='black')

    background.paste(overlay, (0, 0), overlay)
    background.save('./vps.png')

    image = Image.open("./vps.png")

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype("./SimHei.ttf", size=18)

    isp_info = get_isp_info()

    text5_position = (25, 325)
    text5_content = f"IP: {isp_info.get('query').split('.')[0] + '.*.*.' + isp_info.get('query').split('.')[-1]}"

    text1_position = (300, 325)
    text1_content = f"ISP: {isp_info.get('isp')}"

    text2_position = (25, 350)
    text2_content = f"Country: {isp_info.get('country')}"

    text4_position = (300, 350)
    text4_content = f"City: {isp_info.get('city')}"

    text3_position = (25, 375)
    text3_content = f"Region: {isp_info.get('regionName')}"

    text_color = (255, 255, 255)

    draw.text(text5_position, text5_content, fill=text_color, font=font)
    draw.text(text1_position, text1_content, fill=text_color, font=font)
    draw.text(text2_position, text2_content, fill=text_color, font=font)
    draw.text(text3_position, text3_content, fill=text_color, font=font)
    draw.text(text4_position, text4_content, fill=text_color, font=font)
    image.save("./vps.png")

    caption = (f'系统运行时间：{run_day}天{run_hour}小时{run_minute}分钟\n'
               f'内存信息：{memory_used}/{memory_total}\n'
               f'硬盘信息：{disk_used}/{disk_total}\n'
               f'网络流量：总发送：{total_bytes_sent}，总接收：{total_bytes_recv}\n'
               f'CPU信息：{cpu_cores_physical}核心物理CPU，{cpu_cores_logical}核心逻辑CPU，当前频率约为{cpu_freq}MHz，使用率：{cpu_usage * 100}%\n')

    await context.reply_photo('./vps.png', caption=caption, quote=False,
                              reply_to_message_id=context.reply_to_top_message_id)

    await final_msg.safe_delete()


@listener(is_plugin=True, outgoing=True, command="mbcf", description="设置网络流量")
async def mbcf(bot: Client, context: Message):
    value = str(context.parameter[0]).strip('"').strip("'")
    set_key_secret(key='TOP', value=value)
    await context.edit(f"流量信息设置完成: {value} GB")
