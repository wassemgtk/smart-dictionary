build_dev :
	sudo docker build -t qordobahub/qordoba-smart-dictionary-api .

build :
	sudo docker build --no-cache -t qordobahub/qordoba-smart-dictionary-api .

run :
	sudo docker run --rm -n -e AS_HOST=172.17.0.3 qordobahub/qordoba-smart-dictionary-api

interactive :
	sudo docker run --rm -n -t -i -e AS_HOST=172.17.0.3 qordobahub/qordoba-smart-dictionary-api

bash :
	sudo docker run --rm -t -i -n -e AS_HOST=172.17.0.3 qordobahub/qordoba-smart-dictionary-api /bin/bash
