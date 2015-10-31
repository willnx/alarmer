# -*- coding: UTF-8 -*-
"""
Test logic for the Services object
"""
from __future__ import print_function, division, unicode_literals
#TODO add absolute_import

import unittest
import psutil
from mock import patch

import alarmer.monitoring


class FakeProc(object):
    '''For testing'''
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, str(k), v)


class TestServices(unittest.TestCase):
    """
    Test suite for the Services object
    """

    def test_services_repr(self):
        """
        Services repr is formatted as expected
        """
        services = alarmer.monitoring.Services(['test_service1', 'test_service2'])

        expected = 'Services(members=test_service1,test_service2)'

        self.assertEqual(expected, str(services))

    @patch.object(alarmer.monitoring, 'psutil')
    def test_services_build_members_automatically(self, mocked_psutil):
        """
        Instantiating the Services object builds the members table
        """
        proc1 = FakeProc(name=lambda: 'proc1')
        proc2 = FakeProc(name=lambda: 'proc2')
        mocked_psutil.process_iter.return_value = [proc1, proc2]

        services = alarmer.monitoring.Services('proc1 proc2'.split())

        expected = set(['proc1', 'proc2'])
        found = set(services.members.keys())

        self.assertEqual(expected, found)

    @patch.object(alarmer.monitoring, 'psutil')
    def test_services_refresh_one(self, mocked_psutil):
        """
        Only the supplied service is refreshed
        """
        proc1 = FakeProc(name=lambda: 'proc1')
        proc2 = FakeProc(name=lambda: 'proc2')
        mocked_psutil.process_iter.return_value = [proc1, proc2]

        services = alarmer.monitoring.Services('proc1 proc2'.split())
        # artificially remove processes references
        services.members['proc1'] = []
        services.members['proc2'] = []

        services.refresh(service='proc1')

        self.assertEqual(len(services.members['proc1']), 1)
        self.assertEqual(len(services.members['proc2']), 0)

    @patch.object(alarmer.monitoring, 'psutil')
    def test_services_refresh(self, mocked_psutil):
        """
        All the supplied services are refreshed
        """
        proc1 = FakeProc(name=lambda: 'proc1')
        proc2 = FakeProc(name=lambda: 'proc2')
        mocked_psutil.process_iter.return_value = [proc1, proc2]

        services = alarmer.monitoring.Services('proc1 proc2'.split())
        # artificially remove processes references
        services.members['proc1'] = []
        services.members['proc2'] = []

        services.refresh()

        self.assertEqual(len(services.members['proc1']), 1)
        self.assertEqual(len(services.members['proc2']), 1)


if __name__ == '__main__':
    unittest.main()
