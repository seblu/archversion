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

from archversion.error import BaseError
from xdg.BaseDirectory import xdg_cache_home
import json
import logging
import os

class JsonDatabase(dict):
    '''Json database'''

    _path = None

    def __del__(self):
        if self._path is not None:
            self.save()

    def _get_path(self, path, default_filename, create=False):
        '''Get a path and ensure its exists if create is True'''
        if path is None:
            if self._path is not None:
                path = self._path
            else:
                path = os.path.join(xdg_cache_home, "archversion", default_filename)
        if create and not os.path.exists(path):
            directory = os.path.split(path)[0]
            if directory != "" and not os.path.isdir(directory):
                try:
                    os.makedirs(directory)
                except (IOError, OSError) as exp:
                    raise BaseError("Create database path failed: %s" % exp)
            try:
                open(path, "a")
            except (IOError, OSError) as exp:
                raise BaseError("Create database filename failed; %s" % exp)
        return path

    def load(self, path, default_filename):
        '''Load registered version database into this database'''
        assert(default_filename is not None)
        # find the right path
        self._path = self._get_path(path, default_filename)
        if self._path is not None and os.path.isfile(self._path):
            logging.debug("Loading database %s" % self._path)
            try:
                fileobj = open(self._path, "r")
                dico = json.load(fileobj)
                self.update(dico)
            except Exception as exp:
                logging.error("Unable to load database %s: %s" % (self._path, exp))

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
