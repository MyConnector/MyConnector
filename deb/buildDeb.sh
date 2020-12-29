#!/bin/bash

# MyConnector
# Copyright (C) 2014-2021 Evgeniy Korneechev <ek@myconnector.ru>

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
MAN=$USR/share/man/man1
PYTHON=$USR/lib/python3/dist-packages/$TARGET
BASHCOMP=$USR/share/bash-completion/completions

rm -rf $TARGET
mkdir -p $USR $PYTHON
cp -r ../bin/ $USR/
cp -r ../share/ $USR/
chmod 755 $BIN/*
ln -s $TARGET $BIN/connector
mv $BIN/$TARGET-check-* $USR/share/$TARGET
cp ../lib/* $PYTHON/
mkdir -p $MAN
cp ../$TARGET.man $MAN/$TARGET.1
mkdir -p $BASHCOMP
cp ../$TARGET.bashcomp $BASHCOMP/$TARGET
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
