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

'''Controller Module'''


from archversion import USER_AGENT
from archversion.error import ConfigFileError, InvalidConfigFile, VersionNotFound
from urllib.request import urlopen, Request
import json
import logging
import re
import sys

class VersionController(object):
    '''
    Handle version detection of packages
    '''

    def __init__(self, packages, cache):
        self.packages = packages
        # set cache
        if cache is None:
            cache = {}
        self.cache = cache
        # populate compare table
        # need to be done manually to avoid get_upstream to be in
        self.compare_table = {
            "archweb": self.get_version_archweb,
            "aur": self.get_version_aur,
            "cache": self.get_version_cache,
            "none": self.get_version_none
            }

    @staticmethod
    def get_version_upstream(name, value):
        '''Return upstream version'''
        logging.debug("Get upstream version")
        # check upstream param
        if "url" not in value:
            logging.error("No url specified for %s" % name)
            raise InvalidConfigFile("Missing url in config file")
        url = value["url"]
        regex = value.get("regex", "%s[-_]v?(%s)%s" % (
                    value.get("regex_name", name),
                    value.get("regex_version", "[-.\w]+"),
                    value.get("regex_ext",
                              "\.(?:tar(?:\.gz|\.bz2|\.xz)?|tgz|tbz2|zip)")))
        # retrieve config timeout
        timeout = float(value.get("timeout", None))
        # do the job
        try:
            logging.debug("Requesting url: %s" % url)
            logging.debug("Timeout is %f" % timeout)
            url_req = Request(url, headers={"User-Agent": USER_AGENT})
            url_fd = urlopen(url_req, timeout=timeout)
            logging.debug("Version regex: %s" % regex)
            v = re.findall(regex, url_fd.read().decode("utf-8"))
            if v is None:
                raise VersionNotFound("No regex match on upstream")
            # remove duplicity
            v = list(set(v))
            # list all found versions
            logging.debug("Found versions: %s" % v)
            v = max(v, key=VersionKey)
            # list selected version
            logging.debug("Upstream version is : %s" % v)
            return v
        except Exception as exp:
            raise VersionNotFound("Upstream check failed: %s" % exp)
        assert(False)

    @staticmethod
    def get_version_archweb(name, value):
        '''Return archweb version'''
        logging.debug("Get archweb version")
        # if arch is specified
        archs = value.get("arch", "x86_64,i686,any").split(",")
        # if archweb repository is specified
        repos = value.get("repo",
                          "community-testing,community,testing,extra,core"
                          ).split(",")
        # retrieve config timeout
        timeout = float(value.get("timeout", None))
        for arch in archs:
            for repo in repos:
                url = "http://www.archlinux.org/packages/%s/%s/%s/json" % (
                    repo, arch, name)
                url_req = Request(url, headers={"User-Agent": USER_AGENT})
                logging.debug("Requesting url: %s" % url)
                logging.debug("Timeout is %f" % timeout)
                try:
                    url_fd = urlopen(url_req, timeout=timeout)
                    d = json.loads(url_fd.read().decode("utf-8"))
                    v = d["pkgver"]
                    logging.debug("Archweb version is : %s" % v)
                    return v
                except Exception as exp:
                    logging.debug("Archweb check failed: %s" % exp)
        raise VersionNotFound("No Archweb package found")

    @staticmethod
    def get_version_aur(name, value):
        '''Return archlinux user repository version'''
        logging.debug("Get AUR version")
        try:
            # retrieve config timeout
            timeout = float(value.get("timeout", None))
            url = "http://aur.archlinux.org/rpc.php?type=info&arg=%s" % name
            url_req = Request(url, headers={"User-Agent": USER_AGENT})
            logging.debug("Requesting url: %s" % url)
            logging.debug("Timeout is %f" % timeout)
            url_fd = urlopen(url_req, timeout=timeout)
            d = json.loads(url_fd.read().decode("utf-8"))
            v = d["results"]["Version"].rsplit("-")[0]
            logging.debug("AUR version is : %s" % v)
            return v
        except Exception as exp:
            raise VersionNotFound("AUR check failed: %s" % exp)
        assert(False)

    def get_version_cache(self, name, value):
        '''Return cache version'''
        v_cache = self.cache.get(name, None)
        logging.debug("Cache version is : %s" % v_cache)
        return v_cache

    @staticmethod
    def get_version_none(name, value):
        '''Return cache version'''
        return None

    def check_versions(self, only_new=False, not_in_cache=False):
        '''Check versions against according to compare mode'''
        for name, value in self.packages.items():
            try:
                # get compare mode
                compare = value.get("compare", None)
                if compare is None:
                    raise InvalidConfigFile("No defined compare mode")
                if compare not in self.compare_table:
                    raise InvalidConfigFile("Invalid compare mode")
                # get upstream version
                v_upstream = self.get_version_upstream(name, value)
                # apply eval to upstream
                e_upstream = value.get("eval_upstream", None)
                if e_upstream is not None:
                    v_upstream = eval(e_upstream, {}, {"version": v_upstream})
                    logging.debug("eval_upstream produce version: %s" %
                                  v_upstream)
                # check upstream validity
                if v_upstream is None:
                    raise VersionNotFound("Upstream")
                # get cached version
                v_cache = self.cache.get(name, None)
                # only not in cache mode
                if not_in_cache and v_cache == v_upstream:
                    logging.debug("%s: skipped by not in cache mode" % name)
                    continue
                # get compared version
                v_compare = self.compare_table[compare](name, value)
                # apply eval to compared
                e_compare = value.get("eval_compare", None)
                if e_compare is not None:
                    v_compare = eval(e_compare, {}, {"version": v_compare})
                    logging.debug("eval_compare produce version: %s" %
                                  v_compare)
                # save version to cache after getting compared version
                # to avoid interfering with cache mode
                self.cache[name] = v_upstream
                # only new version mode
                if only_new and (v_compare is None or v_upstream == v_compare):
                    logging.debug("%s: skipped by only new mode" % name)
                    continue
                yield (name, v_upstream, v_compare)
            except VersionNotFound as exp:
                logging.warning("%s: Version not found: %s" % (name, exp))
            except ConfigFileError as exp:
                logging.warning("%s: Invalid configuration: %s" % (name, exp))

    def print_names(self):
        '''Print packages name'''
        for name in self.packages.keys():
            print(name)

    def print_cache(self):
        '''Print cache name and version'''
        for name, version in self.cache.items():
            print(name, ":", version)

    def print_modes(self):
        '''Print comparaison modes'''
        for name in sorted(self.compare_table.keys()):
            print(name)

    def print_versions(self, only_new=False, not_in_cache=False):
        '''Print versions'''
        for name, v_upstream, v_compare in self.check_versions(only_new,
                                                               not_in_cache):
            self.print_version(name, v_upstream, v_compare)

    def print_version(self, name, v1, v2=None):
        '''Handle printing of 2 versions'''
        # define used color
        c_blue =  c_white =  c_yellow =  c_compare =  c_reset = ''
        if sys.stdout.isatty():
            if v2 is None:   c_compare = '\033[1;33m'
            elif v1 == v2:   c_compare = '\033[1;32m'
            else:            c_compare = '\033[1;31m'
            c_blue = '\033[1;34m'
            c_white = '\033[1;37m'
            c_yellow = '\033[1;33m'
            c_reset = '\033[m'
        # print package name
        toprint = "%s[%s%s%s]" % (c_blue, c_white, name, c_blue)
        # print upstream
        toprint += " %sup: %s " % (c_yellow, v1)
        if v2 is not None:
            # print separator
            toprint += "%s|" % c_blue
            origin = self.packages.get(name,{}).get("compare", "other")
            toprint += " %s%s: %s" % (c_compare, origin, v2)
        toprint += c_reset
        print(toprint)


class VersionKey(object):
    '''Sorting key of a version string'''

    def __init__(self, vstring):
        self.vstring = vstring
        self.vlist = re.findall("([0-9]+|[a-zA-Z]+)", vstring)

    def __repr__(self):
        return "%s ('%s')" % (self.__class__.__name__, self.vstring)

    def __str__(self):
        return self.vstring

    def __eq__(self, other):
        return self.vstring == other.vstring

    def __ne__(self, other):
        return self.vstring != other.vstring

    def __lt__(self, other):
        try:
            for i, a in enumerate(self.vlist):
                b = other.vlist[i]
                if a.isdigit() and b.isdigit():
                    a = int(a)
                    b = int(b)
                    if a < b:
                        return True
                    elif a > b:
                        return False
                elif a.isdigit():
                    return False
                elif b.isdigit():
                    return True
                else:
                    if a < b:
                        return True
                    elif a > b:
                        return False
        except IndexError:
            return False
        return True

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

# vim:set ts=4 sw=4 et ai:
