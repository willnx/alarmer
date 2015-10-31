# -*- coding: UTF-8 -*-
"""
Contains test for the configuration file logic
"""
from __future__ import print_function, division, unicode_literals
#TODO add absolute_import


import sys
import os.path
import unittest
import ConfigParser
from mock import patch, MagicMock

import alarmer.config


class TestConfig(unittest.TestCase):
    """
    A suite of tests for the logic surrounding the configuration file.
    """

    @patch.object(alarmer.config.os.path, 'isfile')
    def test_find_config_1st_guess_works(self, mocked_isfile):
        """
        find_config_files 1st guess was true
        """
        mocked_isfile.return_value = True

        expected = os.path.join(sys.prefix, alarmer.config.FILE_NAME)
        found = alarmer.config.find_config_file()

        self.assertEqual(found, expected)

    @patch.object(alarmer.config.os.path, 'isfile')
    def test_find_config_2nd_guess_works(self, mocked_isfile):
        """
        find_config_files 2nd guess was true
        """
        mocked_isfile.side_effect = [False, True]

        expected = os.path.join(sys.prefix, 'share', alarmer.config.FILE_NAME)
        found = alarmer.config.find_config_file()

        self.assertEqual(found, expected)

    @patch.object(alarmer.config.os.path, 'isfile')
    def test_find_config_all_guesses_fail(self, mocked_isfile):
        """
        find_config_files is unable to find the ini file
        """
        mocked_isfile.return_value = False

        self.assertRaises(IOError, alarmer.config.find_config_file)

    @patch.object(alarmer.config.os.path, 'isfile')
    def test_get_config_bad_file(self, mocked_isfile):
        """
        bubbles up IOError from find_config_file
        """
        mocked_isfile.return_value = False

        self.assertRaises(IOError, alarmer.config.get_config, 'test_section')


    @patch.object(alarmer.config.os.path, 'isfile')
    def test_get_config_returns(self, mocked_isfile):
        """
        get_config returns an instance of ConfigReader
        """	
        mocked_isfile.return_value = True

        config = alarmer.config.get_config('test_section')

        self.assertTrue(isinstance(config, alarmer.config.ConfigReader))

    def test_config_reader_parse_error1(self):
        """
        NoOptionError is reraised as ConfigParsingError
        """
        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.side_effect = ConfigParser.NoOptionError('test', 'test')

        self.assertRaises(alarmer.config.ConfigParsingError,
                          config.get , 'test_item')

    def test_config_reader_parse_error2(self):
        """
        NoSectionError is reraised as ConfigParsingError
        """
        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.side_effect = ConfigParser.NoSectionError('test')

        self.assertRaises(alarmer.config.ConfigParsingError,
                          config.get , 'test_item')

    def test_config_reader_get_cast_to_int(self):
        """
        ConfigReader.get is able to cast to integers
        """
        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.return_value = '1'

        data = config.get('test', cast=True)

        self.assertTrue(data is 1)

    def test_config_reader_get_cast_to_boolean(self):
        """
        ConfigReader.get is able to cast to booleans
        """
        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.return_value = 'true'

        data = config.get('test', cast=True)

        self.assertTrue(data is True)

    def test_config_reader_get_cast_on_string(self):
        """
        ConfigReader.get is able to return strings when casting
        """
        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.return_value = 'mystring'

        data = config.get('test', cast=True)

        self.assertTrue(data is 'mystring')

    def test_config_reader_get_cast_with_func(self):
        """
        ConfigReader.get doesn't cast functions
        """
        def some_func():
            print('failure')

        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.return_value = 'some_func'

        data = config.get('test', cast=True)

        self.assertTrue(data is 'some_func')

    def test_config_reader_get_cast_with_lambda(self):
        """
        ConfigReader.get doesn't cast lambda functions
        """
        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.return_value = 'lambda: "failure"'

        data = config.get('test', cast=True)

        self.assertTrue(data is 'lambda: "failure"')

    def test_config_reader_get_cast_with_class(self):
        """
        ConfigReader.get doesn't cast classes
        """
        class SomeClass(object):
            pass

        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.return_value = 'SomeClass'

        data = config.get('test', cast=True)

        self.assertTrue(data, 'SomeClass')

    def test_config_reader_get_no_cast(self):
        """
        ConfigReader.get return data when not casting
        """
        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.return_value = 'some_value'

        data = config.get('test', cast=False)

        self.assertTrue(data, 'some_value')

    def test_config_reader_get_different_section(self):
        """
        ConfigReader.get called with a different section supplied
        """
        config = alarmer.config.ConfigReader('/some/path', 'test_section')
        config._config.get = MagicMock()
        config._config.get.return_value = 'some_value'

        data = config.get('test', section='other_section', cast=False)

        self.assertTrue(data, 'some_value')


if __name__ == '__main__':
    unittest.main()
