#!/usr/bin/env python
# encoding=utf-8
from datetime import datetime
from datetime import timedelta

import gevent


# Some utility classes / functions first
def conv_to_set(obj):
    if isinstance(obj, (int, long)):
        return {obj}

    if not isinstance(obj, set):
        obj = set(obj)

    return obj


class AllMatch(set):
    def __contains__(self, item):
        return True


all_match = AllMatch()


class Event(object):
    def __init__(self, action, minute=all_match, hour=all_match,
                 day=all_match, month=all_match, days_of_week=all_match,
                 args=(), kwargs=None):
        """

        :param action:
        :param minute:
        :type minute: set
        :param hour:
        :param day:
        :param month:
        :param days_of_week:
        :param args:
        :param kwargs:
        :return:
        """
        self.mins = conv_to_set(minute)
        self.hours = conv_to_set(hour)
        self.days = conv_to_set(day)
        self.months = conv_to_set(month)
        self.days_of_week = conv_to_set(days_of_week)
        self.action = action
        self.args = args
        self.kwargs = kwargs or {}

    def matchtime(self, t1):
        return ((t1.minute in self.mins) and
                (t1.hour in self.hours) and
                (t1.day in self.days) and
                (t1.month in self.months) and
                (t1.weekday() in self.days_of_week))

    def check(self, t):
        if self.matchtime(t):
            self.action(*self.args, **self.kwargs)


class CronTab(object):
    def __init__(self, *events):
        self.events = events

    def _check(self):
        t1 = datetime(*datetime.now().timetuple()[:5])
        for event in self.events:
            gevent.spawn(event.check, t1)

        t1 += timedelta(minutes=1)
        s1 = (t1 - datetime.now()).seconds + 1
        gevent.spawn_later(s1, self._check)

    def run(self):
        self._check()
        while True:
            gevent.sleep(60)


from collectors import GoogleCollector


EVENTS = [
    # TODO: change this away from an all match
    Event(
        GoogleCollector(),
        # minute={0, 10, 20, 30, 40, 50}
    )
]

if __name__ == '__main__':
    cron = CronTab(*EVENTS)
    cron.run()
