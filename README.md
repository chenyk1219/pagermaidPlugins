# PagerMaid-Pyro 的野生插件仓库


PagerMaid-Pyro 的地址：[PagerMaid-Pyro](https://github.com/TeamPGM/PagerMaid-Pyro)

## 插件列表

- signal

    - 更改信号插件，用于更改接收信号的关键字
    - 用法：`,signal "xxx|xxx|xxx"`
    - 说明：新的信号要用<font color="red">引号包起来</font>并且<font color="red">至少是2个</font>，因为是全文替换，所以如果是单个信号，比如`,`可能会导致文件的其他地方也被替换，导致程序无法正常运行，如果不慎真的替换了，不要慌张，进入
      `/var/lib/pagermaid/pagermaid/`目录，删了`listener.py`文件，重新下载[https://github.com/TeamPGM/PagerMaid-Pyro/blob/master/pagermaid/listener.py](https://github.com/TeamPGM/PagerMaid-Pyro/blob/master/pagermaid/listener.py)，重新启动程序即可。