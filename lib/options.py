#!/usr/bin/python3
# -*- coding: utf-8 -*-

# MyConnector
# Copyright (C) 2014-2022 Evgeniy Korneechev <ek@myconnector.ru>

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

import myconnector.ui
from gi.repository import Gtk
from myconnector.config import *
from myconnector.config import _
from logging import ( getLogger,
                      basicConfig,
                      INFO )
class FakeLog():
    def info (self, *args, **kwargs): pass
    def error (self, *args, **kwargs): pass
    def warning (self, *args, **kwargs): pass
    def exception (self, *args, **kwargs): pass

log = FakeLog()

def saveInFile(filename, obj):
    """Save connection parameters to file *.myc)"""
    conf = ConfigParser( interpolation = None )
    conf [ "myconnector" ] = obj
    with open( "%s/%s" % ( WORKFOLDER, filename ), "w" ) as fileCtor:
        conf.write( fileCtor )

def loadFromFile( filename, window = None, _import = False ):
    """Load/import parameters from file .myc or import from .ctor, .rdp, .remmina"""
    if _import:
        from myconnector.converter import ( ctor_import,
                                            remmina_import,
                                            rdp_import )
        ext = Path( filename ).suffix.lower()
        result = False
        if ext == ".ctor":
            result = ctor_import( filename )
        if ext == ".remmina":
            result = remmina_import( filename )
        if ext in [ ".rdp", ".rdpx" ]:
            result = rdp_import( filename )
        if result == None:
            msg_error( "%s \"%s\" %s!" % ( _("Import from file"), filename, _("failed") ), log.error )
            return None
        elif result:
            return result
        else:
            filepath = filename
    else:
        filepath = "%s/%s" % ( WORKFOLDER, filename )
        filename = filename.replace( "tmp_", "" )
        if not os.path.isfile( filepath ):
            msg_error( "%s \"%s\" %s." % ( _("File"), filename, _("not found") ), log.exception )
            return None
    try:
        conf = ConfigParser( interpolation = None )
        try:
            conf.read( filepath )
            try:
                return conf[ "myconnector" ]
            except KeyError:
                msg_error( "%s \"%s\" %s [myconnector]." % ( _("File"), filename, _("does not contain a section") ), log.exception )
        except ParsingError:
            msg_error( "%s \"%s\" %s." % ( _("File"), filename, _("contains errors") ), log.exception )
    except:
        msg_error( "%s \"%s\" %s!" % ( _("File"), filename, _("has an invalid format") ), log.exception )
        return None

try: enableLog = CONFIG.getboolean( 'log' )
except KeyError: enableLog = DEFAULT[ 'log' ]
if enableLog:
    log = getLogger( "myconnector" )
    basicConfig (
        filename = LOGFILE,
        format = "--- %(levelname)-10s %(asctime)s --- %(message)s",
        level = INFO)

def searchSshUser(query):
    """Определение имени пользователя и сервера
    в формате адреса SSH и SFTP - логин@адрес"""
    try:
        login, server = query.strip().split('@')
    except ValueError:
        login = ''
        server = query
    return server, login

def checkLogFile(filePath):
    """Функция проверки размера лог-файла и его архивация, если он больше 10Мб"""
    if os.path.exists( filePath ):
        sizeLog = int( check_output( "stat -c%%s %s; exit 0" % filePath,
                                     shell=True, universal_newlines=True ).strip() )
        if sizeLog > 10000000:
            import tarfile
            from datetime import datetime
            os.chdir(LOGFOLDER)
            filename = os.path.basename(filePath)
            #'2017-04-05 15:09:52.981053' -> 20170405:
            dt = datetime.today()
            today = str(dt).split(' ')[0].split('-'); today = ''.join(today)
            tarName = filePath + '.' + today + '.tgz'
            tar = tarfile.open (tarName, "w:gz")
            tar.add(filename); os.remove(filename)
            os.chdir(MAINFOLDER)
            tar.close()
            msg = "%s %s %s %s" % ( _("Log"), filename,
                  _("exceeded the allowed size (10mb), been archived"), os.path.basename( tarName ) )
            os.system( 'echo "--- INFO       %s  %s" >> %s' % ( str( dt ), msg, LOGFILE ))

