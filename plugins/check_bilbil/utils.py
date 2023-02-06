import os
import json
import time
import requests

class config():
    """
    配置基本信息
    ----------
    live_status_url:主播直播状态检测url
    headers:爬虫的使用的请求头
    [参考源](https://blog.csdn.net/weixin_44347934/article/details/117395218)
    """
    # https://api.bilibili.com/x/space/acc/info?mid=xx&jsonp=jsonp
    # UP主的uid
    mid = 1524155842
    # 检测UP主直播状态的url
    live_status_url = f"https://api.bilibili.com/x/space/acc/info?mid={mid}&jsonp=jsonp"
    # 检测UP主动态的url
    dynamic_url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?offset=&host_mid={mid}"
    # UP主动态发布地址
    dynamic_pub_url = f"https://space.bilibili.com/{mid}/dynamic"
    # 请求的头部
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }
    # 需通知群的群号
    group_id = 590379047
    # 咕咕关键字，通过它对UP主动态内容是否咕咕进行检测，咕咕关键字中的元组只能有两个元素
    gugu = ["晚咕",("有", "事情"), "请假", "请个假", "咕", "拖延"]
    # 连接超时时间
    connect_time_out = 3.05
    # 超时读取时间
    read_time_out    = 27

def up_dynamic_get(url, headers, connect_time_out, read_time_out, tmp_path=None):
    """
    用于获取up的动态内容

    url:用于获取内容的url
    headers:请求头
    connect_time_out:连接超时时间
    read_time_out:读取超时时间
    tmp_path:存储临时文件的位置,若值为None则不存储
    return:up主的名字,解析后的动态信息(若返回值为0, 0则说明解析超时, 需要暂停访问)
    """
    # 爬取信息
    info = requests.get(url, headers=headers, timeout=(connect_time_out, read_time_out))
    if info.status_code != 200 :
        return 0, 0
    info_js = json.loads(info.content.decode())
    if tmp_path != None:
        # 存储原始文件到临时文件夹
        with open(os.path.join(tmp_path, "dynamic_info_src.json"), "w") as f:
            f.write(info.content.decode())
    # 读取新的动态数据
    dynamic_info = {}
    for dynamic_index in range(1, len(info_js["data"]["items"])):
        up_name = info_js["data"]["items"][dynamic_index]["modules"]["module_author"]["name"]
        # 读取时间戳,并保存为日期格式
        dynamic_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info_js["data"]["items"][dynamic_index]["modules"]["module_author"]["pub_ts"]))
        # 跳过直播动态
        if info_js["data"]["items"][dynamic_index]["modules"]["module_dynamic"]["desc"] == None:
            continue
        dynamic_txt  = info_js["data"]["items"][dynamic_index]["modules"]["module_dynamic"]["desc"]["text"]
        dynamic_info[str(dynamic_index)] = [dynamic_time, dynamic_txt]
    return up_name, dynamic_info