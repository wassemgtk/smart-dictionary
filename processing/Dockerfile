FROM qordobahub/python-base

ENV REDIS_HOST 127.0.0.1

WORKDIR /smart-dictionary
ADD . /smart-dictionary/
RUN pip install -r requirements.txt

CMD ["/usr/bin/env", "python", "processor.py"]
