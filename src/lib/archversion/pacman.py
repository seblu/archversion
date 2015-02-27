# coding: utf-8

# archversion - Archlinux Version Controller
# Copyright © 2013 Sébastien Luttringer
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

'''PKGBUILD Module'''


import logging
import os
import pycman
import re
import subprocess

def parse_pkgbuild(path, shell="bash"):
    '''
    Source variable from a PKGBUILD
    Use bash to export vars

    WARNING: CODE IS EXECUTED
    '''
    # use shell sourcing to resolve custom bashism into PKGBUILD
    argv = [shell, "-c", 'set -a; source "%s"; pkgname0="${pkgname[0]}"; exec printenv -0' % path]
    # Log it as warn because it's dangerous
    logging.warn("Running bash to source file %s" % path)
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, shell=False)
    bashout = proc.communicate("")[0].decode().split("\0")
    bashenv = dict([x.split("=", 1) for x in bashout if "=" in x])
    # remove current env
    for env in os.environ:
        bashenv.pop(env, None)
    return bashenv

def pkgbuild_set_version(path, version, reset=True):
    '''
    Change PKGBUILD $pkgver to version
    if a variable $_pkgver is present, this one will be updated instead of $pkgver
    If reset is True, $pkgrel will be set to 1
    '''
    wspces = "[ \t\r\f\v]"
    data = open(path, "r").read()
    # prefer to replace $_pkgver
    var = "pkgver" if re.search("^%s*_pkgver=" % wspces, data,
        re.MULTILINE) is None else "_pkgver"
    data = re.sub("^(%s*%s=).*$" % (wspces, var),
        "\g<1>%s" % version, data, flags=re.MULTILINE)
    if reset:
        data = re.sub("^(%s*pkgrel=).*" % wspces, "\g<1>1", data,
            flags=re.MULTILINE)
    open(path, "w").write(data)

def pkgbuild_update_checksums(path):
    '''
    Update checksums of PKGBUILD
    Use pacman provided scripts updpkgsums
    '''
    subprocess.check_call(["updpkgsums"], shell=False, close_fds=True)

class Pacman(object):
    '''
    Cheap abstration of archlinux package manager
    This object is a singleton to avoid pyalpm to use too much memory
    '''

    _instance = None

    def __new__(cls, config="/etc/pacman.conf"):
        # singleton design pattern
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._handle = pycman.config.PacmanConfig(config).initialize_alpm()
        return cls._instance

    def find_pkg(self, name, repos=None):
        '''
        find a package named name in repos
        '''
        if repos is None:
            dbs = self._handle.get_syncdbs()
        else:
            dbs = [ db for db in self._handle.get_syncdbs() if db.name in repos ]
        # looking into db for package name
        for db in dbs:
            pkg = db.get_pkg(name)
            if pkg is not None:
                return (db, pkg)
        return (None, None)

# vim:set ts=4 sw=4 et ai:
