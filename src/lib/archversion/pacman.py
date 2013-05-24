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

'''PKGBUILD Module'''


import logging
import os
import subprocess


def parse_pkgbuild(path, shell="bash"):
    '''
    Source variable from a PKGBUILD
    Use bash to export vars

    WARNING: CODE IS EXECUTED
    '''
    # use shell sourcing to resolve custom bashism into PKGBUILD
    argv = [shell, "-c", "set -a; source '%s'; exec printenv -0" % path]
    # Log it as warn because it's dangerous
    logging.warn("Running bash to source file %s" % path)
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, shell=False)
    bashout = proc.communicate("")[0].decode().split("\0")
    bashenv = dict([x.split("=", 1) for x in bashout if "=" in x])
    # remove current env
    for env in os.environ:
        bashenv.pop(env, None)
    return bashenv

# vim:set ts=4 sw=4 et ai:
