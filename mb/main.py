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
KEY_FILE = BASE_DIR / "mb.ini"  # 存储key与secret的json文件路径


def load_key_secret():

    try:
        conf = ConfigParser()
        conf.read(KEY_FILE, encoding="utf-8")
        TOP = conf["MB"]["TOP"]

        return TOP
    except:
        return 1024


def set_key_secret(key, value):
    """
    设置环境变量，存储API key
    :return:
    """
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
    """
    >>> bytes2human(10000)
    '9.8 K'
    >>> bytes2human(100001221)
    '95.4 M'
    """
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
        os.system('wget https://raw.githubusercontent.com/chenyk1219/pagermaidPlugins/main/fonts/SimHei.ttf')

    fontManager.addfont('./SimHei.ttf')

    # 中文乱码和坐标轴负号处理。
    matplotlib.rc('font', family='SimHei', weight='bold')
    plt.rcParams['axes.unicode_minus'] = False
    # plt.axis('off')

    # 获取服务器资源使用情况。
    labels = ['CPU', 'MEM', 'DISK', 'NET']

    interval = 0
    args = poll(interval)
    net_top = get_net_top(*args)

    net_numbers = re.findall(r'\d+', net_top)

    net_user = int(net_numbers[0]) if net_numbers else 0
    net_top = load_key_secret()
    net_left = int(net_top) - net_user if net_top else 1024 - net_user

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/')
    disk_usage_percent = disk_usage.percent

    data1 = [cpu_usage * 100, memory_info, disk_usage_percent, net_user]
    data2 = [100 - cpu_usage * 100, 100 - memory_info, 100 - disk_usage_percent, net_left]
    data3 = [data1, data2]
    bottom_x = [0] * len(labels)
    sums = [sum(i) for i in zip(data1, data2)]

    y = range(len(labels))
    # 绘图。
    fig, ax = plt.subplots()
    fig.set_size_inches(5, 3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(False)

    for i in data3:
        y = [a / b for a, b in zip(i, sums)]
        bar = ax.barh(range(len(labels)), y, height=0.5, left=bottom_x,
                      color=[random.random(), random.random(), random.random()])
        bottom_x = [round(a + b, 2) for a, b in zip(bottom_x, y)]
        # 在柱状图上添加数据标签
        # for rect in bar:
        #     w = rect.get_width()
        #     ax.text(w, rect.get_y() + rect.get_height() / 2, '%d' %
        #             w, ha='left', va='center')

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    # plt.xticks(())

    plt.title('服务器资源使用占比', loc='center', fontsize='18',
              fontweight='bold', color='#6699CC')

    plt.savefig('./test.png')
    plt.show()
    # background_image_path = './img.png'
    overlay_image_path = './test.png'

    # background = Image.open(background_image_path)
    overlay = Image.open(overlay_image_path).resize((500, 300))

    background = Image.new('RGB', (500, 400), color='black')

    background.paste(overlay, (0, 0), overlay)
    background.save('./test.png')

    image = Image.open("./test.png")

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
    # image.show()
    image.save("./test.png")

    await bot.send_document(
        context.chat.id,
        "./test.png",
        message_thread_id=context.message_thread_id,
    )
    await final_msg.safe_delete()


@listener(is_plugin=True, outgoing=True, command="mbcf", description="获取服务器信号")
async def mbcf(bot: Client, context: Message):
    value = str(context.parameter[0]).strip('"').strip("'")
    set_key_secret(key='TOP', value=value)
    await context.edit(f"流量信息设置完成: {value} GB")
