#!/bin/bash

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

TARGET=myconnector
USR=$TARGET/usr
BIN=$USR/bin
ETC=$TARGET/etc/$TARGET
PYTHON=$USR/lib/python3/dist-packages/$TARGET
BASHCOMP=$USR/share/bash-completion/completions
LOCALE=$USR/share/locale/ru/LC_MESSAGES

rm -rf $TARGET
mkdir -p $USR $PYTHON
cp -r ../bin/ $USR/
cp -r ../share/ $USR/
chmod 755 $BIN/*
mv $BIN/$TARGET-check-* $USR/share/$TARGET
cp ../lib/* $PYTHON/
mkdir -p $BASHCOMP
cp ../$TARGET.bashcomp $BASHCOMP/$TARGET
mkdir -p $ETC
cp ../$TARGET.conf $ETC
find $USR -name myconnector-kiosk.1 -delete
mkdir -p $LOCALE
msgfmt ../ru.po -o $LOCALE/$TARGET.mo
INST_SIZE=`du -s myconnector | cut -f 1`
mkdir -p $TARGET/DEBIAN
cd $TARGET
md5deep -rl usr > DEBIAN/md5sums
cd ..
cp control $TARGET/DEBIAN/
sed -i "s\Installed-Size:\Installed-Size: $INST_SIZE\g" $TARGET/DEBIAN/control
fakeroot dpkg-deb --build $TARGET
mv $TARGET.deb ${TARGET}_`grep Version $TARGET/DEBIAN/control | sed s/Version:\ //g`_all.deb
rm -r $TARGET/

#myconnector-docs
TARGET=$TARGET-docs
DOCS=$TARGET/usr/share/doc/$TARGET-$(cat ../VERSION 2>/dev/null)
mkdir -p $DOCS
cp -r ../docs/* $DOCS
rm -f $DOCS/conf.py $DOCS/requirements.txt
INST_SIZE=`du -s myconnector-docs | cut -f 1`
mkdir -p $TARGET/DEBIAN
cd $TARGET
md5deep -rl usr > DEBIAN/md5sums
cd ..
cp control.docs $TARGET/DEBIAN/control
sed -i "s\Installed-Size:\Installed-Size: $INST_SIZE\g" $TARGET/DEBIAN/control
fakeroot dpkg-deb --build $TARGET
mv $TARGET.deb ${TARGET}_`grep Version $TARGET/DEBIAN/control | sed s/Version:\ //g`_all.deb
rm -r $TARGET/
