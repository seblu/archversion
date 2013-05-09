bin_SCRIPTS = archversion
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = archversion.in

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g'

archversion: archversion.in
	$(do_substitution) < $(srcdir)/archversion.in > $@
	chmod +x $@

install-exec-hook:
	ln -s archversion $(DESTDIR)$(bindir)/avc

#.py: .in
#	$(do_substitution) $<  > $@
#
#archversion_PYTHON = archversion.py
#archversiondir = $(pythondir)/archversion
