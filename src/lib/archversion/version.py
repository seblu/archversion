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

'''Version Module'''


from archversion import USER_AGENT, CONFIG_PACKAGES, CACHE_PACKAGES
from archversion.config import BaseConfigFile
from archversion.database import JsonDatabase
from archversion.error import InvalidConfigFile, VersionNotFound
from archversion.pacman import parse_pkgbuild, Pacman
from collections import OrderedDict
from time import time
from urllib.request import urlopen, Request
import fnmatch
import json
import logging
import os
import re
import subprocess
import sys

class VersionController(object):
    '''
    Handle version detection of packages
    '''

    def __init__(self):
        # load packages configuration
        self.packages = BaseConfigFile(CONFIG_PACKAGES)
        # load cache database
        self.cache = JsonDatabase()
        self.cache.load(CACHE_PACKAGES)
        # set cache
        if set(self.cache.keys()) != set(("downstream", "compare", "upstream")):
            logging.debug("Invalid cache, purging it")
            self.cache.clear()
            self.cache["upstream"] = {}
            self.cache["downstream"] = {}
            self.cache["compare"] = {}

    def reduce_packages(self, packages):
        '''Keep only the give packages list'''
        for pkg in list(self.packages):
            if pkg not in packages:
                self.packages.pop(pkg, None)

    def sort_packages(self):
        '''Sort package list by name'''
        self.packages = self.sort_dict(self.packages)

    def sort_cache(self):
        '''Sort package list by name'''
        self.cache = self.sort_dict(self.cache)

    @staticmethod
    def sort_dict(larousse):
        '''Sort a dictionary into and OrderedDict'''
        return OrderedDict(sorted(larousse.items(), key=lambda t: t[0]))

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
        # do it retry time + 1
        ntry = int(value.get("retry", 0)) + 1
        # do the job
        for n in range(1, ntry + 1):
            try:
                logging.debug("Requesting url: %s (try %d/%d)" % (url, n, ntry))
                logging.debug("Timeout is %f" % timeout)
                url_req = Request(url, headers={"User-Agent": USER_AGENT})
                url_fd = urlopen(url_req, timeout=timeout)
                logging.debug("Version regex: %s" % regex)
                v = re.findall(regex, url_fd.read().decode("utf-8"))
                if v is None or len(v) == 0:
                    raise VersionNotFound("No regex match on upstream")
                # remove duplicity
                v = set(v)
                # list all found versions
                logging.debug("Found versions: %s" % v)
                # exclude versions
                regex_exclude = value.get("regex_exclude", ".*(rc|beta|alpha).*")
                if regex_exclude != "":
                    logging.debug("Exclusion regex: %s" % regex_exclude)
                    v -= set(filter(lambda x: re.match(regex_exclude, x), v))
                    logging.debug("Found versions after exclusion: %s" % v)
                # latest version is the highest
                v = max(v, key=VersionKey)
                # list selected version
                logging.debug("Upstream version is : %s" % v)
                return v
            except Exception as exp:
                if n == ntry:
                    raise VersionNotFound("Upstream check failed: %s" % exp)
        assert(False)

    @staticmethod
    def get_version_downstream(name, value, mode):
        '''Return dowstream version'''
        try:
            return getattr(VersionController, "get_version_downstream_%s" % mode)(name, value)
        except AttributeError:
            raise InvalidConfigFile("Invalid dowstream mode")

    @staticmethod
    def get_version_downstream_pacman(name, value):
        '''Return pacman version'''
        logging.debug("Get pacman version")
        # Load pacman
        pacman = Pacman()
        # filter if repo is provided
        allowed_repos = value.get("repo").split(",") if "repo" in value else None
        # looking into db for package name
        db, pkg = pacman.find_pkg(name, allowed_repos)
        if pkg is not None:
            epoch, pkgver, pkgrel = re.match("^(?:(\d+)\:)?([^-:]*)(?:-(\d+))?",
                pkg.version).groups()
            logging.debug("pacman version in %s: %s" % (db.name, pkgver))
            return pkgver
        raise VersionNotFound("No pacman package found")

    @staticmethod
    def get_version_downstream_archweb(name, value):
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
    def get_version_downstream_aur(name, value):
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
            if "version" not in d or d["version"] != 1:
                raise VersionNotFound("Unsupported AUR version")
            if len(d["results"]) == 0:
                raise VersionNotFound("No such package")
            v = d["results"]["Version"].rsplit("-")[0]
            logging.debug("AUR version is : %s" % v)
            return v
        except Exception as exp:
            raise VersionNotFound("AUR check failed: %s" % exp)
        assert(False)

    @staticmethod
    def get_version_downstream_abs(name, value):
        '''Return abs version'''
        logging.debug("Get ABS version")
        # Get ABS tree path
        abspath = value.get("abs_path", "/var/abs")
        # Map db and name
        repos = [d for d in os.listdir(abspath)
                 if os.path.isdir(os.path.join(abspath, d))]
        # filter if repo is provided
        if "repo" in value:
            allowed_repos = value.get("repo").split(",")
            for r in list(repos):
                if r not in allowed_repos:
                    repos.remove(r)
        # looking into db for package name
        for repo in repos:
            logging.debug("Looking into directory %s" % repo)
            repopath = os.path.join(abspath, repo)
            packages = [d for d in os.listdir(repopath)]
            if name in packages:
                pkgpath = os.path.join(repopath, name, "PKGBUILD")
                if os.path.isfile(pkgpath):
                    # use bash to export vars.
                    # WARNING: CODE IS EXECUTED
                    pkgdict = parse_pkgbuild(pkgpath)
                    if "pkgver" in pkgdict:
                        v = pkgdict["pkgver"]
                        logging.debug("ABS version is : %s" % v)
                        return v
        raise VersionNotFound("No ABS package found")

    @staticmethod
    def get_version_downstream_none(name, value):
        '''Return none version'''
        return ""

    def sync_packages(self):
        '''
        Retrieve upstream and downstream versions and store them in cache
        '''
        for name, value in self.packages.items():
            try:
                logging.debug("Syncing versions of package %s" % name)
                # get upstream version
                v_upstream = self.get_version_upstream(name, value)
                # apply eval to upstream
                e_upstream = value.get("eval_upstream", None)
                if e_upstream is not None:
                    v_upstream = eval(e_upstream, {}, {"version": v_upstream})
                    logging.debug("eval_upstream produce version: %s" % v_upstream)
                # save upstream version
                if self.cache["upstream"].get(name, {}).get("version", None) != v_upstream:
                    logging.debug("caching upstream version %s" % v_upstream)
                    self.cache["upstream"][name] = {"version": v_upstream, "epoch": int(time())}
                else:
                    logging.debug("already cached upstream version %s" % v_upstream)
                # get downstream mode
                mode = value.get("downstream", None)
                if mode is None:
                    logging.warning("%s: Invalid downstream mode: %s." % (name, mode))
                    continue
                # get downstream version
                v_downstream = self.get_version_downstream(name, value, mode)
                # apply eval to downstream
                e_compare = value.get("eval_downstream", None)
                if e_compare is not None:
                    v_compare = eval(e_compare, {}, {"version": v_compare})
                    logging.debug("eval_downstream produce version: %s" % v_downstream)
                # save downstream version
                if self.cache["downstream"].get(name, {}).get("version", None) != v_downstream:
                    logging.debug("caching downstream version %s" % v_downstream)
                    self.cache["downstream"][name] = {"version": v_downstream, "epoch": int(time())}
                else:
                    logging.debug("already cached downstream version %s" % v_downstream)
            except Exception as exp:
                logging.error("Sync of %s: %s" % (name, exp))

    def compare_versions(self, only_new=False, only_fresh=False):
        '''
        Compare versions according compare mode
        Return a generator!
        '''
        for name, value in self.packages.items():
            logging.debug("Comparing versions of package %s" % name)
            # get upstream in cache
            v_upstream = self.cache["upstream"].get(name, {}).get("version", None)
            if v_upstream is None:
                logging.warning("%s: Upstream version not found in cache" % name)
                continue
            # get downstream in cache
            v_downstream = self.cache["downstream"].get(name, {}).get("version", None)
            if v_downstream is None:
                logging.warning("%s: Downstream version not found in cache" % name)
                continue
            # only new version mode
            if only_new and v_upstream == v_downstream:
                logging.debug("%s: skipped by only new mode" % name)
                continue
            # only fresh version mode
            if only_fresh:
                last_cmp = self.cache["compare"].get(name, -1)
                last_up = self.cache["upstream"].get(name, {}).get("epoch", 0)
                last_down = self.cache["downstream"].get(name, {}).get("epoch", 0)
                if (last_cmp >= last_up and last_cmp >= last_down):
                    logging.debug("%s: skipped by only fresh mode" % name)
                    continue
            # save our compare in cache
            self.cache["compare"][name] = int(time())
            yield (name, v_upstream, v_downstream)

    def print_names(self):
        '''Print packages name'''
        for name in self.packages.keys():
            print(name)

    @staticmethod
    def print_modes():
        '''Print comparaison modes'''
        for mode in fnmatch.filter(dir(VersionController), "get_version_downstream_*"):
            print(mode[23:])

    def print_versions(self, only_new=False, only_fresh=False):
        '''Print versions'''
        for name, v_upstream, v_downstream in self.compare_versions(only_new, only_fresh):
            self.print_version(name, v_upstream, v_downstream)

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
        # print downstream
        if v2 is not "":
            # print separator
            toprint += "%s|" % c_blue
            origin = self.packages.get(name,{}).get("downstream", "downstream")
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
