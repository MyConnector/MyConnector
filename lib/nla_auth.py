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

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk
from myconnector.config import UIFOLDER

class NlaAuth( Gtk.Window ):
    """Windows for NLA-authentication"""
    def __init__( self, username ):
        Gtk.Window.__init__( self, title = "Аутентификация (with NLA)" )
        builder = Gtk.Builder()
        self.set_resizable( False )
        builder.add_from_file( "%s/nla_auth.ui" % UIFOLDER )
        builder.connect_signals(self)
        frame_nla          = builder.get_object( "frame_nla"    )
        label_nla          = builder.get_object( "label_nla"    )
        self.entry_passwd  = builder.get_object( "entry_passwd" )
        self.check_passwd  = builder.get_object( "check_passwd" )
        label_nla.set_text( "Имя пользователя: %s" % username )
        self.add( frame_nla )
        self.connect( "delete-event", self.onCancel )
        self.passwd = ""
        self.save   = False
        self.show_all()

    def onCancel( self, *args ):
        self.passwd = None
        self.save   = None
        self.quit()

    def onStart( self, *args ):
        self.passwd = self.entry_passwd.get_text()
        self.save   = self.check_passwd.get_active()
        self.quit()

    def run( self ):
        Gtk.main()
        return( self.passwd, self.save )

    def quit( self ):
        self.destroy()
        Gtk.main_quit()

if __name__ == "__main__":
    pass