def msg_error( msg, func ):
    """Message for logging and show in UI"""
    func ( msg )
    from myconnector.dialogs import Error
    err = Error( msg )
    err.run()

class Properties(Gtk.Window):
    def __init__(self, mainWindow):
        Gtk.Window.__init__(self, title = _("MyConnector Preferences") )
        builder = Gtk.Builder()
        self.main_window = mainWindow
        self.labelRDP = mainWindow.labelRDP
        self.labelVNC = mainWindow.labelVNC
        self.conn_note = mainWindow.conn_note
        self.main_window.window.set_sensitive( False )
        self.combo_protocols = mainWindow.combo_protocols
        self.labelFS = mainWindow.labelFS
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_default_icon_name( APP )
        builder.set_translation_domain( APP )
        builder.add_from_file( "%s/preferences.ui" % UIFOLDER )
        builder.connect_signals(self)
        box = builder.get_object("box_properties")
        cancel = builder.get_object("button_cancel")
        self.changeRdpRem = builder.get_object("radio_RDP_remmina")
        self.changeVncRem = builder.get_object("radio_VNC_remmina")
        self.statusbar = builder.get_object("statusbar")
        self.combo_tabs = builder.get_object("combo_tabs")
        self.changeRdpFree = builder.get_object("radio_RDP_freeRDP")
        self.changeVncView = builder.get_object("radio_VNC_viewer")
        self.entryFS = builder.get_object("entry_FS")
        self.checkTray = builder.get_object("check_TRAY")
        self.checkVersion = builder.get_object("check_VERSION")
        self.checkLog = builder.get_object("check_LOG")
        self.checkPasswd = builder.get_object( "check_PASSWD" )
        self.combo_sort = builder.get_object("combo_sort")
        self.editor = builder.get_object( "entry_editor" )
        admin = builder.get_object( "box_admin" )
        admin.set_sensitive( True ) if ROOT else False
        self.initParameters()
        self.add(box)
        self.connect("delete-event", self.onClose)
        cancel.connect("clicked", self.onCancel, self)
        self.show_all()

    def initParameters(self):
        """Initializing parameters from a file myconnector.conf"""
        if CONFIG.get( "rdp", "freerdp" ) == "freerdp":
            self.changeRdpFree.set_active( True )
        if CONFIG.get( "vnc", "vncviewer" ) == "vncviewer":
            self.changeVncView.set_active( True )
        try: self.combo_tabs.set_active_id( CONFIG[ 'tab' ] )
        except KeyError: self.combo_tabs.set_active_id( '0' )
        try: self.entryFS.set_text( CONFIG[ 'fs' ] )
        except KeyError: self.entryFS.set_text( DEFAULT[ 'fs' ] )
        try: self.checkTray.set_active( CONFIG.getboolean( 'tray' ) )
        except ( KeyError, TypeError ): self.checkTray.set_active( DEFAULT[ 'tray' ] )
        try: self.checkVersion.set_active( CONFIG.getboolean( 'check_version' ) )
        except ( KeyError, TypeError ): self.checkVersion.set_active( DEFAULT[ 'check_version' ] )
        try: self.checkLog.set_active( CONFIG.getboolean( 'log' ) )
        except ( KeyError, TypeError ): self.checkLog.set_active( DEFAULT[ 'log' ] )
        try: self.combo_sort.set_active_id( CONFIG[ 'sort' ] )
        except KeyError: self.combo_tabs.set_active_id( '0' )
        try: self.editor.set_text( CONFIG[ "editor" ] )
        except KeyError: self.editor.set_text( DEFAULT[ "editor" ] )
        try: self.checkPasswd.set_active( CONFIG.getboolean( "passwd_off" ) )
        except ( KeyError, TypeError ): self.checkPasswd.set_active( DEFAULT[ "passwd_off" ] )

    def onCancel( self, button, win ):
        self.closeWin( win )

    def onClose( self, win, *args ):
        self.closeWin( win )

    def closeWin( self, window ):
        window.destroy()
        self.main_window.window.set_sensitive( True )
        if not CONFIG.getboolean( 'tray' ):
            self.main_window.onShowWindow()

    def updateTray( self ):
        if CONFIG.getboolean( 'tray' ):
            if self.main_window.trayDisplayed:
                self.main_window.iconTray.show()
            else: self.main_window.trayDisplayed = myconnector.ui.Gui.initTray(self.main_window)
        else:
            try: self.main_window.iconTray.hide()
            except: pass

    def onSave (self, *args):
        """Сохранение настроек программы"""
        if self.changeRdpRem.get_active():
            CONFIG[ "rdp" ] = "remmina"
        else: CONFIG[ "rdp" ] = "freerdp"
        if self.changeVncRem.get_active():
            CONFIG[ "vnc" ] = "remmina"
        else: CONFIG[ "vnc" ] = "vncviewer"
        CONFIG[ 'tab' ] = self.combo_tabs.get_active_id()
        CONFIG[ 'fs' ] = self.entryFS.get_text()
        CONFIG[ 'tray' ] = str( self.checkTray.get_active() )
        CONFIG[ 'check_version' ] = str( self.checkVersion.get_active() )
        CONFIG[ 'log' ] = str( self.checkLog.get_active() )
        CONFIG[ 'sort' ] = self.combo_sort.get_active_id()
        CONFIG[ 'editor' ] = self.editor.get_text()
        CONFIG[ 'passwd_off' ] = str( self.checkPasswd.get_active() )
        config_save()
        msg_save = "%s myconnector.conf..." % _("The preferences are saved in a file")
        myconnector.ui.viewStatus( self.statusbar, msg_save )
        log.info( msg_save )
        if not self.checkLog.get_active():
            log.warning( _("LOGGING WILL BE DISABLED AFTER THE PROGRAM IS RESTARTED!") )
        myconnector.ui.Gui.initLabels(True, self.labelRDP, self.labelVNC, self.labelFS)
        self.conn_note.set_current_page( int( CONFIG[ 'tab' ] ) )
        self.combo_protocols.set_active_id( CONFIG[ 'tab' ] )
        self.updateTray()

    def clearFile(self, target, title, message):
        """Функция для очисти БД серверов или списка подключений"""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, title)
        dialog.format_secondary_text(message)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            if target == "servers":
                f = open( "%s/%s" % ( WORKFOLDER, filename ), "w" )
                f.close()
                myconnector.ui.viewStatus( self.statusbar, _("Done, the changes will take effect after the restart...") )
                log.info( _("Autofill data is cleared.") )
            if target == "connections":
                os.system( "rm -f %s/*.myc" % WORKFOLDER )
                myconnector.ui.Gui.setSavesToListstore( self.main_window )
        dialog.destroy()

    def onClearServers( self, *args ):
        self.clearFile( "servers", _("Confirm clearing the autofill data"),
                        _("You will lose your entire browsing history!!!") )

    def onClearConnects( self, *args ):
        self.clearFile( "connections", _("Confirm clearing the connection list"),
                        _("All your saved connections will be deleted!!!") )

    def onButtonReset(self,*args):
        """Сброс параметров программы"""
        dialog = Gtk.MessageDialog( self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, _("Reset the program") )
        dialog.format_secondary_text( _("Confirm resetting the program parameters to their default values.") )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            config_save( default = True )
            log.info( _("The program is reset to the default value.") )
        dialog.destroy()
        self.initParameters()
        self.updateTray()

    def onDeleteAllPasswords( self, *args ):
        """Delete all save passwords from keyring"""
        dialog = Gtk.MessageDialog( self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, _("Delete passwords") )
        dialog.format_secondary_text( _("Confirm deleting all saved passwords from the keyring.") )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            import keyring
            for mycfile in os.listdir( WORKFOLDER ):
                connection = "%s/%s" % ( WORKFOLDER, mycfile )
                if Path( mycfile ).suffix.lower() == ".myc":
                    conf = ConfigParser( interpolation = None )
                    try:
                        conf.read( connection )
                        if conf[ "myconnector" ].getboolean( "passwdsave" ):
                            keyring.delete_password( conf[ "myconnector" ].get( "server", "" ),
                                                     conf[ "myconnector" ].get( "username", "" ) )
                            conf[ "myconnector" ][ "passwdsave" ] = "False"
                            with open( connection, "w" ) as f:
                                conf.write( f )
                    except: pass
            log.info( _("All saved passwords have been deleted from the keyring.") )
        dialog.destroy()

if __name__ == '__main__':
    pass
