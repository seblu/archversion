SUBDIRS = src/bin src/lib/archversion misc

.PHONY: pkg test

EXTRA_DIST = COPYRIGHT LICENSE

dist_doc_DATA = README.rst

pkg: export PKGDEST = $(CURDIR)
pkg:
	cd misc && makepkg

test: export PYTHONPATH = $(CURDIR)/lib
test:
	-$(CURDIR)/src/bin/archversion
