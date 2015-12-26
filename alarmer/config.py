# -*- coding: UTF-8 -*-
"""
Contains the logic for:
  finding the 'ini' file, generating a configuration object
  setting up a logging object
"""
from __future__ import print_function, division, unicode_literals, absolute_import

import ast
import sys
import logging
import os.path
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


FILE_PATH = os.path.join('alarmer', 'alarmer.ini')


def find_config_file():
    """
    Python normally stores 'datafiles' under the directory defined
    by sys.prefix, but some operating systems (like Ubuntu) break
    with this convention.

    -Raises- IOError when unable to find file

    -Returns- String
    """
    first_guess = os.path.join(sys.prefix, FILE_PATH)
    second_guess = os.path.join(sys.prefix, 'share', FILE_PATH)
    if os.path.isfile(first_guess):
        return first_guess
    elif os.path.isfile(second_guess):
        return second_guess
    else:
        raise IOError('Unable to find {0}'.format(FILE_PATH))


def get_config(section):
    """
    A helper function for finding and constructing the configuration
    object.

    -Returns- Instantiated ConfigReader object

    @param section
        The default section to perform look ups in.
    """
    config_file = find_config_file()
    config = ConfigReader(config_file, section)
    return config

def get_logger(name='alarmer.log', level=None, location=None, max_size=None, rollover_count=None):
    """
    A factory function for making logging objects

    @param name
        The name of the new log file.
        Default is 'alarmer.log'

    @param level
        How verbose the logging is. Valid Values are CRITICAL, ERROR, WARNING,
        INFO, and DEBUG

    @param location
        The directory to save the log file under

    @param max_size
        The set limit of a log file size in MB. Upon exceeding this limit, the
        log file rolls over.

    @param rollover_count
        How many historic log sets to keep
    """
    if not (level and location and max_size and rollover_count):
        msg = 'Missing required param(s): level {0}, location {1}, max_size {2}, rollover_count {3}'.format(level,
                                                                                                            location,
                                                                                                            max_size,
                                                                                                            rollover_count)

    # build base logger
    logger = logging.getLogger()
    logger.setLevel(level.upper())

    # formatter defined
    # Looks like -> 2015-12-12 15:10:15,342 - INFO [<someModule>:89] Hello World!
    formatter = logging.Formatter('%(asctime)s - %(levelname)s [%(module)s:%(lineno)d] %(message)s')

    # file handler construction
    filename = os.path.join(name, location)
    max_size = max_size * 1000 * 1000
    handler = logging.handlers.RotatingFileHandler(filename,
                                                   maxBytes=max_size,
                                                   backupCount=rollover_count)
    handler.setFormatter(formatter)

    # finish building logger object
    logger.addHandler(handler)

    return logger


class ConfigReader(object):
    """
    Allows for strings to be cast into other data types from
    the supplied ini file.

    @param config_file
        The absolute file path to the configuration file

    @param default_section
        The area to look at in the config file when performing a look up.
        Reduces boiler plate as most objects will look in the same section
        for different bits of information.
    """
    def __init__(self, config_file, default_section):
        self._config = ConfigParser.SafeConfigParser()
        self._config.read(config_file)
        self.default_section = default_section


    def grab(self, item, section=None, cast=True):
        """
        Obtain a value from the configuration file

        -Raises- ConfigParsingError when unable to find the requested value

        @param item
            The object in the config file to look for

        @param section
            Which area to look at within the config file.
            Default = The supplied default_section when instantiating the ConfigReader

        @param cast
            ConfigReader values are always strings. When cast is True, it'll attempt
            to convert the found item into a Python data type, like a float or boolean.
            Casting to a function or class is not supported by design.
            Default = True
        """
        if section is None:
            area = self.default_section
        else:
            area = section

        try:
            value = self._config.get(area, item)
        except ConfigParser.NoOptionError as doh:
            raise ConfigParsingError(doh)
        except ConfigParser.NoSectionError as doh:
            raise ConfigParsingError(doh)

        if cast:
            if value.title() in ('True', 'False'):
                value = value.title()
            try:
                answer = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                answer = value
        else:
            answer = value
        return answer

    def grab_many(self, section=None):
        """
        Returns an entire section of an ini file in a dictionary.
        Section values are split on commas, as a result, the dictionary values
        are key -> string : value -> list of strings

        -Returns-
            { 'value_name' : ['value1', 'value2']}

        -Raises-
            ConfigParsingError when unable to find the requested section

        @param section
            The section within the ini to return all items for. If not supplied
            use the default section defined when instantiating the ConfigReader
            object.
            Default is None
        """
        if section is None:
            area = self.default_section
        else:
            area = section

        try:
            base = dict(self._config.items(area))
        except ConfigParser.NoSectionError as doh:
            raise ConfigParsingError(doh)
        else:
            final = {k:base[k].split(',') for k in base}
            return final


class ConfigParsingError(Exception):
     """
     A generic error when for failures in parsing the configuation file.
     """
     pass


if __name__ == '__main__':
    print(find_config_file())
