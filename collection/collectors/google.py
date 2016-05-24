import feedparser
import gevent
import requests

from .base import Collector
from .base import Collection


class GoogleCollector(Collector):
    def collect(self):
        response = requests.get('http://news.google.com/?output=rss')
        response.raise_for_status()

        data = response.content
        parsed_data = feedparser.parse(data)

        jobs = []

        for entry in parsed_data['entries']:
            jobs.append(gevent.spawn(self._collect_data, entry))

        results = []

        for job in jobs:
            try:
                results.append(job.get())
            except Exception:
                # Ignore the errors and continue
                pass

        return results

    def _collect_data(self, entry):
        for retries_left in xrange(4, -1, -1):
            try:
                response = requests.get(entry['link'], timeout=60)
                response.raise_for_status()
            except requests.RequestException:
                if not retries_left:
                    raise

                print 'Error, retrying for url: {}'.format(entry['link'])
            else:
                break

        return Collection('google:{}'.format(entry['id']), response.content)


def demo():
    collector = GoogleCollector()
    print collector.collect()


if __name__ == '__main__':
    demo()
