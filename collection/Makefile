build :
	sudo docker build --no-cache -t qordobahub/qordoba-smart-dictionary-collector .

run :
	sudo docker run --rm -n -e REDIS_HOST=172.17.0.2 qordobahub/qordoba-smart-dictionary-collector

interactive :
	sudo docker run --rm -n -t -i -e REDIS_HOST=172.17.0.2 qordobahub/qordoba-smart-dictionary-collector
