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
from configparser import ( ConfigParser,
                           ParsingError )
from myconnector.connector import options
from os.path import basename
from re import sub

_version = "0.1"
_info    = "Converter from .ctor (outdated format Connector) to new .myc"

def rdp_import( filename ):
    """Get parameters from RDP file"""
    #TODO Fix if Unicode/Windows
    tmpconf = "/tmp/%s" % basename( filename )
    tmpfile = open( tmpconf, "w" )
    print( "[rdp]", file = tmpfile )
    with open( filename, "r", errors = "ignore" ) as f:
        for line in f:
             print( sub( ":.*:", "=", line.strip() ), file = tmpfile )
    tmpfile.close()
    conf = ConfigParser()
    try:
        conf.read( tmpconf )
        try:
            config = conf[ "rdp" ]
        except KeyError:
            options.log.exception( "Файл \"%s\" не содержит секцию [rdp]." % filename )
            return None
        config[ "program"    ] = "freerdp"
        config[ "protocol"   ] = "RDP"
        config[ "fullscreen" ] = "True"
        config[ "server"     ] = config.get( "full address"    , "" )
        config[ "gserver"    ] = config.get( "gatewayhostname" , "" )
        config[ "printers"   ] = str( config.getboolean( "redirectprinters" ) )
        return config
    except ParsingError:
        options.log.exception( "Файл \"%s\" содержит ошибки." % filename )
        return None

def remmina_import( filename ):
    """Get parameters from remmina file"""
    conf = ConfigParser()
    try:
        conf.read( filename )
        try:
            conf[ "remmina" ][ "program" ] = "remmina"
            return conf[ "remmina" ]
        except KeyError:
            options.log.exception( "Файл \"%s\" не содержит секцию [remmina]." % filename )
            return None
    except ParsingError:
        options.log.exception( "Файл \"%s\" содержит ошибки." % filename )
        return None

def ctor_import( filename ):
    """Get parameters from ctor (old format) file"""
    return None

def myc_save( filename ):
    """Save imported parameters to myc file"""
    result = ctor_import( filename )

def parseArgs():
    """Description of the command line argument parser"""
    args = ArgumentParser( prog = "ctor2myc", formatter_class = RawTextHelpFormatter, description = _info )
    args.add_argument( "-v", "--version", action = "version", help = "show the application version",
                       version = "ctor2myc v%s\n%s (MyConnector)." % ( _version, _info ) )
    args.add_argument( "filename", type = str, help = "name of the file .ctor for convert" )
    return args.parse_args()

def main():
    args = parseArgs()
    myc_save( args.filename )

