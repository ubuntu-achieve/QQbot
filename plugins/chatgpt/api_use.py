import json
import requests

from alicebot import Plugin
from alicebot.adapter.apscheduler import scheduler_decorator
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment
from .config import config

cfg = config()

class chatGPT_api_use(Plugin):
    '''
    调用ChatGPT的api实现智能交流
    '''
    priority:int = 0
    block:bool   = True  # 阻断事件向下传播
    async def handle(self) -> None:
        user_info = {}
        with open("user.json", "r") as f:
            user_info_old = json.load(f)
        msg = CQHTTPMessage()
        # 判断接口是否被人占用
        if self.bot.config.ask_state == "False":
            if str(self.event.message)[:2] == "!q":
                # 如果在未占用的时候输入退出命令
                msg += CQHTTPMessageSegment.text(cfg.error)
            else:
                # 若未被占用
                self.bot.config.ask_state = "True"
                user_info["id"] = str(self.event.user_id)
                user_info["len"] = str(0)
                # 写入使用用户信息
                with open("user.json", "w") as f:
                    f.write(json.dumps(user_info))
                msg += CQHTTPMessageSegment.text(cfg.prompt_b)
                # 是占用者访问
                # 写入调用api部分
                if str(self.event.message)[2:] == "":
                    # 判断是否为空
                    msg += CQHTTPMessageSegment.text(cfg.error)
                else:
                    await self.event.reply("收到！正在处理...")
                    data = {
                        "prompt":str(self.event.message)[2:],
                        "model" :"text-davinci-003",
                        'max_tokens' :2000,  # 限制回答的长度
                        'temperature':1,
                    }
                    #发送HTTP POST请求
                    response = requests.post(cfg.api_url, json=data, headers=cfg.headers)
                    #解析响应
                    resp = response.json()
                    # 统计回复的字数
                    user_info["len"] = str(int(user_info["len"]) + len(str(resp["choices"][0]["text"].strip())))
                    # 写入文件
                    with open("user.json", "w") as f:
                        f.write(json.dumps(user_info))
                    msg += CQHTTPMessageSegment.text(cfg.prompt_m)
                    msg += CQHTTPMessageSegment.text("A:"+str(resp["choices"][0]["text"].strip()))
        elif self.bot.config.ask_state == "True":
            # 若被人占用
            # 如果要求退出
            if str(self.event.message)[:2] == "!q":
                if user_info_old["id"] == str(self.event.user_id):
                    # 是占用者访问
                    self.bot.config.ask_state = "False"  # 解除占用
                    # 计算该用户花费
                    if int(user_info_old["len"])*6e-5 > 0.5:
                        msg += CQHTTPMessageSegment.text(cfg.prompt_e)
                        msg += CQHTTPMessageSegment.text(str(int(user_info_old["len"])*6e-5)+"美元")
                        msg += CQHTTPMessageSegment.face(5)
                        msg += CQHTTPMessageSegment.text("你个大坏蛋！")
                    else:
                        msg += CQHTTPMessageSegment.text("“智能对话”已结束，bot共回答了你"+str(user_info_old["len"])+"字节")
                    msg += CQHTTPMessageSegment.at(int(self.event.user_id))
                else:
                    # 非占用者访问
                    msg += CQHTTPMessageSegment.text(cfg.prompt_w)
                    msg += CQHTTPMessageSegment.at(int(user_info_old["id"]))
            else:
                if user_info_old["id"] == str(self.event.user_id):
                    # 是占用者访问
                    # 写入调用api部分
                    if str(self.event.message)[2:] == "":
                        # 判断是否为空
                        msg += CQHTTPMessageSegment.text(cfg.error)
                    else:
                        await self.event.reply("收到！正在处理...")
                        data = {
                            "prompt":str(self.event.message)[2:],
                            "model" :"text-davinci-003",
                            'max_tokens' :2000,  # 限制回答的长度
                            'temperature':1,
                        }
                        #发送HTTP POST请求
                        response = requests.post(cfg.api_url, json=data, headers=cfg.headers)
                        #解析响应
                        resp = response.json()
                        # 统计回复的字数
                        user_info_old["len"] = str(int(user_info_old["len"]) + len(str(resp["choices"][0]["text"].strip())))
                        # 写入文件
                        with open("user.json", "w") as f:
                            f.write(json.dumps(user_info_old))
                        msg += CQHTTPMessageSegment.text(cfg.prompt_m)
                        msg += CQHTTPMessageSegment.text("A:"+str(resp["choices"][0]["text"].strip())+"\n")
                        msg += CQHTTPMessageSegment.at(int(user_info_old["id"]))
                else:
                    # 非占用者访问
                    msg += CQHTTPMessageSegment.text(cfg.prompt_w)
                    msg += CQHTTPMessageSegment.at(int(user_info_old["id"]))
        await self.event.reply(msg)
    
    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        if str(self.event.message)[:2] in ["Q：", "Q:", "!q"]:
            return True