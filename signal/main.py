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


@listener(is_plugin=True, outgoing=True, command=alias_command("signal"), description="替换触发器\n,使用方法：signal 'xxx|xxx'\n新的信号要用引号包起来并且至少是2个，因为是全文替换，所以如果是单个信号，比如,可能会导致文件的其他地方也被替换，导致程序无法正常运行\n如果不慎真的替换了，不要慌张，进入 /var/lib/pagermaid/pagermaid/目录，删了listener.py文件，重新下载https://github.com/TeamPGM/PagerMaid-Pyro/blob/master/pagermaid/listener.py，重新启动程序即可")
async def ci(bot: Client, context: Message):
    context_list = []
    old_trigger = subprocess.Popen(
        "grep -rn  -w 'pattern = rf' /var/lib/pagermaid/pagermaid | grep listener.py | awk -F':' '{print $3}'",
        shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').strip().split('(')[1].split(')')[0]
    context_list.append(f"旧的触发器为：{old_trigger}")
    new_trigger = str(context.parameter[0]).strip('"').strip("'")
    if new_trigger.find('|') >= 0 and len(new_trigger.split('|')) >= 2:
        context_list.append(f"新的触发器为：{new_trigger}")
        shell_str = f"sed -i 's#{old_trigger}#{new_trigger}#g' /var/lib/pagermaid/pagermaid/listener.py"
        subprocess.Popen(str(shell_str), shell=True).wait()
        context_list.append(f"触发器替换完毕，记得使用旧的触发器 {old_trigger} 重启一下服务")
    else:
        context_list.append("参数格式不正确，要用|隔开，比如 ,|，|.")
    await context.edit("\n".join(context_list))
