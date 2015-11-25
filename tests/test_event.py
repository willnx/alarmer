# -*- coding: UTF-8 -*-
"""
Logic for testing our Event object
"""
from __future__ import print_function, division, unicode_literals
#TODO add absolute_import

import unittest
from alarmer.monitoring import Event


class TestEvent(unittest.TestCase):
    """
    Test suite for our Event object
    """

    def test_event_repr(self):
        """
        Format of Event.__repr__
        """
        event = Event('test_event')

        expected = 'Event(name=test_event, birth={0}, last_event={0}, event_count=1)'.format(event.birth)

        self.assertEqual(expected, str(event))

    def test_event_birth_addr(self):
        """
        Event has birth addr
        """
        event = Event('test_event')

        self.assertTrue(hasattr(event, 'birth'))

    def test_event_count_addr(self):
        """
        Event count can increment
        """
        event = Event('test_event')

        #Obj is born with 1 count of an event
        event.event_count += 1
        event.event_count += 1

        self.assertEqual(event.event_count, 3)

    def test_last_event_addr(self):
        """
        Event has birth addr
        """
        event = Event('test_event')

        self.assertTrue(hasattr(event, 'last_event'))


if __name__ == '__main__':
    unittest.main()
