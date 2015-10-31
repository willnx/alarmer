# -*- coding: UTF-8 -*-
"""
Contains the logic for finding the 'ini' file, and generating
a configuration object
"""
from __future__ import print_function, division, unicode_literals
#TODO add absolute_import

import ast
import sys
import os.path
import ConfigParser


FILE_NAME = 'alarmer.ini'


def find_config_file():
    """
    Python normally stores 'datafiles' under the directory defined
    by sys.prefix, but some operating systems (like Ubuntu) break
    with this convention.

    -Raises- IOError when unable to find file

    -Returns- String
    """
    first_guess = os.path.join(sys.prefix, FILE_NAME)
    second_guess = os.path.join(sys.prefix, 'share', FILE_NAME)
    if os.path.isfile(first_guess):
        return first_guess
    elif os.path.isfile(second_guess):
        return second_guess
    else:
        raise IOError('Unable to find {0}'.format(FILE_NAME))


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
        self._default = default_section

    def get(self, item, section=None, cast=True):
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
            area = self._default
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


class ConfigParsingError(Exception):
     """
     A generic error when a requested item from a configuration file
     does not exist.
     """
     pass


if __name__ == '__main__':
    print(find_config_file())
