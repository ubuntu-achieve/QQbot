import re
import os
import json

from alicebot import Plugin
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment

class msg_reply(Plugin):
    """
    用于完成一些基本的消息回复

    1. @回复
    2. 关键字回复：色图、造反
    3. 糖芙尼表情包
    4. 基本问答回复：你(.*?)我吗、说(.*?)我、帮我(.)(.*?)
    5. 功能介绍：直播、动态、表情包、关键字、基本问答、智能对话模式
    
    私人功能
    -------
    - 指定消息存储：存储指定人发送的文字、图片等
    """
    priority:int = 1
    block:bool   = False
    key_img_path = {file_name[:-4]:"file:///data/bot/image/key/"+file_name for file_name in sorted(os.listdir("./image/key/"), reverse=True)}
    tfn_img_path = {file_name[:-4]:"file:///data/bot/image/face/"+file_name for file_name in sorted(os.listdir("./image/face/"), reverse=True)}
    match_exp = ["你(.*?)我吗", "说(.*?)我", "帮我(.)(.*?)"]
    async def handle(self) -> None:
        # msg = CQHTTPMessage()
        with open(os.path.join(self.bot.config.tmp_dir, "event.txt"), "a") as f:
            f.write(str(self.event.user_id)+"("+str(self.event.message_type)+")"+":"+str(self.event.raw_message)+"\n")
        # 1. @回复
        if str(self.event.message).replace(" ", "") == f"[CQ:at,qq={self.bot.config.botuid}]":
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
            # 列出表情包列表
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.text(f"共收录{len(self.tfn_img_path.keys())}个表情包（不齐全请联系好耶补充！）\n表情包触发关键字：\n")
            for index, _keys in enumerate(self.tfn_img_path.keys()):
                msg += CQHTTPMessageSegment.text(f"{index+1}. {_keys}\n")
            msg += CQHTTPMessageSegment.text("访问语法：@好耶bot 糖芙尼 +任意包含关键字的语句")
            # 若有提到关键字，则发出表情包，否则发出表情包列表
            for _keys in self.tfn_img_path.keys():
                if _keys in str(self.event.message):
                    msg = CQHTTPMessage()
                    msg += CQHTTPMessageSegment.image(self.tfn_img_path[_keys])
        # 4. 基础问答功能
        elif sum([re.match(exp, str(self.event.message)[len(f"[CQ:at,qq={self.bot.config.botuid}] "):]) != None for exp in self.match_exp]) == 1:
            event_msg_tmp = str(self.event.message)[len(f"[CQ:at,qq={self.bot.config.botuid}] "):]
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.at(self.event.user_id)
            if re.match("你(.*?)我吗", event_msg_tmp) != None:
                msg += CQHTTPMessageSegment.text("我"+re.match("你(.*?)我吗", event_msg_tmp).groups()[0]+"你啊")
            elif re.match("说(.*?)我", event_msg_tmp) != None:
                msg += CQHTTPMessageSegment.text("我"+re.match("说(.*?)我", event_msg_tmp).groups()[0]+"你")
            elif re.match("帮我(.)(.*?)", event_msg_tmp) != None:
                msg += CQHTTPMessageSegment.text("我在"+re.match("帮我(.)(.*?)", event_msg_tmp).groups()[0]+event_msg_tmp[3:])
        # 5. 功能介绍
        elif "功能列表" in str(self.event.message) or "help" in str(self.event.message):
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.text(
                "好耶bot功能列表：\n\
 1. 直播状态检测：通过发送“@好耶bot+直播”或“@好耶bot+啵”获取直播状态(stable)；\n\
 2. 动态内容获取：通过发送“@好耶bot+动态”获取全部动态、发送“@好耶bot+最近+动态”获取最近一条动态(stable)；\n\
 3. 省流功能：在动态内容获取语法的任意位置添加省流，即可触发功能，例如：“@好耶bot 最近动态省流”(preview)；\n\
 4. 糖芙尼表情包：通过发送“@好耶bot 糖芙尼”了解使用方法(stable)；\n\
 5. 查看周表：通过发送“@好耶bot 周表”获取周表和当日内容，\n\
 6. 基本问答功能：通过“@好耶bot+任意内容”触发，目前仅实现少量问答模板(preview)；\n\
 7. 关键字回答：通过“@好耶bot+任意包含关键字的内容”，目前关键字有“色图”、“睡觉”、“问候”、“造反”(preview)\n\
 8. 智能对话模式：通过“Q:+欲询问内容”开启，输入“!q”结束智能对话模式\n\
（注：该列表通过发送“@好耶bot 功能列表”或“@好耶bot help”获取，对于2、3、5号功能，可以通过添加“更新”词条获取最新内容）"
                )
        elif "强制解除" in str(self.event.message):
            with open(os.path.join(self.bot.config.tmp_dir, "user.json"), "r") as f:
                user_info_old = json.load(f)
            msg = CQHTTPMessage()
            # 解除权限判断
            if str(self.event.user_id) == str(self.bot.config.owner):
                # 有权限
                # 强制解除
                self.bot.config.ask_state = "False"
                # 计算该用户花费
                if float(user_info_old["len"])*6e-5 > 0.5:
                    msg += CQHTTPMessageSegment.text("“智能对话”已结束，你花费了好耶")
                    msg += CQHTTPMessageSegment.text(str(int(user_info_old["len"])*6e-5)+"美元")
                    msg += CQHTTPMessageSegment.face(5)
                    msg += CQHTTPMessageSegment.text("你个大坏蛋！")
                else:
                    msg += CQHTTPMessageSegment.text("bot共回答了你"+str(user_info_old["len"])+"字节")
                msg += CQHTTPMessageSegment.at(int(user_info_old["id"]))
            else:
                # 无权限
                msg += CQHTTPMessageSegment.text("抱歉，你好像没有权限哦～")
            msg += CQHTTPMessageSegment.at(int(self.event.user_id))
        else:
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.text("听不懂哦，我只是个bot")
        await self.event.reply(msg)

    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        return f"[CQ:at,qq={self.bot.config.botuid}]" in str(self.event.raw_message)