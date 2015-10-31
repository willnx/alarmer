# -*- coding: UTF-8 -*-
from __future__ import division

import time

from config import get_config
from event import Event
from monitor_services import Services

config = get_config()
services = Services(config.get('services').split())

def loop():
    """

    """
    pass

