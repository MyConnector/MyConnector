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

import gettext
import locale
import os
import signal
from subprocess import ( check_output,
                         call,
                         Popen )
from configparser import ( ConfigParser,
                           ParsingError )
from pathlib import Path

from sys import version_info
if version_info.minor >= 7:
    from myconnector.dialogs import Error
else:
    class Error:
        def __init__(self, text):
            self.text = text
        def run( self ):
            os.system( "zenity --error --icon-name=myconnector --text=\"%s\"" % self.text )

APP         = "myconnector"
VERSION     = "2.4.3"

_global_conf_file = "/etc/%s/%s.conf" % ( APP, APP )

def check_global( attr ):
    """Checking global settings"""
    conf = ConfigParser( interpolation = None )
    conf.read( _global_conf_file )
    try:
        return conf[ APP ].getboolean( attr )
    except:
        return False

def check_option( attr ):
    try:
        config_init()
        check = CONFIG.getboolean( attr )
    except KeyError:
        check = DEFAULT[ attr ]
    return check

ROOT = True if os.getuid() == 0 else False
HOMEFOLDER = os.getenv( "HOME" )
USERFOLDER = "%s/.%s" % ( HOMEFOLDER, APP )

if ROOT or check_global( "system_folder" ):
    WORKFOLDER = "/etc/%s" % APP
else:
    WORKFOLDER = USERFOLDER

_config = ConfigParser( interpolation = None )

if ROOT or check_global( "system_config" ):
    _config_file = _global_conf_file
else:
    _config_file = "%s/%s.conf" % ( USERFOLDER, APP )

MAINFOLDER = "/usr/share/%s"   % APP
ICONFOLDER = "%s/icons"        % MAINFOLDER
UIFOLDER   = "%s/ui"           % MAINFOLDER
LOGFOLDER  = "%s/.%s/logs"     % ( HOMEFOLDER, APP )
LOGFILE    = "%s/%s.log"       % ( LOGFOLDER, APP )
STDLOGFILE = "%s/all.log"      % LOGFOLDER
RECENTFILE = "%s/recent.db"    % WORKFOLDER
FIRSTRUN   = False if os.path.exists( WORKFOLDER ) else True
MO_FOLDER  = "/usr/share/locale"
LOCALDOCS  = "/usr/share/doc/%s-docs-%s/index.html" % ( APP, VERSION )
GLOBAL     = False

_config = ConfigParser( interpolation = None )

locale.bindtextdomain(  APP, MO_FOLDER )
gettext.bindtextdomain( APP, MO_FOLDER )
gettext.textdomain( APP )
_ = gettext.gettext

os.system( "mkdir -p %s" % LOGFOLDER )

DEFAULT    = { "rdp"            : "freerdp",
               "vnc"            : "vncviewer",
               "spice"          : "remmina",
               "tab"            : "0",
               "log"            : True,
               "fs"             : "xdg-open",
               "editor"         : "",
               "tray"           : False,
               "passwd_off"     : False,
               "check_version"  : True,
               "sort"           : "0",
               "system_config"  : False,
               "system_folder"  : False,
               "stealth_mode"   : False }

#Исходные данные для ярлыка подключения
DESKTOP_INFO = """#!/usr/bin/env xdg-open
[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Icon=myconnector
"""
EXEC = "/usr/bin/myconnector -c "

#Определение путей до папок пользователя
_dirs = {}
try:
    for _string in open(HOMEFOLDER + "/.config/user-dirs.dirs"):
        if _string[0] != "#":
            _name, _value = _string.strip().split('=')
            _dirs[_name] = _value
    DESKFOLDER = _dirs["XDG_DESKTOP_DIR"]
    DOWNFOLDER = _dirs["XDG_DOWNLOAD_DIR"]
    DOCSFOLDER = _dirs["XDG_DOCUMENTS_DIR"]
except FileNotFoundError:
    DESKFOLDER = HOMEFOLDER + "Desktop"
    DOWNFOLDER = HOMEFOLDER + "Downloads"
    DOCSFOLDER = HOMEFOLDER + "Documents"

#Ниже указаны параметры, зависящие от ОС
try:
    _tmp = open("/etc/altlinux-release")
    OS = "altlinux"
    _tmp.close()
except FileNotFoundError:
    OS = check_output( "grep '^ID=' /etc/os-release; exit 0", shell=True, universal_newlines=True ).strip().split( '=' )[1]

