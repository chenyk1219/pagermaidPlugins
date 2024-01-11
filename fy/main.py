import hashlib
import os
import time
import uuid
from configparser import ConfigParser
from json import loads as json_loads

from pagermaid.listener import listener
from pagermaid.utils import Message
from pyrogram import Client

try:
    import requests
except:
    from pagermaid.utils import pip_install

    pip_install("requests")
finally:
    import requests

YOUDAO_URL = "https://openapi.youdao.com/api"
BASE_DIR = Path(__file__).resolve().parent
KEY_FILE = BASE_DIR / "KeySecret.ini"  # 存储key与secret的json文件路径
MAX_LENGTH = 1500  # 限制翻译输入的最大长度


def load_key_secret() -> tuple[str, str]:
    """
    读取json文件中保存的API key

    :return:(key, secret)
    """
    conf = ConfigParser()
    conf.read(KEY_FILE, encoding="utf-8")
    APP_KEY = conf["YouDao"]["APP_KEY"]
    APP_SECRET = conf["YouDao"]["APP_SECRET"]

    return APP_KEY, APP_SECRET


def set_key_secret(key, value):
    """
    设置环境变量，存储API key
    :return:
    """
    conf = ConfigParser()
    if not os.path.exists(KEY_FILE):
        os.system(r"touch {}".format(KEY_FILE))
        if "YouDao" in conf.sections():
            conf.set("YouDao", option=key, value=value)
            conf.write(open(KEY_FILE, "a", encoding="utf-8"))
        else:
            conf.add_section("YouDao")
            conf.set("YouDao", option=key, value=value)
            conf.write(open(KEY_FILE, "w", encoding="utf-8"))
    else:
        conf.read(KEY_FILE, encoding="utf-8")
        if "YouDao" in conf.sections():
            conf.set("YouDao", option=key, value=value)
            conf.write(open(KEY_FILE, "r+", encoding="utf-8"))
        else:
            conf.add_section("YouDao")
            conf.set("YouDao", option=key, value=value)
            conf.write(open(KEY_FILE, "r+", encoding="utf-8"))


class YouDaoTranslator:
    """
    调用有道翻译API实现机器翻译
    """

    def __init__(self):
        self.q = ""  # 待翻译内容
        self._request_data = {}
        self._APP_KEY, self._APP_SECRET = load_key_secret()

    def _gen_sign(self, current_time: str, salt: str) -> str:
        """
        生成签名

        :param current_time: 当前UTC时间戳(秒)
        :param salt: UUID
        :return: sign
        """
        q = self.q
        q_size = len(q)
        if q_size <= 20:
            sign_input = q
        else:
            sign_input = q[0:10] + str(q_size) + q[-10:]
        sign_str = self._APP_KEY + sign_input + salt + current_time + self._APP_SECRET
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(sign_str.encode("utf-8"))
        return hash_algorithm.hexdigest()

    def _package_data(self, current_time: str, salt: str) -> None:
        """
        设置接口调用参数

        :param current_time: 当前UTC时间戳(秒)
        :param salt: UUID
        :return: None
        """
        request_data = self._request_data

        request_data["q"] = self.q  # 待翻译内容
        request_data["appKey"] = self._APP_KEY
        request_data["salt"] = salt
        request_data["sign"] = self._gen_sign(current_time, salt)
        request_data["signType"] = "v3"
        request_data["curtime"] = current_time
        # _request_data["ext"] = "mp3"  # 翻译结果音频格式
        # _request_data["voice"] = "0"  # 翻译结果发音选择，0为女声，1为男声
        request_data["strict"] = "true"  # 是否严格按照指定from和to进行翻译
        # _request_data["vocabId"] = "out_Id"  # 用户上传的词典，详见文档

    def _set_trs_mode(self, mode: str) -> None:
        """
        设置翻译语言模式

        :param mode: 语言模式，en2zh或zh2en
        :return: None
        """
        try:
            if mode == "en2zh":
                self._request_data["from"] = "en"
                self._request_data["to"] = "zh-CHS"
            elif mode == "zh2en":
                self._request_data["from"] = "zh-CHS"
                self._request_data["to"] = "en"
            elif mode == "auto2zh":
                self._request_data["from"] = "auto"
                self._request_data["to"] = "zh-CHS"
            else:
                self._request_data["from"] = mode.split('2')[0]
                self._request_data["to"] = mode.split('2')[1]
        except:
            self._request_data["from"] = "auto"
            self._request_data["to"] = "auto"

    def _do_request(self) -> requests.Response:
        """
        发送请求并获取Response

        :return: Response
        """
        current_time = str(int(time.time()))
        salt = str(uuid.uuid1())
        self._package_data(current_time, salt)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return requests.post(YOUDAO_URL, data=self._request_data, headers=headers)

    def translate(self, q: str, mode: str) -> str:
        """
        翻译

        :param q: 待翻译文本
        :param mode: 翻译语言模式，en2zh或zh2en
        :return: 翻译结果
        """
        if not q:
            return "q is empty!"
        if len(q) > MAX_LENGTH:
            return "q is too long!"

        self.q = q
        self._set_trs_mode(mode)
        response = self._do_request()
        content_type = response.headers["Content-Type"]

        if content_type == "audio/mp3":
            # 返回mp3格式的音频结果
            millis = int(round(time.time() * 1000))
            file_path = "合成的音频存储路径" + str(millis) + ".mp3"
            with open(file_path, "wb") as fo:
                fo.write(response.content)
            trans_result = file_path
        else:
            # 返回json格式的文本结果
            error_code = json_loads(response.content)["errorCode"]  # 有道API的错误码
            if error_code == "0":
                trans_result = json_loads(response.content)["translation"]
            else:
                trans_result = f"ErrorCode {error_code}, check YouDao's API doc plz."
        return trans_result


