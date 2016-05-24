FROM qordobahub/python-base

RUN apt-get install -y liblua5.1-0-dev liblua50-dev liblualib50-dev libssl-dev
WORKDIR /smart-dictionary
ADD . /smart-dictionary/
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["/usr/bin/env", "python", "api.py"]
