#!/usr/bin/python3
# -*- coding: utf-8 -*-

# MyConnector
# Copyright (C) 2014-2023 Evgeniy Korneechev <ek@myconnector.ru>

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
import myconnector.config as CONF


class Password( Gtk.Window ):
    """Window for authentication (as zenity)"""
    def __init__( self, username, window ):
        Gtk.Window.__init__( self, title = CONF._("Authentication...") )
        if window:
            self.main_window = window
            self.main_window.set_sensitive( False )
        builder = Gtk.Builder()
        self.set_resizable( False )
        self.set_modal( True )
        builder.set_translation_domain( CONF.APP )
        self.set_default_icon_name( CONF.APP )
        builder.add_from_file( "%s/passwd.ui" % CONF.UIFOLDER )
        builder.connect_signals(self)
        main_box = builder.get_object( "main_box" )
        self.entry_passwd   = builder.get_object( "entry_passwd"   )
        self.check_passwd   = builder.get_object( "check_passwd"   )
        self.entry_username = builder.get_object( "entry_username" )
        if CONF.check_option( "passwd_off" ):
            self.check_passwd.set_sensitive( False )
        self.add( main_box )
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
        if hasattr( self, "main_window" ):
            self.main_window.set_sensitive( True )

class Error( Gtk.Window ):
    """Error dialog"""
    def __init__( self, text, info = False ):
        Gtk.Window.__init__( self, title = CONF._("Error") if not info else CONF._("Information") )
        self.set_resizable( False )
        self.set_modal( True )
        self.set_default_size( 500, 100 )
        self.set_default_icon_name( CONF.APP )
        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL )
        label = Gtk.Label( label = text )
        label.set_valign( Gtk.Align.END )
        box.pack_start( label, True, True, 0 )
        button = Gtk.Button( label = "OK" )
        button.set_halign( Gtk.Align.CENTER )
        button.set_valign( Gtk.Align.CENTER )
        button.set_size_request( 100, -1 )
        button.connect( "clicked", self.quit )
        box.pack_start( button, True, True, 0 )
        self.add( box )
        self.connect( "destroy", Gtk.main_quit )

    def run( self ):
        self.show_all()
        Gtk.main()

    def quit( self, button ):
        self.destroy()
        Gtk.main_quit()

class Rename( Gtk.Window ):
    """Rename dialog"""
    def __init__( self, old_name ):
        Gtk.Window.__init__( self, title = CONF._("Rename connection") )
        self.set_resizable( False )
        self.set_modal( True )
        self.set_default_size( 400, 100 )
        self.set_default_icon_name( CONF.APP )
        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL )
        self.entry = Gtk.Entry( text = old_name )
        self.entry.set_valign( Gtk.Align.END )
        self.entry.connect( "activate", self.onOk )
        box.pack_start( self.entry, True, True, 0 )
        box0 = Gtk.Box( orientation = Gtk.Orientation.HORIZONTAL )
        button_ok = Gtk.Button( label = "OK" )
        button_ok.set_halign( Gtk.Align.CENTER )
        button_ok.set_valign( Gtk.Align.CENTER )
        button_ok.set_size_request( 100, -1 )
        button_ok.connect( "clicked", self.onOk )
        box0.pack_start( button_ok, True, True, 0 )
        button_cancel = Gtk.Button( label = CONF._("Cancel") )
        button_cancel.set_halign( Gtk.Align.CENTER )
        button_cancel.set_valign( Gtk.Align.CENTER )
        button_cancel.set_size_request( 100, -1 )
        button_cancel.connect( "clicked", self.quit )
        box0.pack_start( button_cancel, True, True, 0 )
        box.pack_start( box0, True, True, 0 )
        self.add( box )
        self.connect( "destroy", Gtk.main_quit )

    def onOk( self, button ):
        self.new_name = self.entry.get_text()
        self.quit()

    def run( self ):
        self.show_all()
        Gtk.main()
        try:
            return( self.new_name )
        except AttributeError:
            return( False )

    def quit( self, *args ):
        self.destroy()
        Gtk.main_quit()

if __name__ == "__main__":
    pass
