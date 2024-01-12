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

from io import BytesIO

from PIL import Image
from math import floor

from pagermaid.listener import listener
from pagermaid.enums import Message, Client

try:
    import easyocr
except:
    from pagermaid.utils import pip_install

    pip_install("easyocr")
finally:
    import easyocr


async def resize_image(photo):
    image = Image.open(photo)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = floor(size1new)
        size2new = floor(size2new)
        size_new = (size1new, size2new)
        image = image.resize(size_new)
    else:
        maxsize = (512, 512)
        image.thumbnail(maxsize)

    return image


@listener(is_plugin=True, alias_command="ocr",
          description="简单的图片OCR，重要的事情说三遍"
                      "\n‼️此脚本依赖了第三方库easyocr，这个库对cpu、gpu都有硬性要求。不是所有的服务器都能安装，建议先进服务器安装成功easyocr后再安装此脚本"
                      "\n‼️此脚本依赖了第三方库easyocr，这个库对cpu、gpu都有硬性要求。不是所有的服务器都能安装，建议先进服务器安装成功easyocr后再安装此脚本"
                      "\n‼️此脚本依赖了第三方库easyocr，这个库对cpu、gpu都有硬性要求。不是所有的服务器都能安装，建议先进服务器安装成功easyocr后再安装此脚本"
                      "\n安装方法：,install ocr"
                      "\n使用方法：,ocr"
                      "\n\n作者：@inextopschannel"
                      "\n\n仓库：https://github.com/chenyk1219/pagermaidPlugins"
          )
async def ocr(bot: Client, context: Message):
    reply = context.reply_to_message
    photo = None
    if reply and reply.photo:
        photo = reply
    elif context.photo:
        photo = context
    if not photo:
        return await context.edit("请回复一张图片")
    try:
        photo = await bot.download_media(photo)
        message: Message = await context.edit("正在OCR识别中...\n███████70%")
        image = await resize_image(photo)
        file = BytesIO()
        file.name = "sticker.png"
        image.save(file, "png")
        file.seek(0)
        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        result = reader.readtext(image=file, detail=0)
        await context.edit(" ".join(result))
        return await context.edit("识别完毕")
    except Exception as e:
        return await context.edit(f"识别失败：{e}")
    await context.safe_delete()
