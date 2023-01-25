from alicebot import Plugin
from alicebot.adapter.cqhttp import CQHTTPMessage

class send_test(Plugin):
    '''
    用于测试消息发送功能
    '''
    priority:int = 0
    block:bool   = False
    async def handle(self) -> None:
        a = open("event.txt", "w")
        a.write(str(self.event.user_id))
        a.close()
        # msg = CQHTTPMessage()
        await self.event.reply("success~")
    
    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        return str(self.event.message).lower() == "hello"
