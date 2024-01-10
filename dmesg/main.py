from pyrogram import Client
from pagermaid.listener import listener
from pagermaid.utils import Message
import subprocess
import time
import sys

try:
    import psutil
except:
    from pagermaid.utils import pip_install

    pip_install("psutil")
finally:
    import psutil


@listener(is_plugin=True, outgoing=True, command="dmesg",
          description="查看服务器的系统运行日志"
                      "\n安装方法：,install dmesg"
                      "\n使用方法：,dmesg"
                      "\n注意：此命令只在Linux系统下有效"
                      "\n启动日志过多，会以文件的形式下载查看"
                      "\n建议私发。除非你需要别人帮你处理服务器问题，可以提供给别人"
                      "\n\n作者：@inextopschannel"
                      "\n\n仓库：https://github.com/chenyk1219/pagermaidPlugins"
          )
async def get_human_readable_dmesg(bot: Client, context: Message):
    context_list = []
    dmesg = subprocess.Popen('dmesg', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').split('\n')
    for line in dmesg:
        try:
            s = time.strftime('%Y-%m-%d %H:%M:%S',
                              time.localtime(
                                  (float(psutil.boot_time()) + float(line.split('] ')[0][2:].strip())))), line
            context_list.append(str(s))
            sys.stdout.flush()
        except ValueError:
            print(line)
    await context.edit("\n".join(context_list))
