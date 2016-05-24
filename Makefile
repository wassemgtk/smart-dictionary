run_redis :
	sudo docker run --rm -n --expose 6379 --name redis -v `pwd`/redis-data:/volume qordobahub/qordoba-redis /usr/bin/redis-server /etc/redis/redis.conf
