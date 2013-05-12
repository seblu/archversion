noinst_SCRIPTS=PKGBUILD
EXTRA_DIST = PKGBUILD.in $(noinst_SCRIPTS)
CLEANFILES = $(noinst_SCRIPTS)

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g'


PKGBUILD: PKGBUILD.in
	$(do_substitution) < $(srcdir)/$< > $@

dist_doc_DATA = example*.conf
