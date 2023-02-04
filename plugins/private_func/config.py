class Args():
    # 匹配url
    url_match = "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
    # 匹配CQ码
    cq_match = "\[(?:CQ:([\s\S][^\]]*))\]"
    headers = {  # 请求的头部
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.63",
    }
    # 白名单,只解析在白名单上的用户发出的链接
    whitelist = ["1852199699", "1471752028", ]
    blacklist = ["2815317501", ]
    # 连接超时时间
    connect_time_out = 3.05
    # 超时读取时间
    read_time_out    = 27