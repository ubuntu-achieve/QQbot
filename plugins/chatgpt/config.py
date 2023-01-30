class config():
    # ChatGPT的api密钥
    api_key  = "<yourkey>"
    # ChatGPT访问网址
    api_url  = "https://api.openai.com/v1/completions"
    # 欢迎语
    prompt_b = "欢迎使用“智能对话”模式(其实是好耶调用的ChatGPT)\n输入语法为“Q:+欲对话的内容”；输入“!q”即可结束对话！\n访问速度比较慢，耐心等待哦\n"
    # 提示语
    prompt_m = "#以下为智能对话内容#\n"
    # 结束语
    prompt_e = "“智能对话”已结束，你花费了好耶"
    # 占用提示
    prompt_w = "对话进程被占用，目前占用者为"
    # 错误提示
    error    = "语法错误"
    headers  = {
        "Authorization":f"Bearer {api_key}"
    }
    