from time import strftime, localtime

from alicebot import Plugin
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment
from alicebot.adapter.cqhttp import CQHTTPAdapter

class send_group_msg(Plugin):
    '''
    在指定群聊中发送消息
    '''
    priority:int = 0
    block:bool   = False
    async def handle(self) -> None:
        await self.bot.get_adapter("cqhttp").send(
            f"Time: {strftime('%Y-%m-%d %H:%M:%S', localtime())}",
            message_type="group",
            id_=707938614,  # 群号
        )
        # msg_obj.send("test","private",)
        pass

    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        return True

class send_group_msg(Plugin):
    '''
    向指定的人发送消息
    '''
    priority:int = 0
    block:bool   = False
    async def handle(self) -> None:
        await self.bot.get_adapter("cqhttp").send(
            f"Time: {strftime('%Y-%m-%d %H:%M:%S', localtime())}",
            message_type="private",
            id_=1852199699,  # QQ号
        )
        pass

    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        return True