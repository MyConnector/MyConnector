#!/usr/bin/python3
# -*- coding: utf-8 -*-

# MyConnector
# Copyright (C) 2014-2020 Evgeniy Korneechev <ek@myconnector.ru>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the version 2 of the GNU General
# Public License as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

from argparse import ( ArgumentParser,
                       RawTextHelpFormatter )

_version = "0.1"
_info    = "Converter from .ctor (outdated format Connector) to new .myc"

def parseArgs():
    """Description of the command line argument parser"""
    args = ArgumentParser( prog = "ctor2myc", formatter_class = RawTextHelpFormatter, description = _info )
    args.add_argument( "-v", "--version", action = "version", help = "show the application version",
                       version = "ctor2myc v%s\n%s (MyConnector)." % ( _version, _info ) )
    args.add_argument( "filename", type = str, help = "name of the file .ctor for convert" )
    return args.parse_args()

def main():
    args = parseArgs()
    print ( args.filename )