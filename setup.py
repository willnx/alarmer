# -*- coding: UTF-8 -*-
"""
Let's build the alarmer!
"""
from setuptools import setup, find_packages


VER_MAJOR = 0
VER_MINOR = 0
BUILD = open('build-number.txt').read()
VERSION = '{0}.{1}.{2}'.format(VER_MAJOR, VER_MINOR, BUILD)
DATAFILES = [('alarmer', ['datafiles/alarmer.ini'])]

setup(name='alarmer',
      author='Nicholas Willhite',
      version=VERSION,
      packages=find_packages(),
      data_files = DATAFILES,
      description='A process monitoring tool',
      url='https://github.com/willnx/alarmer',
      install_requires=['psutil', 'netifaces', 'requests'],
      license='LICENSE.txt',
     )
