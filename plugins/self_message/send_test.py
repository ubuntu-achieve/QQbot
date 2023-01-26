from alicebot import Plugin
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment

class send_test(Plugin):
    '''
    用于测试消息发送功能，当发出hello时自动回复success~(包括私聊和群聊)
    event包含属性：
    - message_type(消息类型):private, group
    - sub_type(表示消息类型的子类型):group, public
    - message_id(消息ID):int32
    - user_id(发送者QQ号):int64
    - message(一个消息链):message
    - raw_message(CQ码格式的消息，表情、表情包、图片等):string
    - font(字体):int
    - sender(发送者信息):object
    '''
    priority:int = 0
    block:bool   = False
    async def handle(self) -> None:
        # msg = CQHTTPMessage()
        with open("event.txt", "a") as f:
            f.write(str(self.event.user_id)+"("+str(self.event.message_type)+")"+":"+str(self.event.message)+"\n")
        await self.event.reply("success~")

    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        return str(self.event.message).lower() == "hello"

class send_at_test(Plugin):
    '''
    在被@之后自动回复
    '''
    priority:int = 0
    block:bool   = False
    async def handle(self) -> None:
        # msg = CQHTTPMessage()
        with open("event.txt", "a") as f:
            f.write(str(self.event.user_id)+"("+str(self.event.message_type)+")"+":"+str(self.event.raw_message)+"\n")
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.at(self.event.user_id)
        msg += CQHTTPMessageSegment.text("没事不要@我，烦内～")
        await self.event.reply(msg)

    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        return "[CQ:at,qq=439183872]" == str(self.event.raw_message).replace(" ", "")