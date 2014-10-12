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

from archversion import XDG_DIRECTORY
from archversion.error import MissingConfigFile
from collections import OrderedDict
from configparser import RawConfigParser
from logging import debug
from os.path import join, exists
from xdg.BaseDirectory import save_config_path

class BaseConfigFile(OrderedDict):
    '''Base config file class'''

    def __init__(self, filename):
        '''Initialize config object'''
        assert(filename is not None)
        OrderedDict.__init__(self)
        path = save_config_path(XDG_DIRECTORY)
        self.path = join(path, filename)
        if not isinstance(self.path, str) or not exists(self.path):
            raise MissingConfigFile(self.path)
        self.load()

    def load(self):
        '''Load configuration'''
        debug("loading config file at: %s" % self.path)
        self._configparser = RawConfigParser()
        self._configparser.read(self.path)
        for name in self._configparser.sections():
            self[name] = OrderedDict(self._configparser.items(name))