if OS == "altlinux":
    #Версия и релиз приложения
    _package_info = check_output( "rpm -q myconnector 2>/dev/null; exit 0", shell=True, universal_newlines=True ).strip().split( '-' )
    try: RELEASE = _package_info[2].split('.')[0]
    except: RELEASE = "git"

    #Папка монтирования устройств
    _udisks2 = check_output( "/usr/sbin/control udisks2; exit 0", shell=True, universal_newlines=True ).strip()
    if _udisks2 == 'default':
        USBPATH = "/run/media/%s" % os.getenv( "USER" )
    else:
        USBPATH = "/media"

    #Команда проверки наличия в системе Citrix Receiver
    CITRIX_CHECK = "rpm -q ICAClient > "

    #FreeRDP: ключ проброса смарткарт
    SCARD = ' /smartcard:""'

elif OS == "linuxmint" or OS == "ubuntu":
    try:
        _package_install = check_output( "dpkg-query -s myconnector  2>/dev/null | head -2 | tail -1; exit 0",
                                         shell=True, universal_newlines=True ).strip().split( ' ' )[1]
    except IndexError: _package_install = 'deinstall'
    if _package_install == 'deinstall':
        RELEASE = "git"
    else:
        _package_info = check_output( "dpkg-query -W myconnector 2>/dev/null; exit 0",
                                      shell=True, universal_newlines=True ).strip().split( '\t' )
        try:
            _package_info = _package_info[1].split("-")
            RELEASE = _package_info[1]
        except IndexError: RELEASE = "git"

    USBPATH = "/media/%s" % os.getenv( "USER" )

    CITRIX_CHECK = "dpkg -s icaclient > "

    SCARD = ' /smartcard'

else:
    VERSION = RELEASE = USBPATH = CITRIX_CHECK = SCARD = ""
    err = Error( "%s: https://docs.myconnector.ru/." % _("Unsupported OS!\n"
                 "Some features of the program may not work!\nLearn more about supported OS") )
    err.run()

#Protocols' default options
DEF_PROTO = {}
#vncviewer
DEF_PROTO[ "VNC1" ] = {  "fullscreen"        : "False",
                         "viewonly"          : "False",
                         "listen"            : "False",
                         "listen_port"       : "",
                         "program"           : "vncviewer" }
#FreeRDP:
DEF_PROTO[ "RDP1" ] = {  "username"          : "",
                         "domain"            : "",
                         "fullscreen"        : "True",
                         "clipboard"         : "True",
                         "resolution"        : "",
                         "color"             : "32",
                         "folder"            : "",
                         "gserver"           : "",
                         "guser"             : "",
                         "gdomain"           : "",
                         "gpasswd"           : "",
                         "admin"             : "False",
                         "smartcards"        : "False",
                         "printers"          : "False",
                         "sound"             : "False",
                         "microphone"        : "False",
                         "multimon"          : "False",
                         "compression"       : "False",
                         "compr_level"       : "0",
                         "fonts"             : "False",
                         "aero"              : "False",
                         "drag"              : "False",
                         "animation"         : "False",
                         "theme"             : "False",
                         "wallpapers"        : "False",
                         "nsc"               : "False",
                         "jpeg"              : "False",
                         "jpeg_quality"      : "80.0",
                         "usb"               : "False",
                         "disable_nla"       : "True",
                         "workarea"          : "False",
                         "span"              : "False",
                         "desktop"           : "False",
                         "downloads"         : "False",
                         "documents"         : "False",
                         "gdi"               : "False",
                         "reconnect"         : "True",
                         "certignore"        : "True",
                         "passwdsave"        : "False",
                         "glyph"             : "False",
                         "userparams"        : "",
                         "security"          : "False",
                         "program"           : "freerdp" }
#Remmina
DEF_PROTO[ "RDP" ] = {   "username"          : "",
                         "domain"            : "",
                         "colordepth"        : "32",
                         "quality"           : "0",
                         "resolution"        : "",
                         "viewmode"          : "3",
                         "sharefolder"       : "",
                         "shareprinter"      : "0",
                         "disableclipboard"  : "0",
                         "sound"             : "off",
                         "sharesmartcard"    : "0" ,
                         "program"           : "remmina" }
DEF_PROTO[ "VNC" ] = {   "username"          : "",
                         "quality"           : "9",
                         "colordepth"        : "24",
                         "viewmode"          : "1",
                         "viewonly"          : "0",
                         "disableencryption" : "0",
                         "disableclipboard"  : "0",
                         "showcursor"        : "1",
                         "program"           : "remmina" }
DEF_PROTO[ "NX" ] = {    "username"          : "",
                         "quality"           : "0",
                         "resolution"        : "",
                         "viewmode"          : "1",
                         "nx_privatekey"     : "",
                         "disableencryption" : "0",
                         "disableclipboard"  : "0",
                         "exec"              : "" }
