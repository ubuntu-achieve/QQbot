import os
import json
import time
import requests

from alicebot import Plugin
from alicebot.adapter.apscheduler import scheduler_decorator
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment

from .utils import config, up_dynamic_get

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
        up_name, dynamic_info = up_dynamic_get(cfg.dynamic_url, cfg.headers, cfg.connect_time_out, cfg.read_time_out, self.bot.config.tmp_dir)
        # 读取以前存储的数据
        with open(os.path.join(self.bot.config.tmp_dir, "dynamic_info.json"), "r") as f:
            # 若user.json为空会报错，这里加上一个验证
            try:
                dynamic_info_old = json.load(f)
            except:
                dynamic_info_old = {}
        # 判断是否更新
        if dynamic_info != dynamic_info_old:
            # 发出通知
            msg = CQHTTPMessage()
            msg += CQHTTPMessageSegment.text(f"{up_name}在{dynamic_info[next(iter(dynamic_info.keys()))][1]}发布了动态！\n{dynamic_info[next(iter(dynamic_info.keys()))][1]}\n前往链接：{cfg.dynamic_pub_url}")
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
        if "更新" in str(self.event.message):
            _, dynamic_info = up_dynamic_get(cfg.dynamic_url, cfg.headers, cfg.connect_time_out, cfg.read_time_out, self.bot.config.tmp_dir)
        else:
            # 读取以前存储的数据
            with open(os.path.join(self.bot.config.tmp_dir, "dynamic_info.json"), "r") as f:
                dynamic_info = json.load(f)
        # 发出通知
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.text(f"动态列表：\n")
        for index, dynamic_index in enumerate(dynamic_info.keys()):
            msg += CQHTTPMessageSegment.text(f"\t{index+1}({dynamic_info[dynamic_index][0]}):{dynamic_info[dynamic_index][1]}\n\n")
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
        if "更新" in str(self.event.message):
            _, dynamic_info = up_dynamic_get(cfg.dynamic_url, cfg.headers, cfg.connect_time_out, cfg.read_time_out, self.bot.config.tmp_dir)
        else:
            # 读取以前存储的数据
            with open(os.path.join(self.bot.config.tmp_dir, "dynamic_info.json"), "r") as f:
                dynamic_info = json.load(f)
        # 发出通知
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.text(f"前往链接：{cfg.dynamic_pub_url}\n")
        msg += CQHTTPMessageSegment.text(f"动态列表：\n")
        for index, dynamic_index in enumerate(dynamic_info.keys()):
            for gus in cfg.gugu:
                if type(gus) == tuple:
                    if gus[0] in dynamic_info[dynamic_index][1] and gus[1] in dynamic_info[dynamic_index][1]:
                        msg += CQHTTPMessageSegment.text(f"\t{index+1}({dynamic_info[dynamic_index][0]}):咕了\n")
                        break
                elif gus in dynamic_info[dynamic_index][1]:
                    msg += CQHTTPMessageSegment.text(f"\t{index+1}({dynamic_info[dynamic_index][0]}):咕了\n")
                    break
                if gus == cfg.gugu[-1]:
                    msg += CQHTTPMessageSegment.text(f"\t{index+1}({dynamic_info[dynamic_index][0]}):自己看！检测不出来\n")
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
                with open(os.path.join(self.bot.config.tmp_dir, "event.txt"), "a") as f:
                    f.write("======="+str(self.event.message)+"=======\n")
                return True
    
