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

'''Database Module'''

from archversion import XDG_DIRECTORY
from archversion.error import BaseError
from os.path import join
from xdg.BaseDirectory import save_cache_path
import json
import logging


class JsonDatabase(dict):
    '''Json database'''

    _path = None

    def __del__(self):
        if self._path is not None:
            self.save()

    def load(self, filename):
        '''Load registered version database into this database'''
        assert(filename is not None)
        path = join(save_cache_path(XDG_DIRECTORY), filename)
        try:
            open(path, "a")
        except (IOError, OSError) as exp:
            raise BaseError("Create database filename failed; %s" % exp)
        logging.debug("Loading database %s" % path)
        try:
            fileobj = open(path, "r")
            dico = json.load(fileobj)
            self.update(dico)
        except Exception as exp:
            logging.error("Unable to load database %s: %s" % (path, exp))
        # because we use self._path is __del__, this should be done when
        # we are sure that db is loaded
        self._path = path

    def save(self, save_empty=False):
        '''Save current version database into a file'''
        if not save_empty and len(self) == 0:
            logging.debug("Not saved. Database is empty")
            return
        if self._path is not None:
            logging.debug("Saving database %s" % self._path)
            try:
                fileobj = open(self._path, "w")
                json.dump(self, fileobj)
            except Exception as exp:
                logging.error("Unable to save database %s: %s" % (self._path, exp))
