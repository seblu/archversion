# coding: utf-8

# archversion - Archlinux Version Controller
# Copyright © 2012 Sébastien Luttringer
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''Configuration Module'''

from archversion.error import MissingConfigFile
from collections import OrderedDict
from configparser import RawConfigParser
from xdg.BaseDirectory import load_first_config
import logging
import os

class BaseConfigFile(OrderedDict):
    '''Base config file class'''

    def __init__(self, path, default_filename):
        '''Initialize config object'''
        assert(default_filename is not None)
        OrderedDict.__init__(self)
        self.path = path
        if path is None:
            self.path = load_first_config(default_filename)
        if not isinstance(self.path, str) or not os.path.exists(self.path):
            logging.debug("No such config file: %s" % self.path)
            raise MissingConfigFile()
        self.load()

    def load(self):
        '''Load configuration'''
        logging.debug("loading config file at: %s" % self.path)
        self._configparser = RawConfigParser()
        self._configparser.read(self.path)
        self.config = OrderedDict()
        for name in self._configparser.sections():
            self.config[name] = OrderedDict(self._configparser.items(name))