DEF_PROTO[ "XDMCP" ] = { "colordepth"        : "0",
                         "viewmode"          : "1",
                         "resolution"        : "",
                         "once"              : "0",
                         "showcursor"        : "0",
                         "exec"              : "" }
DEF_PROTO[ "SPICE" ] = { "usetls"            : "0",
                         "viewonly"          : "0",
                         "resizeguest"       : "0",
                         "disableclipboard"  : "0",
                         "sharesmartcard"    : "0",
                         "enableaudio"       : "0",
                         "cacert"            : "" ,
                         "program"           : "remmina" }
DEF_PROTO[ "SSH" ] = {   "username"          : "",
                         "ssh_auth"          : "0",
                         "ssh_privatekey"    : "",
                         "ssh_charset"       : "UTF-8",
                         "knocking"          : "",
                         "exec"              : "" }
DEF_PROTO[ "SFTP" ] = {  "username"          : "",
                         "ssh_auth"          : "0",
                         "ssh_privatekey"    : "",
                         "ssh_charset"       : "UTF-8",
                         "knocking"          : "",
                         "execpath"          : "/" }
#pyhoca-cli
DEF_PROTO[ "X2GO" ] = {  "username"          : "",
                         "session"           : "",
                         "port"              : "",
                         "geometry"          : "fullscreen",
                         "passwdsave"        : "False",
                         "printers"          : "False",
                         "sound"             : "False" }
#virtviewer
DEF_PROTO[ "SPICE1" ] = { "fullscreen"       : "False",
                          "program"          : "virtviewer" }

def config_init( global_enable = None ):
    """Initializing config"""
    global _config
    global _config_file
    global GLOBAL, CONFIG, CONFIGS

    global_conf_file = "/etc/%s/%s.conf" % ( APP, APP )
    if global_enable == None:
        GLOBAL = check_global( "system_config" )
    else:
        GLOBAL = True if global_enable else False
        if GLOBAL or ROOT:
            _config_file = _global_conf_file
            _config[ APP ][ "system_config" ] = str( GLOBAL )
        config_save()
    if GLOBAL or ROOT:
        _config_file = _global_conf_file
    else:
        _config_file = "%s/%s.conf" % ( USERFOLDER, APP )
    CONFIG, CONFIGS = config_read()

def config_save( default = False ):
    """Default config for MyConnector"""
    if default:
        _config[ APP ] = DEFAULT
        _config[ "vncviewer"     ] = DEF_PROTO[ "VNC1"   ].copy()
        _config[ "remmina_vnc"   ] = DEF_PROTO[ "VNC"    ].copy()
        _config[ "ssh"           ] = DEF_PROTO[ "SSH"    ].copy()
        _config[ "sftp"          ] = DEF_PROTO[ "SFTP"   ].copy()
        _config[ "remmina_rdp"   ] = DEF_PROTO[ "RDP"    ].copy()
        _config[ "nx"            ] = DEF_PROTO[ "NX"     ].copy()
        _config[ "xdmcp"         ] = DEF_PROTO[ "XDMCP"  ].copy()
        _config[ "remmina_spice" ] = DEF_PROTO[ "SPICE"  ].copy()
        _config[ "virtviewer"    ] = DEF_PROTO[ "SPICE1" ].copy()
        _config[ "freerdp"       ] = DEF_PROTO[ "RDP1"   ].copy()
        _config[ "x2go"          ] = DEF_PROTO[ "X2GO"   ].copy()
    with open( _config_file, 'w' ) as configfile:
        _config.write( configfile )

def config_read():
    """Parsing config file"""
    try:
        _config.read( _config_file )
        main = _config[ APP ]
        protocols = { "VNC1"   : _config[ "vncviewer"     ],
                      "VNC"    : _config[ "remmina_vnc"   ],
                      "RDP"    : _config[ "remmina_rdp"   ],
                      "RDP1"   : _config[ "freerdp"       ],
                      "NX"     : _config[ "nx"            ],
                      "XDMCP"  : _config[ "xdmcp"         ],
                      "SPICE"  : _config[ "remmina_spice" ],
                      "SPICE1" : _config[ "virtviewer"    ],
                      "SSH"    : _config[ "ssh"           ],
                      "SFTP"   : _config[ "sftp"          ],
                      "X2GO"   : _config[ "x2go"          ] }
        return main, protocols
    except:
        err = Error( _("The configuration file is corrupted or requires updating, a new one will be created!") )
        err.run()
        try:
            os.rename( _config_file, "%s.bak" % _config_file )
        except PermissionError:
            err = Error( _("Need root privileges!") )
            err.run()
            exit (1)
        config_save( default = True )
        _config.read( _config_file )
        return config_read()

if not os.path.exists( _config_file ):
    config_save( default = True )

config_init()
