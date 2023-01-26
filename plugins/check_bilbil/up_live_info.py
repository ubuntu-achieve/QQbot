import json
import requests
from time import strftime, localtime

from alicebot import Plugin
from alicebot.adapter.apscheduler import scheduler_decorator
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment

from .config import config

cfg = config()

########## 直播检测 ##########
@scheduler_decorator(
    trigger="interval", trigger_args={"seconds": 30}, override_rule=True
)
class up_live_reminder(Plugin):
    '''
    定时检测主播开播情况，若检测到开播则发送提示信息
    '''
    priority:int  = 0
    block:bool    = False
    async def handle(self) -> None:
        # 爬取信息
        info = requests.get(cfg.live_status_url, headers=cfg.headers)
        info_js = json.loads(info.content.decode())
        with open("tmp.json", "w") as f:
            f.write(info.content.decode())
        # 主播名称
        live_name   = info_js["data"]["name"]
        # 开播状态
        live_status = info_js["data"]["live_room"]["liveStatus"]
        #直播标题
        live_title  = info_js["data"]["live_room"]["title"]
        #直播链接
        live_url    = info_js["data"]["live_room"]["url"]
        if str(live_status) == "0":  # 若未开播则不做任何操作，并将reminded设置为未提醒过
            if self.bot.config.reminded == "True": # 若未开播但是提醒过了，说明已经下播了
                msg = CQHTTPMessage()
                msg += CQHTTPMessageSegment.text(f"\t{live_name}  下啵啦！")
                await self.bot.get_adapter("cqhttp").send(
                    msg,
                    # todo
                    message_type="group",
                    id_=cfg.group_id
                )
            self.bot.config.reminded = "False"
        elif self.bot.config.reminded == "False":  # 如果开播了，且没有提醒过，则做出提醒
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.text(f"\t{live_name}  开啵啦！\n\t{live_title}\n前往链接：{live_url}")

            await self.bot.get_adapter("cqhttp").send(
                msg,
                # todo
                message_type="group",
                id_=cfg.group_id
            )
            self.bot.config.reminded = "True"
        
    async def rule(self) -> bool:
        return False
    
class up_live_ask(Plugin):
    """
    当检测到有人询问直播情况时，进行反馈
    """
    priority:int = 0
    block:bool   = False
    async def handle(self) -> None:
        # 爬取信息
        info = requests.get(cfg.live_status_url, headers=cfg.headers)
        info_js = json.loads(info.content.decode())
        # 主播名称
        live_name   = info_js["data"]["name"]
        # 开播状态
        live_status = info_js["data"]["live_room"]["liveStatus"]
        #直播标题
        live_title  = info_js["data"]["live_room"]["title"]
        #直播链接
        live_url    = info_js["data"]["live_room"]["url"]
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.at(self.event.user_id)
        if str(live_status) == "0":  # 若未开播则退出程序
            msg += CQHTTPMessageSegment.text(f"还没有开播哦(上次检测时间：{strftime('%Y-%m-%d %H:%M:%S', localtime())})")
        else:
            msg += CQHTTPMessageSegment.text(f"\t{live_name}  开啵啦！\n\t{live_title}\n前往链接：{live_url}")
        await self.event.reply(msg)
    
    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        if "[CQ:at,qq=439183872]" in str(self.event.raw_message):
            if "直播" in str(self.event.message) or "啵" in str(self.event.message):
                with open("event.txt", 'a') as f:
                    f.write("======="+str(self.event.message)+"=======\n")
                return True

