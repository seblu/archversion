EXTRA_DIST = __init__.py.in

archversion_PYTHON =  __init__.py config.py version.py database.py error.py pacman.py

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g'

__init__.py: __init__.py.in
	$(do_substitution) < $(srcdir)/$< > $@

archversiondir = $(pythondir)/archversion
