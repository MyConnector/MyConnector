#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

from os import system
from argparse import ( ArgumentParser,
                       RawTextHelpFormatter )
from .config import ( VERSION,
                      RELEASE, _ )

def parseArgs():
    """Description of the command line argument parser"""
    about = "MyConnector - %s (%s)" % (VERSION, RELEASE)
    file_help = "%s (.myc, .remmina, .rdp)" % _("name of the file")
    args = ArgumentParser( prog = "myconnector", formatter_class = RawTextHelpFormatter, usage = "%(prog)s [options]",
                           description = "MyConnector - %s." % _("remote desktop client"),
                           epilog = "%s.\n\nCopyright (C) 2014-2024 Evgeniy Korneechev <ek@myconnector.ru>" %
                           _("Do not specify parameters for starting the GUI") )
    args.add_argument( "-c", "--connection", help = _("name of the saved connection") )
    args.add_argument( "-f", "--file", help = file_help )
    args.add_argument( "-l", "--list", action = "store_true", default = False, help = _("list of the saved connections") )
    args.add_argument( "-e", "--edit", action = "store_true", default = False, help = "%s\n%s vi)" % (
                     _("edit config file for enable/disable the mode (will use"),
                     _("any the editor defines by VISUAL or EDITOR, default") ) )
    args.add_argument( "--kiosk", metavar="<option>", help = "%s ('--kiosk help' %s)" %
                     ( _("KIOSK mode control"), _("for more information") ) )
    args.add_argument( "-u", "--update", action = "store_true", default = False, help = _("updating the program via the Internet") )
    args.add_argument( "-v", "--version", action = "version", help = _("show the application version"), version = about )
    args.add_argument( "-d", "--debug", action = "store_true", default = False, help = _("show log files online") )
    args.add_argument( "-q", "--quit", action = "store_true", default = False, help = _("quit the application") )
    args.add_argument( "name", type = str, nargs = "?", metavar="FILE", help = file_help )
    return args.parse_args()

def main():
    args = parseArgs()
    if args.quit:
        from .ui import quitApp as quit
        quit()
    if args.kiosk:
        try:
            from myconnector.kiosk import CLI
            CLI( args.kiosk )
            exit( 0 )
        except ImportError:
            print( _("The mode KIOSK unavailable, package is not installed.") )
            exit( 127 )
    system( "xdg-mime default myconnector.desktop application/x-myconnector" )
    if args.debug:
        from .ui import startDebug as debug
        debug()
    if args.edit:
        from .ui import editConfig as edit
        res = edit()
        exit( res )
    if args.list:
        from .ui import getSaveConnections as list_connections
        _list, _group = list_connections()
        for record in _list:
            print( '"%s"' % record[ 0 ] )
        exit( 0 )
    if args.update:
        from .ui import updateSelf as update
        res = update()
        exit( res )
    if args.connection:
        from .ui import connect
        connect( args.connection )
        exit( 0 )
    file = ""
    if args.file or args.name:
        file = args.file if args.file else args.name
    from .ui import main as run
    run ( file )

