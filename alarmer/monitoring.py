# -*- coding: UTF-8 -*-
"""
Objects use in the monitoring loop

@jargon service
    Some sort of consumable functionality, generally at a systems level.
    For example, Apache is a webserver service. PostgreSQL is a database service.

@jargon process
    A daemon/thread/etc of a service. Must be a unique item within the process
    table, and addressable via a PID (process ID).
"""
from __future__ import print_function, division, unicode_literals, absolute_import

import time
import datetime
import smtplib
from email.mime.text import MIMEText
from multiprocessing import Process

import psutil
import requests
from netifaces import interfaces, ifaddresses, AF_INET


class Event(object):
    """
    Represents a change in state for a monitored service & process.

    Manipulates how Python checks for equality and changes expected behavior of
    inserting into a dictionary.
    """
    def __init__(self, service, process, pid):
        self._service = service
        self._process = process
        self._pid = [pid]
        self.birth = time.time()
        self.last_event = time.time()
        self.event_count = 1

    @property
    def pid(self):
        return self._pid

    @property
    def name(self):
        return '{0} -> {1}'.format(self._service, self._name)

    def bump(self, pid):
        """
        Update the Event to account for a re-occurance; i.e. "it happened again"
        """
        self.event_count += 1
        self._pid.append(pid)
        self.last_event = time.time()

    def __repr__(self):
        return 'Event(name={0}, birth={1}, last_event={2}, event_count={3})'.format(self.name,
                                                                                    self.birth,
                                                                                    self.last_event,
                                                                                    self.event_count)

    def __hash__(self):
        """
        Allows us to create a new Event instance that has the same hash as an
        existing Event instance; really handy for tracking events in a dictionary.
        """
        return hash(self._service) ^ hash(self._process)

    def __eq__(self, other):
        return hash(self) == hash(other)


class Service(object):
    """
    Represents a monitored service; can consist of many processes.
    Calling for a process as an attribute returns the last known valid PID of that
    process.

    @param name
        The name of the service

    @param processes
        The names of all processes that makeup this service. Expected input is
        an iterable where each value returned is the string name of a process.
        Examples::
          list  -> ['my_process', 'other_process']
          tuple -> ('my_process', 'other_process')

        What not to input::
           string -> 'my_process' ; this iterates as 'm', 'y', '_', 'p', 'r', 'o', 'c', 'e', 's', 's'
    """

    def __init__(self, name, processes=None):
        if isinstance(process, str):
            raise ValueError('processes param cannot be string, must be iterable like list, tuple, etc')
        self._name = name
        self._procs = { k:set() for k in procs }
        self.status()

    def __repr__(self):
        return 'Service(name={0}, processes={1})'.format(self.name, ','.join(self.processes))

    def __len__(self):
        """How many processes are tracked by this Service"""
        return len(self._procs)

    def __iter__(self):
        """Iterate over the psutil.Process objects"""
        for proc in self._procs:
            yield proc

    @property
    def name(self):
        return self._name

    @property
    def processes(self):
        return self._procs.keys()

    def __getattr__(self, attr):
        """Enables users to get a list of pids for a process name"""
        return list(self._procs[attr])

    def _find(self):
        """
        Obtain current data about monitored processes

        -Returns- Dictionary
            Key   -> name of process
            Value -> set of psutil.Process objects
        """
        info = dict.fromkeys(self._procs, set())
        for proc in psutil.process_iter():
            try:
                proc_name = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            else:
                if proc_name in info:
                    info[proc_name].add(proc)

        return info

    def status(self):
        """
        Compairs the current state of the process table with known data about
        the service from the last check of the process table.

        **Note** Mutates state of object by updating PID info for processes

        -Return- Tuple
           index[0] -> dictionary mapping process name to new pids
           index[1] -> dictionary mapping process name to dead pids
        """
        current = self._find()
        new_pids = {}
        dead_pids = {}
        for name in current:
            new = current[name] - self._proc[name]
            new_pids[name] = [x.pid for x in new]
            self._procs[name] = self._proc[name] | current[name] # Union between both sets

        for name in self._procs:
            for proc in self._procs[name]:
                if not proc.is_running():
                    group = dead_pids.setdefaults(name, [])
                    group.append(proc.pid)
                    self._procs[name].remove(proc)

        return new_pids, dead_pids


class Dispatcher(Process):
    """
    Encapsulates taking an event and notifying someone about it.
    """
    local_ips = {}

    @staticmethod
    def _find_ipaddrs():
        """
        So we can add the IP info to the message we dispatch.
        """
        addrs = {}
        for iface_name in interfaces():
            addrs[iface_name] = [x['addr'] for x in ifaddresses(iface_name).setdefault(AF_INET, {'addr': "no addr"})]

        return addrs

    def _format_msg(self, event):
        """
        Generate a message string from an Event object
        """
        # Update for every message in case the IP changes (DHCP...)
        self.local_ips = self._find_ipaddrs()

        birth_time = self._format_timestamp(event.birth)
        recent_time = self._format_timestamp(event.last_event)
        ip_msg = self._ip_info_msg(self.local_ips)

        if birth_time == recent_time:
           # first message for the event
           msg = 'Service {0} went offline at {1}\n'.format(event.name,
                                                            birth_time)
           msg += ip_msg
        else:
           msg = 'Service {0} went offline {1} times since {2}'.format(event.name,
                                                                       event.count,
                                                                       birth_time)
           msg += ip_msg
        return msg

    @staticmethod
    def _ip_info_msg(ip_dict):
        """Convert the IP info into something cleaner"""
        tmp = []
        for key in ip_dict:
            tmp.append('{0}\n\t{1}'.format(key, ','.join(ip_dict[key])))
        return 'Machine IP info:\n{0}'.format(''.join(tmp))

    @staticmethod
    def _format_timestamp(time_val):
        """Turns EPOC time into human time"""
        return datetime.datetime.formtimestamp(int(time_val)).strftime('%Y-%m-%d %H:%M:%S')

    def run(self, config, logger, pipe):
        """
        Loop for new events to notify about

        @param config
            An instance of the ConfigReader object

        @param logger
            A Python logger object

        @param pipe
            An instantiated Event object
        """
        self.config = config
        self.log = logger
        alerts = []
        while True:
            if pipe.poll():
                # if there's something in the pipe, pull everything out of it
                # prevents periodic alerting from blocking the monitoring loop
                while pipe.poll():
                    tmp = pipe.recv()
                    alerts.append(tmp)

                for event in alerts:
                    msg = self._format_msg(event)

                    if self.email_on:
                        self._send_email(msg, event.name)

                    if self.slack_on:
                        self._send_slack(msg, event.name)

                    if not (self.email_on or self.slack_on):
                        msg = 'Unable to send event for {0} because all notifications are disabled'
                        self.log.error(msg)
                alerts = []
            else:
                time.sleep(0.5)

    def _send_email(self, msg, event_name):
        """
        Opens a connection to the SMTP mail server, and sends the
        event email.

        @param msg
            The message to relay to someone
            -Type- string

        @param event_name
            Provides some meta data in email subject line
            -Type- string
        """
        email = MIMEText(msg)
        email['Subject'] = 'Alarmer Event for {0}'.format(event_name)
        email['From'] = 'NoReply'
        email['To'] = self.config.grab('email_to'.split(','))

        host = self.config.grab('email_server_host')
        port = self.config.grab('email_server_port')
        mail_server = smtplib.SMTP(host, port)
        mail_server.sendmail(email.as_string())
        mail_server.quit()

    def _send_slack(self, msg, event_name):
        """
        TODO
        """
        pass
