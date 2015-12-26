# -*- coding: UTF-8 -*-
from __future__ import division

import time
import psutil
from collections import deque
from multiprocessing import Pipe

from .config import get_config, get_logger
from .monitoring import Event, Service, Dispatcher


def loop():
    """
    The main loop for monitoring and alerting on services
    """
    # Setup major objects
    config = get_config('monitor')
    logger = get_logger(level=config.grab('level', section='logging'),
                        location=config.grab('location', section='logging'),
                        max_size=config.grab('max_size', section='logging'),
                        rollover_count=config.grab('rollover_count', section='logging')
                        )
    dispatcher = Dispatcher()
    _monitor = config.grab_many(section='services')
    services = {}
    for member in _monitor:
        services[_member] = Service(name=_member, processes=monitor[_member])

    # Setup looping & alerting parmaters
    events = {}
    SEC_TO_MIN = 60
    loop_run_frequency = config.grab('frequency')
    alert_frequency = config.grab('rate') * SEC_TO_MIN
    event_reset_period = config.grab('reset_after') * SEC_TO_MIN

    # Start the dispatcher
    child_pipe, pipe = Pipe(duplex=False)
    dispatcher.run(config, logger, child_pipe)

    # Run monitoring loop
    start_alert_period = time.time()
    while True:
        start_run_time = time.time()
        for member in services:
            new_pids, dead_pids = member.status()

            if dead_pids:
                for name in dead_pids:
                    for pid in dead_pids[name]:
                        new_event = Event(member, name, pid)
                        if new_event in events:
                            # Event has overriden __hash__; that's why this works
                            events[new_event].bump() # add occurance to event
                        else:
                            pipe.send(new_event) # push to dispatcher for alerting

            if new_pids:
                for name in dead_pids:
                    for pid in dead_pids[name]:
                        # It's spam to notify of a new pid ASAP
                        new_event = Event(member, name, pid)
                        events[new_event].bump()

        # remove events that have been 'green' for long enough
        for event in events:
            if time.time() - event.last_event >= event_reset_period:
                events.pop(event, None)

        # Send periodic alerts
        if time.time() - start_alert_period >= alert_frequency:
            for event in events:
                pipe.send(event)
                start_alert_period = time.time()

        # time to nap
        ran_for = time.time() - start_run_time
        delta = loop_run_frequency - ran_for
        time.sleep(max(0, delta)) # so we don't sleep negitive



if __name__ == '__main__':
    loop(services=services,
         dispathcer=dispatcher,
         logger=logger,
         buffer=config.grab('buffer')
