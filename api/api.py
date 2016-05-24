#!/usr/bin/env python
# coding=utf-8
import httplib

if __name__ == '__main__':
    import gevent.monkey
    gevent.monkey.patch_all()


import os
import base64

import aerospike
import aerospike.predicates
import bottle
from bottle import delete
from bottle import get
from bottle import post
from bottle import request
from bottle import response

from form import FormFactory


DB_NAME = os.environ.get('AS_DB_NAME', 'db')

NAMESPACE_NAME = os.environ.get('AS_NS_NAME', 'words')

AS_CONFIG = {
    'hosts': [
        (os.environ['AS_HOST'], os.environ.get('AS_PORT', 3000))
    ]
}


# noinspection PyTypeChecker
WordForm = FormFactory(
    {
        'word': {'type': 'text', 'primary': True},
        'source': {'type': 'text', 'default': None, 'null': True, 'blank': True},
        'features': {'type': 'text'}
    }
)


def hash_key(word):
    return base64.urlsafe_b64encode(word.lower()).rstrip('=')


def stringify_dict(unicode_dict):
    return {key.encode('utf-8'): value.encode('utf-8') for key, value in unicode_dict.iteritems()}


def get_client():
    global _client

    try:
        return _client
    except NameError:
        _client = aerospike.client(AS_CONFIG).connect()
        return _client


@get('/')
def get_status():
    return {'status': 'ok'}


@post('/words/')
def create_word():
    form = WordForm(request.json)

    if not form.is_valid():
        response.status = httplib.BAD_REQUEST
        return form.errors

    key = hash_key(form['word'])

    key_data = DB_NAME, NAMESPACE_NAME, key
    client = get_client()

    _, metadata = client.exists(key_data)
    if metadata:
        response.status = httplib.BAD_REQUEST
        return {'error': 'key already exists'}

    client.put(key_data, stringify_dict(form.data))

    response.status = httplib.CREATED
    return {'status': 'created'}


# TODO: pagination
@get('/categories/<category>/')
def get_category_words(category):
    client = get_client()

    query = client.query(DB_NAME, NAMESPACE_NAME)
    query.where(aerospike.predicates.equals('category', category))

    raw_results = []
    query.foreach(raw_results.append)
    results = [value for key, metadata, value in raw_results]

    return {'results': results, 'total': len(results)}


@get('/words/<word>/')
def get_word(word):
    key = hash_key(word)
    key_data = DB_NAME, NAMESPACE_NAME, key

    client = get_client()
    identifier, metadata, value = client.get(key_data)

    if metadata:
        return value
    else:
        response.status = httplib.NOT_FOUND
        return {'error': 'not found'}


@delete('/words/<word>/')
def delete_word(word):
    key = hash_key(word)
    key_data = DB_NAME, NAMESPACE_NAME, key

    client = get_client()

    _, metadata = client.exists(key_data)
    if metadata:
        client.remove(key_data)
        response.status = httplib.NO_CONTENT
    else:
        response.status = httplib.NOT_FOUND
        return {'error': 'not found'}


if __name__ == '__main__':
    from gevent import wsgi

    class LoggerStreamer(object):
        def write(self, string):
            # TODO: switch this to log to stdout
            print string

    class GeventServer(bottle.ServerAdapter):
        """Gevent server for bottle"""

        def run(self, handler):
            """Run the server"""
            server = wsgi.WSGIServer((self.host, self.port), handler, log=LoggerStreamer())
            server.serve_forever()

    app = bottle.default_app()

    run_options = {
        'host': '0.0.0.0',
        'server': GeventServer,
        'quiet': True,
        'app': app
    }

    print 'Starting server on 0.0.0.0:8080'

    bottle.run(**run_options)
