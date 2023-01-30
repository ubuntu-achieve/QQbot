import json
import requests

from alicebot import Plugin
from alicebot.adapter.apscheduler import scheduler_decorator
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment

from .config import config

cfg = config()

########## 动态检测 ##########
@scheduler_decorator(
    trigger="interval", trigger_args={"seconds": 180}, override_rule=True
)
class up_dynamic_reminder(Plugin):
    """
    定时检测主播动态，发现更新则在指定群聊中通知
    """
    priority:int = 0
    block:bool   = False
    async def handle(self) -> None:
        # 爬取信息
        info = requests.get(cfg.dynamic_url, headers=cfg.headers)
        info_js = json.loads(info.content.decode())
        # 读取以前存储的数据
        with open("dynamic_info.json", "r") as f:
            dynamic_info_old = json.load(f)
        # 读取新的动态数据
        dynamic_info, new_txt = {}, None
        for dynamic_index in range(1, len(info_js["data"]["items"])):
            up_name = info_js["data"]["items"][dynamic_index]["modules"]["module_author"]["name"]
            dynamic_time = info_js["data"]["items"][dynamic_index]["modules"]["module_author"]["pub_time"]
            # 跳过直播动态
            if info_js["data"]["items"][dynamic_index]["modules"]["module_dynamic"]["desc"] == None:
                continue
            dynamic_txt  = info_js["data"]["items"][dynamic_index]["modules"]["module_dynamic"]["desc"]["text"]
            if new_txt == None:
                new_txt = dynamic_txt
            dynamic_info[str(dynamic_index)] = [dynamic_time, dynamic_txt]
            # print(f"{up_name}在{dynamic_time}发布的动态\n{dynamic_txt}")
        # 判断是否更新
        if new_txt != dynamic_info_old[next(iter(dynamic_info_old.keys()))][-1]:
            # 如果更新则重新写入本地文件
            with open("dynamic_info.json", "w") as f:
                f.write(json.dumps(dynamic_info))
            # 发出通知
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.text(f"{up_name}在{dynamic_time}发布了动态！\n{new_txt}\n前往链接：{cfg.dynamic_pub_url}")
            await self.bot.get_adapter("cqhttp").send(
                msg,
                message_type="group",
                id_=cfg.group_id
            )
    
    async def rule(self) -> bool:
        return False

class up_dynamic_ask(Plugin):
    """
    有人询问UP主动态时给出反馈
    """
    priority:int = 0
    block:bool   = True  # 停止传播，防止对其他回复模块造成干扰
    # 自定义变量，用于判断是否更新
    update:bool  = False
    async def handle(self) -> None:
        # 读取以前存储的数据
        with open("dynamic_info.json", "r") as f:
            dynamic_info_old = json.load(f)
        
        # 发出通知
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.text(f"动态列表：\n")
        for index, dynamic_index in enumerate(dynamic_info_old.keys()):
            msg += CQHTTPMessageSegment.text(f"\t{index+1}:{dynamic_info_old[dynamic_index][1]}\n\n")
            if "最近" in str(self.event.message) and index == 0:
                break
        msg += CQHTTPMessageSegment.text(f"前往链接：{cfg.dynamic_pub_url}")
        await self.event.reply(msg)
    
    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        if f"[CQ:at,qq={self.bot.config.botuid}]" in str(self.event.raw_message):
            if "动态" in str(self.event.message) and "省流" not in str(self.event.message):
                return True

class up_dynamic_ask_save(Plugin):
    """
    有人询问UP主省流动态时给出反馈
    """
    priority:int = 0
    block:bool   = True  # 停止传播，防止对其他回复模块造成干扰
    # 自定义变量，用于判断是否更新
    update:bool  = False
    async def handle(self) -> None:
        # 读取以前存储的数据
        with open("dynamic_info.json", "r") as f:
            dynamic_info_old = json.load(f)
        
        # 发出通知
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.text(f"前往链接：{cfg.dynamic_pub_url}\n")
        msg += CQHTTPMessageSegment.text(f"动态列表：\n")
        for index, dynamic_index in enumerate(dynamic_info_old.keys()):
            for gus in cfg.gugu:
                if type(gus) == tuple:
                    if gus[0] in dynamic_info_old[dynamic_index][1] and gus[1] in dynamic_info_old[dynamic_index][1]:
                        msg += CQHTTPMessageSegment.text(f"\t{index+1}({dynamic_info_old[dynamic_index][0]}):咕了\n")
                        break
                elif gus in dynamic_info_old[dynamic_index][1]:
                    msg += CQHTTPMessageSegment.text(f"\t{index+1}({dynamic_info_old[dynamic_index][0]}):咕了\n")
                    break
                if gus == cfg.gugu[-1]:
                    msg += CQHTTPMessageSegment.text(f"\t{index+1}({dynamic_info_old[dynamic_index][0]}):自己看！检测不出来\n")
            if "最近" in str(self.event.message) and index == 0:
                break
        await self.event.reply(msg)
    
    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        if f"[CQ:at,qq={self.bot.config.botuid}]" in str(self.event.raw_message):
            if "动态" in str(self.event.message) and "省流" in str(self.event.message):
                with open("event.txt", 'a') as f:
                    f.write("======="+str(self.event.message)+"=======\n")
                return True