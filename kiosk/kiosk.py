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

import os
from gi.repository import Gtk
from configparser import ( ConfigParser,
                           NoOptionError,
                           NoSectionError )
from urllib.parse import unquote
import pwd
from subprocess import call
from shutil import ( copy,
                     chown,
                     SameFileError )
from myconnector.config import ( UIFOLDER,
                                 APP, _ )

_kiosk_dir = "/usr/share/myconnector/kiosk"
_webkiosk = "%s/myconnector-webkiosk" % _kiosk_dir
_kiosk_conf = "/etc/myconnector/kiosk.conf"
_config = ConfigParser( interpolation = None )
_lightdm_conf = "/etc/lightdm/lightdm.conf"
_lightdm_conf_dir = "%s.d" % _lightdm_conf
_autologin_conf = "%s/kiosk.conf" % _lightdm_conf_dir
_sddm_conf = "/etc/X11/sddm/sddm.conf"
_etc_dir = "/etc/kiosk"
_true = ( "True", "true", "Yes", "yes" )

def check_dm():
    """Check DM"""
    if os.path.exists( _lightdm_conf ):
        return "lightdm"
    elif os.path.exists( _sddm_conf ):
        return "sddm"
    else:
        return False
_DM = check_dm()

def enabled():
    """Checking 'is-root', OS and DM for access to settings"""
    return os.getuid() == 0 and os.path.exists( "/etc/altlinux-release" ) and _DM

def dm_clear_autologin():
    """Disable existing records for autologin-user"""
    if _DM == "lightdm":
        clear_cmd = "sed -i \"s/^autologin-user.*/#autologin-user=/\""
        os.system ("%s %s" % (clear_cmd, _lightdm_conf))
        if os.path.exists (_lightdm_conf_dir): os.system ("%s %s/*.conf 2>/dev/null" % (clear_cmd, _lightdm_conf_dir))
        if os.path.exists (_autologin_conf): os.remove(_autologin_conf)
    if _DM == "sddm":
        os.system ( "sed -i s/^User.*/User=/ %s" % _sddm_conf )

def load_kiosk_user():
    """Load username for KIOSK from the config file"""
    tmp = ConfigParser( interpolation = None )
    tmp.read( _kiosk_conf )
    try:
        return tmp[ "kiosk" ].get( "user", "kiosk" )
    except:
        return "kiosk"

def autologin_enable(username):
    """Enable autologin for the mode KIOSK"""
    dm_clear_autologin()
    if _DM == "lightdm":
        with open (_autologin_conf, "w") as f:
            print("[Seat:*]\nautologin-user=%s" % username, file = f)
    if _DM == "sddm":
        os.system ( "sed -i s/^User.*/User=%s/ %s" % ( username, _sddm_conf ) )

def create_kiosk_exec(username, shortcut):
    """Create executable file in X11 directory"""
    kiosk_exec = "/etc/X11/xsession.user.d/%s" % username
    with open (kiosk_exec, "w") as f:
        print("""#!/bin/sh
PROFILE=%s
e="$(sed -n s/^Exec[[:space:]]*=[[:space:]]*//p "/etc/kiosk/$PROFILE")"
test -n "$e" && `$e`""" % shortcut, file = f)
    os.chmod(kiosk_exec, 0o755)

def enable_kiosk( mode = "kiosk" ):
    """Exec MyConnector in the mode KIOSK"""
    username = _config[ "kiosk" ].get( "user", "kiosk" )
    if _config[ "kiosk" ].get( "autologin", "True" ) in _true:
        autologin_enable( username )
    else:
        dm_clear_autologin()
    shortcut = "myconnector-%s.desktop" % mode
    os.system ("install -m644 %s/%s %s/" % (_kiosk_dir, shortcut, _etc_dir))
    create_kiosk_exec(username, shortcut)

def fix_shortcut(mode, _input, output):
    """Replace variable in the desktop files"""
    shortcut = "%s/myconnector-%s.desktop" % (_etc_dir, mode)
    os.system ("sed -i \"s|\%s|%s|g\" %s" % (_input, output, shortcut))

def enable_kiosk_myc( _file ):
    """Exec MyConnector (with myc-file) in the mode KIOSK"""
    mode = "kiosk"
    enable_kiosk(mode)
    fix_shortcut( mode, "$MYC", "'%s'" % _file )

