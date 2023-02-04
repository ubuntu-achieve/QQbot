# 好耶bot: 一个综合性的QQ机器人

好耶bot 基于[Alicebot](https://github.com/st1020/alicebot)开发，集成了多功能：

- B站UP主直播状态提醒
- B站UP主动态更新提醒
- B站UP主周表检测识别
- 表情包存储
- ChatGPT api集成
- 链接解析
- 基本问答功能

## 安装

首先配置Python包

```sh
git colne https://github.com/ubuntu-achieve/QQbot.git
cd QQbot && pip install -r requirements.txt
```

然后安装PaddleOCR环境

## 使用

在终端中运行`run.sh`文件即可

```shell
# 赋予run.sh运行权限
sudo chmod +x run.sh
./run.sh
```

## 许可证

好耶bot 采用 MIT 许可证开放源代码。