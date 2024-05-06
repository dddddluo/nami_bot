docker stop nami
docker rm -f nami
docker run -it --restart=always -d --name nami \
--platform linux/amd64 \
-v /home/nami/db:/app/db \
-e BOT_TOKEN="abc" \
dddddluo/nami:latest