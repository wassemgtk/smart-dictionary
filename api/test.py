#!/usr/bin/env python
# encoding=utf-8
import httplib
import json
from urlparse import urljoin

import requests


JSON_MIME_TYPE = 'application/json'

HEADERS = {
    'Content-type': JSON_MIME_TYPE,
    'Accept': JSON_MIME_TYPE
}

BASE_URL = 'http://127.0.0.1:8080/'

TEST_DATA = {
    'word': 'I.S.I.S',
    'source': 'google news',
    'category': 'organization'
}


def do_request(method, url, data=None):
    url = urljoin(BASE_URL, url)

    if data:
        data = json.dumps(data)

    return requests.request(method, url, data=data, headers=HEADERS)


def test():
    # Test Creation
    create_response = do_request('post', 'words/', TEST_DATA)
    assert create_response.status_code == httplib.CREATED, 'Bad response for creation: {}'.format(create_response.status_code)
    assert create_response.json() == {'status': 'created'}, 'Bad info: {}'.format(create_response.json())

    create_second_response = do_request('post', 'words/', TEST_DATA)
    assert create_second_response.status_code == httplib.BAD_REQUEST, 'Bad response for creation second: {}'.format(create_second_response.status_code)
    assert create_second_response.json() == {'error': 'key already exists'}, 'Bad info: {}'.format(create_second_response.json())

    get_response = do_request('get', 'words/I.S.I.S/')
    assert get_response.status_code == httplib.OK, 'Bad response for get: {}'.format(get_response.status_code)
    assert get_response.json() == TEST_DATA

    category_response = do_request('get', 'categories/organization/')
    assert category_response.status_code == httplib.OK, 'Bad response for category get: {}'.format(category_response.status_code)
    assert len(category_response.json()['results']) == 1, 'Bad number of results for category: {}'.format(len(category_response.json()['results']))
    assert category_response.json()['results'][0] == TEST_DATA, 'Data is not equal to test data: {}'.format(category_response.json()['results'][0])

    delete_response = do_request('delete', 'words/I.S.I.S/')
    assert delete_response.status_code == httplib.NO_CONTENT, 'Bad response for deletion: {}'.format(delete_response.status_code)

    delete_second_response = do_request('delete', 'words/I.S.I.S/')
    assert delete_second_response.status_code == httplib.NOT_FOUND, 'Bad response for deletion second: {}'.format(delete_second_response.status_code)

    print 'All tests ran successfully!'

if __name__ == '__main__':
    try:
        test()
    except AssertionError:
        do_request('delete', 'words/I.S.I.S/')
        raise
