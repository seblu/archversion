===========
ArchVersion
===========


INTRODUCTION
============
*archversion* is an upstream version of packages tracker against
- the *Archlinux* web site [#]_;
- the *Archlinux* User Repository [#]_;
- a local pacman databases;
- a local abs sync;
- an ad-hoc local cache;
- nothing.

It targets Devs and TUs to help them to stay informed of new release of their packages.
It can also be used by AUR maintainers to track update for their packages.


HOW TO USE IT
=============
The first thing to do is to define a list of packages to track by creating a file
~/.config/archversion.conf. The file content looks like an old fashioned INI file.

The following example allow to check the last version of acpid against archlinux
official repositories

|  [acpid]
|  url = http://sourceforge.net/projects/acpid2/files/

You can find more complete examples in the misc/ directory.

Basically, you can run:
*archversion check -d* to only display version which differ with cache.
*archversion check -n* to only display new verions.
*archversion check -nd* to display new versions not in cache.

You can add the last one in a cron job to get a daily report of which packages
need updates.


HOW IT WORKS
============
As simple as possible! *archversion* retrieve the content of the provided upstream
webpage and search for well-known pattern. And then compare it to the reference.


COMPARING MODES
===============

pacman
------
This mode compare a remote upstream version against a local package version from
pacman databases.
This software is not responsible of syncing pacman databases. Please do it yourself.
This mode is recommended.

archweb
-------
This mode compare a remote upstream version against a remote package version
on *www.archlinux.org*.
Getting version is done using the json ouput of packages pages.
Unfortunatly, Archweb doesn't offer a RPC, so find the right URL for a package
need a lot of call. As a consequency it's slow and load the archlinux servers.
So, I recommend to avoid using this mode in favour of pacman mode!

aur
---
This mode compare a remomte upstream version against a remote package version
from the *Archlinux User Repository*.
AUR provides a JSON-RPC which allow to easily query about packages.

abs
---
This mode compare a remote upstream version against a local package version from
a synced ABS filesystem tree.
This is not responsible of syncing ABS tree. Please do it yourself.
This is **DANGEROUS** because PKGBUILD are *partially* executed to guess the package version!
So, prefer pacman mode!

cache
-----
This mode compare a remote upstream version against a local cached value from a
previous call. This mode could be called memory.
It can be useful to check package upgrades without having a package in repository.

none
----
This mode is a fake one, it only retrieves upstream version without any comparaison.


DEPENDENCIES
============
- Python 3.x [#]_
- PyXDG [#]_
- PyALPM [#]_


SOURCES
=======
*archversion* sources are available on github [#]_.


LICENSE
=======
*archversion* is licensied under the term of GPL v2 [#]_.


AUTHOR
======
*archversion* was started by Sébastien Luttringer in July 2012.


LINKS
=====
.. [#] http://www.archlinux.org/
.. [#] http://aur.archlinux.org/
.. [#] http://python.org/download/releases/
.. [#] http://freedesktop.org/wiki/Software/pyxdg
.. [#] https://projects.archlinux.org/users/remy/pyalpm.git
.. [#] https://github.com/seblu/archversion/
.. [#] http://www.gnu.org/licenses/gpl-2.0.html