@listener(is_plugin=True, outgoing=True, command="fy",
          description="翻译指定内容，默认翻译为中文，目前只支持有道，官方申请key指导文档：https://ai.youdao.com/doc.s#guide，"
                      "bob指导文档：https://bobtranslate.com/service/translate/youdao.html"
                      "\n\n说明：使用前需要设置有道的API的ak和sk，ak和sk用引号包起来，防止特殊符合发生转译"
                      "\n\n1. 设置ak：,fyak 'app_key'\n\n2. 设置sk：,fysk 'app_secret'"
                      "\n\n使用：,fy [mode]，mode: 可选参数翻译语言模式，en2zh或zh2en，默认为：auto2zh，其他的要用2隔开，比如en2de"
                      "\n\n使用场景：回复别人发的纯文本内容，输入 ,fy"
                      "\n\n检查ak和sk设置是否正确（明文，建议私发）：,fyck"
                      "\n\n去与外国友人对线吧!!!"
                      "\n\n作者：@inextopschannel"
                      "\n\n仓库：https://github.com/chenyk1219/pagermaidPlugins"
          )
async def translate(bot: Client, context: Message):
    try:
        q = context.reply_to_message.text
        mode = str(context.parameter)
        if not mode:
            mode = 'auto2zh'
        translator = YouDaoTranslator()
        trans_result = translator.translate(q, mode=mode)
        await context.edit(trans_result)
    except:
        await context.edit("翻译异常，请阅读使用指导：,help fy，配置前置工作")


@listener(is_plugin=True, outgoing=True, command="fyak",
          description="设置翻译的API AK")
async def setdefaultak(bot: Client, context: Message):
    value = str(context.parameter[0]).strip('"').strip("'")
    set_key_secret(key='APP_KEY', value=value)
    await context.edit("有道翻译密钥设置成功")


@listener(is_plugin=True, outgoing=True, command="fysk",
          description="设置翻译的API SK")
async def setdefaultsk(bot: Client, context: Message):
    value = str(context.parameter[0]).strip('"').strip("'")
    set_key_secret(key='APP_SECRET', value=value)
    await context.edit("有道翻译密钥设置成功")


@listener(is_plugin=True, outgoing=True, command="fyck",
          description="检查翻译的API key")
async def setdefaultcheck(bot: Client, context: Message):
    ak, sk = load_key_secret()
    await context.edit(f"有道翻译AK：{ak}\n有道翻译SK：{sk}")
