import time
import sys
import contextlib
from httpx import get, post

token = str(sys.argv[1])
main = get(
    "https://api.github.com/repos/chenyk1219/pagermaidPlugins/commits/main"
).json()
text = (
    (
        (
            (
                "#更新日志 #pagermaid插件 #"
                + main["commit"]["author"]["name"].replace("_", "")
                + " \n\n🔨 ["
                + main["sha"][:7]
            )
            + "](https://github.com/chenyk1219/pagermaidPlugins/commits/"
        )
        + main["sha"]
    )
    + "): "
) + main["commit"]["message"]

url = f"https://api.telegram.org/bot{token}/sendMessage"
for cid in ["-1002045956568"]:
    push_content = {
        "chat_id": cid,
        "disable_web_page_preview": "True",
        "parse_mode": "markdown",
        "text": text,
    }
    # if cid == "-1001441461877":
    #     push_content["message_thread_id"] = 1027828
    with contextlib.suppress(Exception):
        main_req = post(url, data=push_content)
    time.sleep(1)
print(main["sha"] + " ok！")
