import re

from alicebot import Plugin
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment

class msg_reply(Plugin):
    """
    用于完成一些基本的消息回复

    1. @回复
    2. 关键字回复：色图、造反
    3. 糖芙尼表情包
    4. 基本问答回复：你(.*?)我吗、说(.*?)我、帮我(.)(.*?)
    """
    priority:int = 1
    block:bool   = False
    key_img_path = {
        "色图":"file:///data/bot/image/色图.jpg",
        "睡觉":"file:///data/bot/image/睡觉.jpg",
        "问候":"file:///data/bot/image/问候.jpg",
        "造反":"file:///data/bot/image/造反.gif",
    }
    tfn_img_path = {
        "处男":"file:///data/bot/image/face/处男.png",
        "打工":"file:///data/bot/image/face/打工.jpg",
        "得意":"file:///data/bot/image/face/得意.png",
        "害怕":"file:///data/bot/image/face/害怕.png",
        "好耶":"file:///data/bot/image/face/好耶.png",
        "红包":"file:///data/bot/image/face/红包.png",
        "看戏":"file:///data/bot/image/face/看戏.jpg",
        "生气":"file:///data/bot/image/face/生气.jpg",
        "唐门":"file:///data/bot/image/face/唐门.jpg",
        "小丑":"file:///data/bot/image/face/小丑.jpg",
        "蜘蛛":"file:///data/bot/image/face/蜘蛛.gif",
        "gun":"file:///data/bot/image/face/gun.jpg",
    }
    match_exp = ["你(.*?)我吗", "说(.*?)我", "帮我(.)(.*?)"]
    async def handle(self) -> None:
        # msg = CQHTTPMessage()
        with open("event.txt", "a") as f:
            f.write(str(self.event.user_id)+"("+str(self.event.message_type)+")"+":"+str(self.event.raw_message)+"\n")
        # 1. @回复
        if str(self.event.message).replace(" ", "") == "[CQ:at,qq=439183872]":
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.at(self.event.user_id)
            if str(self.event.user_id) == "1852199699":
                msg += CQHTTPMessageSegment.text("有什么需要我帮忙的吗")
                msg += CQHTTPMessageSegment.face(6)
            else:
                msg += CQHTTPMessageSegment.text("没事不要@我，烦内～")
        # 2. 关键字回复
        elif sum([(_keys in str(self.event.message)) for _keys in self.key_img_path.keys()]) == 1:
            msg = CQHTTPMessage()
            for _keys in self.key_img_path.keys():
                if _keys in str(self.event.message):
                    msg += CQHTTPMessageSegment.image(self.key_img_path[_keys])
        # 3. 糖芙尼表情包
        elif "糖芙尼" in str(self.event.message):
            msg = CQHTTPMessage()
            for _keys in self.tfn_img_path.keys():
                if _keys in str(self.event.message):
                    msg += CQHTTPMessageSegment.image(self.tfn_img_path[_keys])
            if len(msg) < 1:
                msg += CQHTTPMessageSegment.image(self.tfn_img_path[""])
        # 4. 基础问答功能
        elif sum([re.match(exp, str(self.event.message)[len("[CQ:at,qq=439183872] "):]) != None for exp in self.match_exp]) == 1:
            event_msg_tmp = str(self.event.message)[len("[CQ:at,qq=439183872] "):]
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.at(self.event.user_id)
            if re.match("你(.*?)我吗", event_msg_tmp) != None:
                msg += CQHTTPMessageSegment.text("我"+re.match("你(.*?)我吗", event_msg_tmp).groups()[0]+"你啊")
            elif re.match("说(.*?)我", event_msg_tmp) != None:
                msg += CQHTTPMessageSegment.text("我"+re.match("说(.*?)我", event_msg_tmp).groups()[0]+"你")
            elif re.match("帮我(.)(.*?)", event_msg_tmp) != None:
                msg += CQHTTPMessageSegment.text("我在"+re.match("帮我(.)(.*?)", event_msg_tmp).groups()[0]+event_msg_tmp[3:])
        else:
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.text("听不懂哦，我只是个bot")
        await self.event.reply(msg)

    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        return "[CQ:at,qq=439183872]" in str(self.event.raw_message)