def enable_kiosk_web(url):
    """Exec chromium in the mode KIOSK"""
    mode = "webkiosk"
    enable_kiosk(mode)
    fix_shortcut(mode, "$URL", url)

def disable_kiosk( reset_conf = True):
    """Disable the mode KIOSK"""
    dm_clear_autologin()
    os.system( "rm -f /etc/X11/xsession.user.d/%s 2>/dev/null" % load_kiosk_user() )
    os.system( "rm -f %s/myconnector-*.desktop" % _etc_dir )
    if reset_conf:
        _config.read( _kiosk_conf )
        try:
            _config[ "kiosk" ][ "mode" ] = "0"
        except KeyError:
            config_init( True )
        else:
            with open( _kiosk_conf, 'w' ) as configfile:
                _config.write( configfile )

def enable_ctrl():
    """Enable key 'Ctrl' in webkiosk"""
    os.system( "sed -i /^xmodmap/d %s" % _webkiosk )
    os.system( "sed -i /^setxkbmap/d %s" % _webkiosk )

def disable_ctrl():
    """Disable key 'Ctrl' in webkiosk (swap with 'CapsLock')"""
    enable_ctrl()
    os.system( "sed -i s/while/\"setxkbmap -v -option ctrl:swapcaps\\nxmodmap"
               " -e 'keycode 105 = '\\nxmodmap -e 'keycode 37 = '\\nwhile\"/g %s" % _webkiosk )

def config_init( write ):
    """Default config for KIOSK"""
    _config["kiosk"] = { 'mode': '0',
                         'user': 'kiosk',
                         'autologin': 'true',
                         'file': '',
                         'url': '',
                         'ctrl_disabled': 'false' }
    if write:
        with open( _kiosk_conf, 'w' ) as configfile:
            _config.write( configfile )

def check_user( user ):
    """User existence check"""
    try:
        pwd.getpwnam( user )
    except KeyError:
        os.system( "xterm -e 'adduser %s'" % user )
        os.system( "zenity --info --title='KIOSK' --icon-name=myconnector --text='%s \"%s\" %s'" %
                   ( _("User"), user, _("was created without password! Set, if need.") ) )

def myc_save( user, _input ):
    """Save file for mode = 2"""
    output = "/home/%s/%s" % ( user, os.path.basename( _input ) )
    result = ""
    try:
        copy( _input, output )
        chown( output, user, user )
    except FileNotFoundError as result:
        return result
    except SameFileError:
        pass
    enable_kiosk_myc( output )
    return result

