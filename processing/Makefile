get_mitie :
	./get_mitie.sh

build_dev : get_mitie
	sudo docker build -t qordobahub/qordoba-smart-dictionary-processing .

build : get_mitie
	sudo docker build --no-cache -t qordobahub/qordoba-smart-dictionary-processing .

run :
	sudo docker run --rm -n -e REDIS_HOST=172.17.0.2 -e API_HOST=172.17.0.6 qordobahub/qordoba-smart-dictionary-processing

interactive :
	sudo docker run --rm -n -t -i -e REDIS_HOST=172.17.0.2 -e API_HOST=172.17.0.6 qordobahub/qordoba-smart-dictionary-processing
