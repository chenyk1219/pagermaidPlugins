# PagerMaid-Pyro 的野生插件仓库


PagerMaid-Pyro 的地址：[PagerMaid-Pyro](https://github.com/TeamPGM/PagerMaid-Pyro)

⚠ **请注意，不同版本的插件不通用。**  

⚠ **PagerMaid-Modify 版插件请前往 [PagerMaid_Plugins](https://github.com/TeamPGM/PagerMaid_Plugins/tree/master)**。

## 使用方法

```shell
,apt_source add https://raw.githubusercontent.com/chenyk1219/pagermaidPlugins/main
```

## 插件列表

- signal

    - 更改信号插件，用于更改接收信号的关键字
    - 安装 `,apt install signal`
    - 用法：`,signal "xxx|xxx"`
    - 说明：新的信号要用`引号包起来`并且`至少是2个`，因为是全文替换，所以如果是单个信号，比如`,`可能会导致文件的其他地方也被替换，导致程序无法正常运行，如果不慎真的替换了，不要慌张，进入
      `/var/lib/pagermaid/pagermaid/`目录，删了`listener.py`文件，重新下载[https://github.com/TeamPGM/PagerMaid-Pyro/blob/master/pagermaid/listener.py](https://github.com/TeamPGM/PagerMaid-Pyro/blob/master/pagermaid/listener.py)，重新启动程序即可。

- ports
    - 端口扫描插件，用于扫描端口是否被连接
    - 安装 `,apt install ports`
    - 用法：`,ports xxx`
    - 说明：xxx为端口号，目前只支持单个端口号，比如`,ports 8080`