class Kiosk(Gtk.Window):
    def __init__(self):
        """Window with settings of the mode KIOSK"""
        os.makedirs (_lightdm_conf_dir, exist_ok = True)
        os.makedirs (_etc_dir, exist_ok = True)
        Gtk.Window.__init__( self, title = _("KIOSK mode control") )
        builder = Gtk.Builder()
        builder.set_translation_domain( APP )
        builder.add_from_file( "%s/kiosk.ui" % UIFOLDER )
        builder.connect_signals(self)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_default_icon_name("myconnector")
        self.changeKioskOff = builder.get_object("radio_kiosk_off")
        self.changeKioskAll = builder.get_object("radio_kiosk_all")
        self.changeKioskCtor = builder.get_object("radio_kiosk_ctor")
        self.entryKioskCtor = builder.get_object("entry_kiosk_ctor")
        self.changeKioskWeb = builder.get_object("radio_kiosk_web")
        self.entryKioskWeb = builder.get_object("entry_kiosk_web")
        self.entryKioskUser = builder.get_object("entry_kiosk_user")
        self.checkKioskCtrl = builder.get_object("check_kiosk_safe")
        self.checkKioskAutologin = builder.get_object("check_kiosk_autologin")
        box = builder.get_object("box")
        self.add(box)
        self.connect("delete-event", self.onClose)
        self.show_all()
        result = _config.read( _kiosk_conf )
        if not result: config_init( True )
        self.initParams()

    def onClose (self, window, *args):
        """Close window"""
        window.destroy()

    def entryOn(self, widget):
        """Enable widget sensitivity"""
        try: widget.set_button_sensitivity(Gtk.SensitivityType.ON)
        except: widget.set_sensitive(True)

    def entryOff(self, widget):
        """Disable widget sensitivity"""
        try: widget.set_button_sensitivity(Gtk.SensitivityType.OFF)
        except: widget.set_sensitive(False)

    def onSave (self, *args):
        """Action for button 'Save'"""
        mode = "0"
        file = ''
        url = ''
        disable_kiosk()
        _config['kiosk']['autologin'] = str( self.checkKioskAutologin.get_active() )
        user = self.entryKioskUser.get_text()
        if user == "root":
            os.system( "zenity --error --title='KIOSK' --icon-name=myconnector --text='%s'" %
                       _("Root is not allowed to use the mode!") )
            return 1
        if user == "": user = "kiosk"
        _config['kiosk']['user'] = user
        if not self.changeKioskOff.get_active():
            check_user( user )
        if self.changeKioskAll.get_active():
            mode = "1"
            enable_kiosk()
            fix_shortcut( "kiosk", "$MYC", "" )
        if self.changeKioskCtor.get_active():
            mode = "2"
            uri = self.entryKioskCtor.get_uri()
            if uri:
                source = unquote( uri.replace( "file://" , "" ))
                result = myc_save( user, source )
                if result:
                    os.system( "zenity --error --title='KIOSK' --icon-name=myconnector --text=\"%s\"" % result )
                    return 1
            else:
                os.system( "zenity --error --title='KIOSK' --icon-name=myconnector --text='%s'" %
                            _("No connection file specified!") )
                return 1
        if self.changeKioskWeb.get_active():
            mode = "3"
            url = self.entryKioskWeb.get_text()
            enable_kiosk_web(url)
        ctrl = self.checkKioskCtrl.get_active()
        if ctrl:
            disable_ctrl()
        else:
            enable_ctrl()
        _config['kiosk']['mode'] = mode
        _config['kiosk']['file'] = file
        _config['kiosk']['url'] = url
        _config['kiosk']['ctrl_disabled'] = str( ctrl )
        with open( _kiosk_conf, 'w' ) as configfile:
            _config.write( configfile )
        #else need disable tray...
        self.onClose(self)

    def initParams (self):
        """Initialisation state of the UI elements"""
        mode = _config.get( "kiosk", "mode" )
        if mode == "1": self.changeKioskAll.set_active(True)
        elif mode == "2":
            self.changeKioskCtor.set_active(True)
            self.entryKioskCtor.set_uri( "file://%s" % _config.get( "kiosk", "file" ) )
        elif mode == "3":
            self.changeKioskWeb.set_active(True)
            self.entryKioskWeb.set_text( _config.get( "kiosk", "url" ) )
        else:
            self.changeKioskOff.set_active(True)
        ctrl = _config.get( "kiosk", "ctrl_disabled" )
        if ctrl in _true:
            self.checkKioskCtrl.set_active( True )
        autologin = _config.get( "kiosk", "autologin" )
        if autologin in _true:
            self.checkKioskAutologin.set_active( True )
        user = _config.get( "kiosk", "user" )
        self.entryKioskCtor.set_current_folder( "/home/%s" % user )
        if user == "kiosk": user = ""
        self.entryKioskUser.set_text( user )

    def onReset (self, *args):
        """Action for button 'Reset'"""
        self.entryKioskCtor.set_uri('')
        self.entryKioskWeb.set_text('')
        self.initParams()

def kiosk_disabled():
    print( _("KIOSK mode disabled!") )

def kiosk_status():
    print( "%s 'myconnector --kiosk status' %s." % ( _("Try"), _("for more information") ) )

def check_user_from_cli():
    user = _config[ "kiosk" ].get( "user", "" )
    if user:
        check_user( user )
        return user
    else:
        print( "%s: %s" % ( _("Config error"), _("user not specified!") ) )
        disable_kiosk()
        kiosk_disabled()
        exit( 1 )

def enable_from_cli():
    check_user_from_cli()
    enable_kiosk()
    fix_shortcut( "kiosk", "$MYC", "" )
    print( _("KIOSK standalone mode enabled!") )
    kiosk_status()

def enable_from_cli_myc():
    user = check_user_from_cli()
    file  = _config[ "kiosk" ].get( "file",  "" )
    error = False
    if file:
        result = myc_save( user, file )
        if result:
            print( "%s: %s" % ( _("Config error"), result ) )
            error = True
    else:
        print( "%s: %s" % ( _("Config error"), _("No connection file specified!") ) )
        error = True
    if error:
        disable_kiosk()
        kiosk_disabled()
        exit( 1 )
    print( "%s: %s" % ( _("KIOSK the filemode enabled! File"), file ) )
    kiosk_status()

