#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk
from myconnector.config import ( UIFOLDER,
                                 APP, _ )

class PasswdDialog( Gtk.Window ):
    """Window for authentication (as zenity)"""
    def __init__( self, username, domain = None ):
        Gtk.Window.__init__( self, title = _("Authentication...") )
        builder = Gtk.Builder()
        self.set_resizable( False )
        self.set_modal( True )
        builder.set_translation_domain( APP )
        builder.add_from_file( "%s/passwd.ui" % UIFOLDER )
        builder.connect_signals(self)
        main_box = builder.get_object( "main_box" )
        self.entry_passwd   = builder.get_object( "entry_passwd"   )
        self.check_passwd   = builder.get_object( "check_passwd"   )
        self.entry_username = builder.get_object( "entry_username" )
        self.add( main_box )
        if domain: username = "%s\%s" % ( domain, username )
        self.entry_username.set_text( username )
        if username:
            self.entry_passwd.grab_focus()
        else:
            self.entry_username.grab_focus()
        self.connect( "delete-event", self.onCancel )
        self.username = ""
        self.passwd   = False
        self.save     = False
        self.show_all()

    def onCancel( self, *args ):
        self.passwd = False
        self.save   = False
        self.quit()

    def onStart( self, *args ):
        self.passwd   = self.entry_passwd.get_text()
        self.save     = self.check_passwd.get_active()
        self.username = self.entry_username.get_text()
        self.quit()

    def run( self ):
        Gtk.main()
        return( self.username, self.passwd, self.save )

    def quit( self ):
        self.destroy()
        Gtk.main_quit()

if __name__ == "__main__":
    pass
