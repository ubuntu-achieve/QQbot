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
    group_id = 310810991
    # 咕咕关键字，通过它对UP主动态内容是否咕咕进行检测，咕咕关键字中的元组只能有两个元素
    gugu = ["晚咕",("有", "事情"), "请假", "请个假", "咕"]