bin_SCRIPTS=__init__.py
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = __init__.py.in

archversion_PYTHON =  __init__.py config.py controller.py database.py error.py

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g'

__init__.py: __init__.py.in
	$(do_substitution) < $(srcdir)/$< > $@

archversiondir = $(pythondir)/archversion