def enable_from_cli_web():
    check_user_from_cli()
    url  = _config[ "kiosk" ].get( "url",  "" )
    if url:
        enable_kiosk_web( url )
        if _config[ "kiosk" ].get( "ctrl_disabled", "False" ) in _true:
            disable_ctrl()
        else:
            enable_ctrl()
    else:
        print( "%s: %s" % ( _("Config error"), _("URL for webkiosk not specified!") ) )
        disable_kiosk()
        kiosk_disabled()
        exit( 1 )
    print( _("WEB-KIOSK enabled!") )
    kiosk_status()

def CLI( option ):
    """KIOSK mode control"""
    if not os.path.exists( "/etc/altlinux-release" ):
        print( _("Unsupported OS! Need ALT!") )
        exit( 1 )
    if option in ( "disable", "status", "enable", "edit" ):
        if os.getuid() == 0:
            if option == "disable":
                disable_kiosk()
                kiosk_disabled()
                exit( 0 )
            if option == "status":
                _config.read( _kiosk_conf )
                try:
                    mode = _config.get( "kiosk", "mode" )
                except ( NoOptionError, NoSectionError ) as e:
                    print( "%s: %s." % ( _("Error"), e ) )
                    print( "%s\n%s:" % ( _("The default settings are set."), _("Config does not exists or contains errors") ) )
                    config_init( True )
                    mode = "0"
                if mode == "0":
                    print( "%s: %s\n----------------" % ( _("Status"), _("disabled") ) )
                else:
                    print( "%s: %s\n---------------" % ( _("Status"), _("enabled") ) )
                print( "%s %s:" % ( _("KIOSK config file"), _kiosk_conf ) )
                os.system( "cat %s" % _kiosk_conf )
                exit( 0 )
            if option == "enable":
                disable_kiosk( False )
                _config.read( _kiosk_conf )
                try:
                    mode = _config.get( "kiosk", "mode" )
                except NoSectionError:
                    config_init( True )
                finally:
                    _config[ "kiosk" ][ "mode" ] = "1"
                    enable_from_cli()
                    with open( _kiosk_conf, 'w' ) as configfile:
                        _config.write( configfile )
                    exit( 0 )
            if option == "edit":
                editor = os.getenv( "EDITOR" )
                if not editor: editor = os.getenv( "VISUAL" )
                if not editor: editor = "vi"
                call( [ editor, _kiosk_conf ] )
                _config.read( _kiosk_conf )
                disable_kiosk( False )
                try:
                    mode = _config[ "kiosk" ].get( "mode", "0" )
                except KeyError:
                    print( "%s %s" % ( _("Config contains errors."), _("The default settings are set.") ) )
                    config_init( True )
                    kiosk_disabled()
                    exit( 1 )
                if mode == "0":
                    kiosk_disabled()
                    exit( 0 )
                if mode == "1":
                    enable_from_cli()
                    exit( 0 )
                if mode == "2":
                    enable_from_cli_myc()
                    exit( 0 )
                if mode == "3":
                    enable_from_cli_web()
                    exit( 0 )
        else:
            print( _("Permission denied!") )
            exit( 126 )
    if option == "help":
        print( """myconnector --kiosk - %s

%s: myconnector --kiosk <option>

%s:
  enable        %s;
  edit          %s
                %s: vi);
  disable       %s;
  status        %s;
  help          %s.

%s: man myconnector-kiosk

Copyright (C) 2014-2021 Evgeniy Korneechev <ek@myconnector.ru>""" % (
        _("KIOSK mode control"),
        _("Usage"),
        _("Options"),
        _("enable the standalone mode"),
        _("edit config file for enable/disable the mode (will use"),
        _("any the editor defines by VISUAL or EDITOR, default"),
        _("disable the mode"),
        _("display current status of the mode"),
        _("show this text and exit"),
        _("See also"), ) )
        exit( 0 )
    else:
        print( "myconnector --kiosk: %s: %s" % ( _("invalid command"), option ) )
        print( "%s 'myconnector --kiosk help' %s." % ( _("Try"), _("for more information") ) )
        exit( 1 )

if __name__ == '__main__':
    pass
