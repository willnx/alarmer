# -*- coding: UTF-8 -*-
"""
Test logic for the Services object
"""
from __future__ import print_function, division, unicode_literals
#TODO add absolute_import

import unittest2
import psutil

from alarmer.monitoring import Services


class TestServices(unittest2.TestCase):
    """
    Test suite for the Services object
    """

    def test_no_services(self):
        """
        Doesn't blow up when there are no services found
        """
        pass



if __name__ == '__main__':
    unittest.main()
