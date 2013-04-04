===========
ArchVersion
===========

INTRODUCTION
============
*archversion* is an upstream version controller against current *Archlinux* [#]_
or *AUR* [#]_ version.
It can be used by Dev and TUs to check if new release of their package are available.


EXAMPLES
========
*archversion -d* will only display version which differ with cache.
*archversion -n* will only display new verions.
*archversion -nd* will display new version not in cache (useful for mail report).


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
