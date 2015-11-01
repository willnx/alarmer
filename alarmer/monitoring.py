# -*- coding: UTF-8 -*-
"""
Objects use in the monitoring loop
"""
from __future__ import print_function, division, unicode_literals
#TODO add absolute_import

import time
import datetime
import smtplib
from email.mime.text import MIMEText

import psutil
import requests
from netifaces import interfaces, ifaddresses, AF_INET

from config import get_config


class Event(object):
    """
    Represents a change in state for a monitored process
    """

    def __init__(self, name):
        self.name = name
        birth = time.time()
        last_event = time.time()
        event_count = 1

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
    Encapsulates taking an event and notifying someone about it.

    @param config_file
        The absolute file system location of the configuration file

    @param logger
        A Python logger object
    """

    def __init__(self, config_file, logger):
        self.config = get_config('dispatcher')
        self.log = logger
        self.email_on = self.config.get('enable_email')
        self.local_ips = {}

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

    def send(self, event):
        """
        Relay a message for an event

        @param event
            An instantiated Event object
        """
        msg = self._format_msg(event)

        if self.email_on:
            self._send_email(msg, event.name)

        if self.slack_on:
            self._send_slack(msg, event.name)

        if not (self.email_on or self.slack_on):
            msg = 'Unable to send event for {0} because all notifications are disabled'
            self.log.error(msg)

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
        email['To'] = self.config.get('email_to'.split(','))

        host = self.config.get('email_server_host')
        port = self.config.get('email_server_port')
        mail_server = smtplib.SMTP(host, port)
        mail_server.sendmail(email.as_string())
        mail_server.quit()

    def _send_slack(self, msg, event_name):
        """
        TODO
        """
        pass


