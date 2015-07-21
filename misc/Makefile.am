noinst_SCRIPTS=PKGBUILD PKGBUILD-git
EXTRA_DIST = PKGBUILD.in $(noinst_SCRIPTS) archversion.service archversion.timer
CLEANFILES = $(noinst_SCRIPTS)

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g'


PKGBUILD: PKGBUILD.in
	$(do_substitution) < $(srcdir)/$< > $@

dist_doc_DATA = *.conf.example

pkg:
	makepkg -p PKGBUILD-git
