from time import strftime, localtime

from alicebot import Plugin
from alicebot.adapter.apscheduler import scheduler_decorator
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment

@scheduler_decorator(
    trigger="interval", trigger_args={"seconds": 10}, override_rule=True
)
class Schedule(Plugin):
    '''
    设置定时任务，每10秒发送一次时间
    '''
    priority:int = 0
    block:bool   = False

    async def handle(self) -> None:
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.text(f"Time: {strftime('%Y-%m-%d %H:%M:%S', localtime())}")
        msg += CQHTTPMessageSegment.image("./data/test.jpg")
        await self.bot.get_adapter("cqhttp").send(
            msg,
            message_type="private",
            id_=1852199699,  # 群号
        )

    async def rule(self) -> bool:
        return False
