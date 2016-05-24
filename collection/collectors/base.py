import abc
import os
from collections import namedtuple

import redis


Collection = namedtuple('Collection', ['id', 'content'])


class Collector(object):
    __metaclass__ = abc.ABCMeta

    def __call__(self):
        print 'Starting collection from {}'.format(self.__class__.__name__)

        collections = self.collect()

        print 'Collected {} entries from {}'.format(len(collections), self.__class__.__name__)

        redis_client = redis.Redis(os.environ['REDIS_HOST'])

        for collection in collections:
            # Set the id with some unused data, just so we know what IDs we've processed already
            # Do not process the same id more than once
            created = redis_client.setnx(collection.id, 1)
            if created:
                data_id = ':'.join(['data', collection.id])
                redis_client.lpush('ner_document_queue', data_id)
                redis_client.setex(data_id, collection.content, 3600 * 24)  # Ensure this data expires in a day max

    @abc.abstractmethod
    def collect(self):
        raise NotImplementedError()