class plan_send(Plugin):
    """
    当有人对周表做出询问时进行回复
    """
    priority:int = 0
    block:bool   = True  # 停止传播，防止对其他回复模块造成干扰

    def plan_update(self):
        """
        用于更新置顶动态中涉及到周表的图片,也用于初次下载周表图片
        return:True|False(反应周表获取成功与否)
        """
        # 仅在使用时加载paddleocr，以减少占用
        from paddleocr import PaddleOCR, draw_ocr
        _, _ = up_dynamic_get(cfg.dynamic_url, cfg.headers, cfg.connect_time_out, cfg.read_time_out, self.bot.config.tmp_dir)
        # 读取动态的原始文件
        with open(os.path.join(self.bot.config.tmp_dir, "dynamic_info_src.json"), "r") as f:
            info_js = json.load(f)
        # 检测存储文件的文件夹是否存在
        if not os.path.exists("./image/plan"):
            os.makedirs("./image/plan")
        if not os.path.exists(os.path.join(self.bot.config.tmp_dir, "plan")):
            os.makedirs(os.path.join(self.bot.config.tmp_dir, "plan"))
        # 检测周表图片是否存在
        plan_img_list = info_js["data"]["items"][0]["modules"]["module_dynamic"]["major"]["draw"]["items"]
        # 更新图片
        for index in range(len(plan_img_list)):
            # 下载图片
            with open(os.path.join(self.bot.config.tmp_dir, f"plan/{index}.png"), "wb") as f:
                f.write(requests.get(plan_img_list[index]["src"], headers=cfg.headers, timeout=(cfg.connect_time_out, cfg.read_time_out)).content)
        file_list = os.listdir(os.path.join(self.bot.config.tmp_dir, "plan"))
        # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
        # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
        ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        week_plain = {
            "key":["周一","周二", "周三", "周四", "周五", "周六", "周日"],
            "time":str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            }
        for file_name in file_list:
            results = ocr.ocr(os.path.join(self.bot.config.tmp_dir, "plan/"+file_name))
            # 如果没有检测结果则跳过该张图片
            if results == None:
                continue
            # 快速检测该图片是否是周表
            word_count = 0
            for line in results:
                word_count += line[1][0].count("周")
            # 若是周表则保存其相关内容
            if word_count >= 6:
                # TODO 仅适用于Linux系统
                os.system(f"cp {os.path.join(self.bot.config.tmp_dir, 'plan/'+file_name)} ./image/plan/week_plan.png")
                day_info = None
                for line in results:
                    if line[0][1][0] > 1400:
                        continue
                    if line[1][0] in week_plain["key"]:
                        week_plain[line[1][0]] = []
                        day_info = line
                    elif day_info != None and line[0][0][1] - day_info[0][0][1] < 50:
                        week_plain[day_info[1][0]].append(line[1][0])
                break
        if word_count >= 6:
            with open(os.path.join(self.bot.config.tmp_dir, "week_plan.json"), "w") as f:
                # 转换为json格式后写入文件
                json.dump(week_plain, f)
            return True
        else:
            return False

    async def handle(self) -> None:
        # 如果接收到更新命令或文件不存在则进行更新
        if "更新" in str(self.event.message) or not os.path.exists(os.path.join(self.bot.config.tmp_dir, "week_plan.json")):
            with open(os.path.join(self.bot.config.tmp_dir, "event.txt"), "a") as f:
                f.write("======"+"更新周表"+"======\n")
            # 如果更新失败,则不进行接下来的操作
            if not self.plan_update():
                return 0
        # 读取周表数据
        with open(os.path.join(self.bot.config.tmp_dir, "week_plan.json"), "r") as f:
            week_plan = json.load(f)
        msg = CQHTTPMessage()
        msg += CQHTTPMessageSegment.text(f"【周表】-- 更新时间{week_plan['time']}\n")
        msg += CQHTTPMessageSegment.image("file:///data/bot/image/plan/week_plan.png")
        msg += CQHTTPMessageSegment.text(
            "今天("+
            week_plan["key"][time.localtime().tm_wday]+
            ")的内容是："+
            str(week_plan[week_plan["key"][time.localtime().tm_wday]])
            )
        await self.event.reply(msg)
    
    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        if f"[CQ:at,qq={self.bot.config.botuid}]" in str(self.event.raw_message):
            with open(os.path.join(self.bot.config.tmp_dir, "event.txt"), "a") as f:
                f.write("======"+str(self.event.message)+"======\n")
            if "周表" in str(self.event.message):
                return True
            else:
                return False