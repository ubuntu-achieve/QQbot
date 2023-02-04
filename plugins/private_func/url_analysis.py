import re
import os
import json
import requests
from bs4 import BeautifulSoup

from alicebot import Plugin
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment

from .config import Args

class url_analysis(Plugin):
    """
    对消息中的链接进行基本的解析
    """
    priority:int = 0
    block:bool   = False
    arg = Args()

    def get_method(self, url):
        '''
        requests的get仅支持http协议,所以对url进行自动的调整,并封装成新的get方法
        
        url:待获取链接
        return:0|content(失败返回0,成功返回content)
        '''
        if url[:4] != "http":
            url = "https://" + url
        # 设置超时链接时间、超时读取时间
        html = requests.get(url, headers=self.arg.headers, timeout=(self.arg.connect_time_out, self.arg.read_time_out))
        if html.status_code != 200:
            # 若链接无法访问直接退出程序
            return 0
        else:
            # 若可以访问则返回获取内容
            return html.content

    async def handle(self) -> None:
        url = re.findall(self.arg.url_match, str(self.event.message))[0]
        html = self.get_method(url)
        if html == 0:
            return 0
        html = BeautifulSoup(html, "html.parser")
        # analysis数组中存储的是[网站介绍图片, 网站标题, 网站描述]
        analysis    = [html.find("meta", attrs={"property":"og:image"}), html.find("title"), html.find("meta", attrs={"name":"description"})]
        # 尝试提取网站介绍图片
        try:
            img = self.get_method(analysis[0]["content"])
            with open(os.path.join(self.bot.config.tmp_dir, "analysis.png"), "wb") as f:
                f.write(img)
        except:
            analysis[0] = None
        # 尝试提取网站标题文字
        try:
            analysis[1] = str(analysis[1].text)
        except:
            analysis[1] = None
        # 尝试提取网站描述内容
        try:
            analysis[2] = str(analysis[2]["content"])
        except:
            analysis[2] = None
        # 如果都没解析出来,就不发送消息,直接终止程序
        if analysis.count(None) >= 3:
            return 0
        # 将解析结果写入消息
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.text("【链接解析】\n")
        msg += CQHTTPMessageSegment.text(url+"\n")
        for index in range(len(analysis)):
            if analysis[index] != None:
                if index == 0:
                    msg += CQHTTPMessageSegment.image("file:///data/bot/tmp/analysis.png")
                elif index == 1:
                    msg += CQHTTPMessageSegment.text("\n【"+analysis[index]+"】\n")
                elif index == 2:
                    msg += CQHTTPMessageSegment.text(analysis[index])
        await self.event.reply(msg)
    
    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        # 只解析白名单内的人发出的url
        # 检测对话中是否存在链接
        if str(self.event.user_id) in self.arg.whitelist:
            if len(re.findall(self.arg.url_match, str(self.event.message))) > 0 and len(re.findall(self.arg.cq_match, str(self.event.message))) <= 0:
                with open(os.path.join(self.bot.config.tmp_dir, "event.txt"), "a") as f:
                    f.write(str(self.event.user_id)+"("+str(self.event.message_type)+")"+":"+str(self.event.message).replace(str(self.event.raw_message), "")+"123\n")
                return True
            else:
                return False
        else:
            return False