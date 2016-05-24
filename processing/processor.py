#!/usr/bin/env python
import httplib
import json
import os
import multiprocessing
import math
from urlparse import urljoin

import gevent
import gevent.lock
import gipc
import redis
import requests



# Ensure we have data for REDIS_HOST environment variable
assert 'REDIS_HOST' in os.environ, "You haven't set the environment variable for redis"


MAXIMUM_HOLDOFF = 600

redis_client = redis.Redis(os.environ['REDIS_HOST'])

process_lock = gevent.lock.BoundedSemaphore(multiprocessing.cpu_count())

API_BASE_URL = 'http://{host}:{port}/'.format(
    host=os.environ['API_HOST'],
    port=os.environ.get('API_PORT', 8080)
)

API_CREATION_URL = urljoin(API_BASE_URL, 'words/')

JSON_MIME_TYPE = 'application/json'

API_HEADERS = {
    'Content-type': JSON_MIME_TYPE,
    'Accept': JSON_MIME_TYPE
}

CATEGORY_MAP = {
    'ORGANIZATION': 'organization',
    'PERSON': 'person',
    'LOCATION': 'location',
    'MISC': 'miscellaneous'
}


def analyze_item(writer, document):
    from analyzer import parse_document

    # TODO: pass information like url along?
    writer.put(parse_document(document, {}))


def process_item(document_id):
    # Do this in another greenlet to not block the main coroutine
    document = redis_client.get(document_id)
    redis_client.delete(document_id)  # It's only the data, so we remove it as well

    process_lock.acquire()

    try:
        with gipc.pipe() as (reader, writer):
            gipc.start_process(analyze_item, args=(writer, document))
            parsed_data = reader.get()

            print 'Received parsed data: {}'.format(parsed_data)

            for category, word in parsed_data:
                data = json.dumps({
                    'word': word,
                    'category': CATEGORY_MAP[category],
                    'source': document_id
                })
                response = requests.post(API_CREATION_URL, data=data, headers=API_HEADERS)

                try:
                    response.raise_for_status()
                except requests.RequestException:
                    if response.status_code == httplib.BAD_REQUEST and response.json() == {'error': 'key already exists'}:
                        continue

                    print 'Received bad response from API: {}: {}'.format(response.status_code, response.json())
    finally:
        process_lock.release()


def process_queue():
    print 'Starting to process queues...'

    holdoff_count = 0

    while True:
        # Wait to make sure we aren't overloading the analyzer
        process_lock.wait()

        document_id = redis_client.lpop('ner_document_queue')

        if document_id:
            print 'Processing {}'.format(document_id)

            holdoff_count = 0
            gevent.spawn(process_item, document_id)
        else:
            # Gradually increase hold-off interval
            holdoff_count = max(1, holdoff_count + 1)  # A little overflow preventer (unlikely as it might be)
            holdoff_timer = min(MAXIMUM_HOLDOFF, (holdoff_count * (holdoff_count ** math.log(holdoff_count))))

            print 'No items found {} times, sleeping for {} seconds'.format(holdoff_count, holdoff_timer)

            gevent.sleep(holdoff_timer)


if __name__ == '__main__':
    process_queue()


