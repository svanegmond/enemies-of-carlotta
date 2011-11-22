prefix = /usr/local
bindir = $(prefix)/bin
mandir = $(prefix)/share/man
man1dir = $(mandir)/man1
man1dires = $(mandir)/es/man1
man1dirfr = $(mandir)/fr/man1
sharedir = $(prefix)/share/enemies-of-carlotta
command = enemies-of-carlotta

all: check

check:
	python testrun.py

install:
	install -d $(DESTDIR)$(bindir)
	install -d $(DESTDIR)$(sharedir)
	install -d $(DESTDIR)$(man1dir)
	install -d $(DESTDIR)$(man1dires)
	install -d $(DESTDIR)$(man1dirfr)
	sed 's,^SHAREDIR=.*,SHAREDIR="$(sharedir)",' enemies-of-carlotta \
	    > $(DESTDIR)$(bindir)/$(command)
	chmod 755 $(DESTDIR)$(bindir)/$(command)
	sh fix-config $(sharedir) < eoc.py > $(DESTDIR)$(sharedir)/eoc.py
	install -m 0755 qmqp.py $(DESTDIR)$(sharedir)/qmqp.py
	python -c 'import py_compile; py_compile.compile("$(DESTDIR)$(sharedir)/eoc.py")'
	python -c 'import py_compile; py_compile.compile("$(DESTDIR)$(sharedir)/qmqp.py")'
	install -m 0644 enemies-of-carlotta.1 $(DESTDIR)$(man1dir)/$(command).1
	install -m 0644 enemies-of-carlotta.1.es $(DESTDIR)$(man1dires)/$(command).1
	install -m 0644 enemies-of-carlotta.1.fr $(DESTDIR)$(man1dirfr)/$(command).1
	install -m 0644 templates/????* $(DESTDIR)$(sharedir)
