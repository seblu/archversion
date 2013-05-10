===========
ArchVersion
===========

INTRODUCTION
============
*archversion* is an upstream version controller against current *Archlinux* [#]_
or *AUR* [#]_ version.
It can be used by Dev and TUs to check if new release of their packages are available.

HOW TO USE IT
=============
The first thing to do is to define a list of packages to track by creating a file
~/.config/archversion.conf. The file content looks like an old fashioned INI file.

The following example allow to check the last version of acpid2 against archlinux
official repositories

|  [acpid]
|  url = http://sourceforge.net/projects/acpid2/files/

You can find a more complete example in the misc directory.

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
*archversion* allow you to compare version against different references, not only
official Archlinux repository.
You can compare upstream version against:
- An Archlinux package
- An AUR package
- A cached value


DEPENDENCIES
============
- Python 3.x [#]_
- PyXDG [#]_


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
.. [#] https://github.com/seblu/archversion/
.. [#] http://www.gnu.org/licenses/gpl-2.0.html
