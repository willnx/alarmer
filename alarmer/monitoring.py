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
    Represents all services being monitored.

    @verbiage members
        A member is a specific service that's being monitored.

    @verbiage process group
        Some services consist of many processes.

    @param service_list
        A list of all services to monitor.
    """

    def __init__(self, service_list):
        self.service_list = service_list
        self.members = {}
        self.refresh()

    def __iter__(self):
        for service in self.members:
            yield self.members[service]

    def __repr__(self):
        return 'Services(members={0})'.format(','.join(self.members.keys()))

    def refresh(self, service=None):
        """
        Iterate over the process table and update our references
        to processes being monitored.

        @param service
            If provided, only update that services process group
        """
        if service:
            self.members[service] = [x for x in psutil.process_iter() if x.name() == service]

        else:
            self.members = {k: [] for k in self.service_list}
            for proc in psutil.process_iter():
                name = proc.name()
                if name in self.members:
                    self.members[name].append(proc)


class Dispatcher(object):
    """
    """

    def dispatch(self, event):
        """
        Relay a message for an event
        """
        pass
