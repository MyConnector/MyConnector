# MyConnector
# Copyright (C) 2014-2024 Evgeniy Korneechev <ek@myconnector.ru>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the version 2 of the GNU General
# Public License as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

TARGET := myconnector
LOCAL := /usr/local
PREFIX := $(LOCAL)/share
BASE := $(PREFIX)/$(TARGET)
PREFIX_BIN := $(LOCAL)/bin
ALT := $(shell cat /etc/altlinux-release 2>&-)
ifdef ALT
	PYTHON := /usr/lib/python3/site-packages/$(TARGET)
else
	PYTHON := /usr/lib/python3/dist-packages/$(TARGET)
endif
MAN := $(PREFIX)/man
APS := $(PREFIX)/applications
MIME := $(PREFIX)/mime
BASHCOMP := $(PREFIX)/bash-completion/completions
ETC := /etc/$(TARGET)
KIOSK := kiosk.conf
KIOSK_DIR := $(BASE)/kiosk
DATESTAMP := $(shell git log --pretty="%cd" --date=short -1 2>&- | sed s/-//g)
GLOBAL := lib/config.py
LOCALE := $(PREFIX)/locale/ru/LC_MESSAGES
DOCS := $(PREFIX)/doc/$(TARGET)-docs-$(shell cat VERSION 2>&-)
CONF := $(ETC)/$(TARGET).conf

.PHONY: help install uninstall clean remove installdocs

help:
	@echo "Запустите make с одной из необходимых ролей:"
	@echo "... help (по умолчанию, показать данную справку)"
	@echo "... install (установка программы, требует sudo)"
	@echo "... uninstall (удаление программы, требует sudo)"
	@echo "... clean (сброс изменений в исходниках)"

install:
	@apt-get remove myconnector -y || /bin/true
	sed -i s#/usr/share#$(PREFIX)#g $(GLOBAL) kiosk/* bin/*
	sed -i s#/usr/bin/$(TARGET)#$(PREFIX_BIN)/$(TARGET)#g $(GLOBAL) share/applications/$(TARGET).desktop kiosk/*
	sed -i s#$(PREFIX)/applications#/usr/share/applications#g $(GLOBAL)
	@if [ -n "$(DATESTAMP)" ]; then sed -i s#git#git.$(DATESTAMP)#g $(GLOBAL); fi
	install -m755 bin/$(TARGET) $(PREFIX_BIN)
	install -m755 bin/ctor2myc $(PREFIX_BIN)
	cp -r share $(LOCAL)
	mkdir -p $(PYTHON) $(ETC) $(KIOSK_DIR) $(LOCALE)
	install -m644 lib/*.py $(PYTHON)
	install -m755 bin/$(TARGET)-check-* $(BASE)
	install -m644 kiosk/*.desktop $(KIOSK_DIR)
	install -m755 kiosk/$(TARGET)-*kiosk $(KIOSK_DIR)
	install -m755 kiosk/$(TARGET)-kiosk-check $(KIOSK_DIR)
	install -m644 kiosk/kiosk.py $(PYTHON)
	install -m644 kiosk/*.ui $(BASE)/ui
	@msgfmt ru.po -o $(LOCALE)/$(TARGET).mo || echo "Localization is not available, install gettext and try again."
	@if [ ! -f $(ETC)/$(KIOSK) ]; then install -m600 kiosk/$(KIOSK) $(ETC); fi
	@if [ ! -f $(CONF) ]; then install -m644 $(TARGET).conf $(CONF); fi
	mkdir -p $(BASHCOMP)
	install -m644 $(TARGET).bashcomp $(BASHCOMP)/$(TARGET)
	update-mime-database $(MIME)
	update-desktop-database
	@make clean

uninstall:
	rm -f $(PREFIX_BIN)/$(TARGET)
	rm -rf $(BASE) $(PYTHON)
	rm -f $(MAN)/man1/$(TARGET)*
	rm -f $(MAN)/ru/man1/$(TARGET)*
	rm -f $(APS)/$(TARGET).desktop
	rm -f $(MIME)/packages/$(TARGET).xml
	@if [ -f $(ETC)/$(KIOSK) ]; then mv -f $(ETC)/$(KIOSK) $(ETC)/$(KIOSK).makesave; fi
	@if [ -f $(CONF) ]; then mv -f $(CONF) $(CONF).makesave; fi
	find $(PREFIX)/icons/hicolor -name $(TARGET).png -delete
	rm -f $(BASHCOMP)/$(TARGET)
	rm -f $(LOCALE)/$(TARGET).mo
	rm -rf $(DOCS)
	update-mime-database $(MIME)
	update-desktop-database

clean:
	sed -i s#$(PREFIX)#/usr/share#g $(GLOBAL) kiosk/* bin/*
	sed -i s#$(PREFIX_BIN)/$(TARGET)#/usr/bin/$(TARGET)#g $(GLOBAL) share/applications/$(TARGET).desktop kiosk/*
	@if [ -n "$(DATESTAMP)" ]; then sed -i s#.$(DATESTAMP)##g $(GLOBAL); fi

remove:
	make uninstall

installdocs:
	mkdir -p $(DOCS)
	cp -r docs/* $(DOCS)
	rm -f $(DOCS)/conf.py $(DOCS)/requirements.txt
