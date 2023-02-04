nohup python main.py > ./log/alicebot.log 2>&1 &
cd plugins/go-cqhttp/ && nohup ./go-cqhttp  > ../../log/cqhttp.log 2>&1 &