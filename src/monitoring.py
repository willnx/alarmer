# -*- coding: UTF-8 -*-
"""
Derp
"""
from __future__ import print_function, division, unicode_literals
#TODO add absolute_import

import psutil

from config import get_config


class Event(object):
    """
    Represents a change in state for a monitored process
    """
    birth = 0
    last_event = 0
    event_count = 0

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Event(name={0}, birth={1}, last_event={2}, event_count={3})'.format(self.name,
                                                                                    self.birth,
                                                                                    self.last_event,
                                                                                    self.event_count)


class Services(object):
    """

    """

    def __init__(self, service_list):
        self.service_list = service_list
        self.group = []
        self.refresh()

    def __iter__(self):
        for i in self.group:
            yield i

    def refresh(self):
        """
        
        """
        self.group = [x for x in psutil.process_iter() if x.name() in self.service_list]


def dispatch(event):
    """
    Relay a message for an event
    """
    pass
