import os

from alicebot import Bot

bot = Bot()
tmp_dir = "./tmp"
if __name__ == "__main__":
    # 需要event.txt dynamic_info.json user.json tmp_dir/ 存在
    os.mkdir(tmp_dir) if not os.path.exists(tmp_dir) else 1
    os.mknod(os.path.join(tmp_dir, "event.txt")) if not os.path.exists(os.path.join(tmp_dir, "event.txt")) else 1
    os.mknod(os.path.join(tmp_dir, "dynamic_info.json")) if not os.path.exists(os.path.join(tmp_dir, "dynamic_info.json")) else 1
    os.mknod(os.path.join(tmp_dir, "user.json")) if not os.path.exists(os.path.join(tmp_dir, "user.json")) else 1
    bot.run()