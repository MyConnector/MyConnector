#!/usr/bin/python3
# -*- coding: utf-8 -*-

# MyConnector
# Copyright (C) 2014-2025 Evgeniy Korneechev <ek@myconnector.ru>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the version 2 of the GNU General
# Public License as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

import myconnector.options as options
from myconnector.config import *
from myconnector.config import _
from re import sub
from shlex import quote
try: import keyring
except Exception as error:
    class Keyring:
        def set_password(self, *args): pass
        def get_password(self, *args): return ""
    keyring = Keyring()
    options.log.warning("Python 3: %s. %s." % ( error, _("Password storage is not available for MyConnector") ) )

try: enableLog = CONFIG.getboolean( 'log' )
except KeyError: enableLog = DEFAULT[ 'log' ]
if enableLog and not check_global( "stealth_mode" ):
    STD_TO_LOG = ' >> ' + STDLOGFILE + " 2>&1 &"
else:
    STD_TO_LOG = ' &'

class VncViewer:
    """Класс для настройки VNC-соединения через VncViewer"""
    def start( self, args, window = False ):
        if type(args) == str:
            options.log.info( "VNC: %s %s", _("Connecting to the server"), args )
            command = 'vncviewer ' + args
            server = args
        else:
            for key in CONFIGS[ "VNC1" ]:
                if not key in args: args[ key ] = CONFIGS[ "VNC1" ][ key ]
            server = args[ "server" ]
            command = 'vncviewer %s ' % server
            if args.get( "fullscreen", "False" ) == "True": command += "-fullscreen "
            if args.get( "viewonly", "False"   ) == "True": command += "-viewonly "
            if args.get( "listen", "False"     ) == "True":
                command = "vncviewer -listen %s" % args.get( "listen_port", "" )
        options.log.info( "VNC: %s %s. %s:", _("Connecting to the server"), server, _("Launch Command") )
        options.log.info( command )
        os.system(command + STD_TO_LOG)

class XFreeRdp:
    """Класс для настройки RDP-соединения через xfreerdp"""
    def start( self, args, window = False ):
        if XFREERDP:
            freerdpVersion = freerdpCheckVersion()
            if freerdpVersion >= "3.0.0":
                glyph      = " /cache:glyph:on"
                secnla     = " /sec:nla:off"
                sertignore = " /cert:ignore"
                gateway    = " /gateway:g:"
                gateway_u  = " /gateway:u:"
                gateway_d  = " /gateway:d:"
                gateway_p  = " /gateway:p:"
            else:
                glyph      = " +glyph-cache"
                secnla     = " -sec:-nla"
                sertignore = " /cert-ignore"
                gateway    = " /g:"
                gateway_u  = " /gu:"
                gateway_d  = " /gd:"
                gateway_p  = " /gp:"
            if freerdpVersion > "1.2":
                for key in CONFIGS[ "RDP1" ]:
                    if not key in args: args[ key ] = CONFIGS[ "RDP1" ][ key ]
                server   = args[ "server" ]
                username = args.get( "username" , "" )
                command  = "%s /v:%s /t:'%s' /u:%s" % ( XFREERDP_PATH, server, args.get( "name", server ), quote( username ) )
                if args.get( "domain" , ""                    ): command += " /d:%s" % args[ "domain" ]
                if args.get( "fullscreen", "True"   ) == "True":
                    if freerdpCheckFloatbar(): command += " /f /floatbar:sticky:off,show:always"
                    else: command += " /f"
                if args.get( "clipboard" , "True"   ) == "True": command += " +clipboard"
                if args.get( "resolution" , ""                ): command += " /size:%s" % args[ "resolution" ]
                if args.get( "color" , ""                     ): command += " /bpp:%s" % args[ "color" ]
                if args.get( "folder" , ""                    ): command += " /drive:SharedFolder,'%s'" % args[ "folder" ]
                if args.get( "gserver" , ""                   ): command += "%s%s" % ( gateway, args[ "gserver" ] )
                if args.get( "guser" , ""                     ): command += "%s%s" % ( gateway_u, args[ "guser" ] )
                if args.get( "gdomain" , ""                   ): command += "%s%s" % ( gateway_d, args[ "gdomain" ] )
                if args.get( "gpasswd" , ""                   ): command += "%s%s" % ( gateway_p, quote( args[ "gpasswd" ] ) )
                if args.get( "admin", "False"       ) == "True": command += " /admin"
                if args.get( "smartcards", "False"  ) == "True": command += SCARD
                if args.get( "printers", "False"    ) == "True": command += " /printer"
                if args.get( "sound", "False"       ) == "True": command += " /sound:sys:alsa"
                if args.get( "microphone", "False"  ) == "True": command += " /microphone:sys:alsa"
                if args.get( "multimon", "False"    ) == "True": command += " /multimon"
                if args.get( "compression", "False" ) == "True": command += " +compression /compression-level:%s" % args.get( "compr_level" , "0" )
                if args.get( "fonts", "False"       ) == "True": command += " +fonts"
                if args.get( "aero", "False"        ) == "True": command += " +aero"
                if args.get( "drag", "False"        ) == "True": command += " +window-drag"
                if args.get( "animation", "False"   ) == "True": command += " +menu-anims"
                if args.get( "theme", "False"       ) =="False": command += " -themes"
                if args.get( "wallpapers", "False"  ) =="False": command += " -wallpaper"
                if args.get( "nsc", "False"         ) == "True": command += " /nsc"
                if args.get( "jpeg", "False"        ) == "True": command += " /jpeg /jpeg-quality:%s" % args.get( "jpeg_quality" , "80.0" )
                if args.get( "usb", "False"         ) == "True" and os.path.exists( USBPATH ):
                    command += " /drive:MEDIA,%s" % USBPATH
                if args.get( "workarea", "False"    ) == "True": command += " /workarea"
                if args.get( "span", "False"        ) == "True": command += " /span"
                if args.get( "desktop" , "False"    ) == "True": command += " /drive:Desktop,%s" % DESKFOLDER
                if args.get( "downloads" , "False"  ) == "True": command += " /drive:Downloads,%s" % DOWNFOLDER
                if args.get( "documents" , "False"  ) == "True": command += " /drive:Documents,%s" % DOCSFOLDER
                if args.get( "gdi", "False"         ) == "True": command += " /gdi:hw"
                else: command += " /gdi:sw"
                if args.get( "certignore", "True"   ) == "True": command += sertignore
                if args.get( "reconnect", "True"    ) == "True": command += " +auto-reconnect"
                if args.get( "glyph", "False"       ) == "True": command += glyph
                if args.get( "userparams" , ""                ): command += " %s" % args[ "userparams" ]
                disable_nla = args.get( "disable_nla", "True" )
                if disable_nla == "True"                       : command += secnla
                security = args.get( "security", "False" )
                if security != "False":
                    command += " /sec:%s" % security
                password = args.get( "passwd" , "" )
                options.log.info( "FreeRDP: %s %s. %s:", _("Connecting to the server"), server, _("Launch Command") )
                options.log.info( command )
                if not password:
                    try:
                        password = keyring.get_password( server, username )
                    except Exception as e:
                        options.log.error( e )
                        password = ""
                if not password and disable_nla != "True":
                    new_username, password = passwd( server, username, args.get( "file", "" ), window )
                    if new_username == username or not new_username:
                        pass
                    else:
                        command = command.replace( "/u:%s" % quote( username ), "/u:%s" % quote( new_username ) )
                        if "@" in new_username or "\\" in new_username:
                             command = command.replace( "/d:%s" % args[ "domain" ], "" )
                if password:
                    command += " /p:%s" % quote( password )
                if password == "" or password == None:
                    command += " /p:" #support empty password
                if password != False: #if there is password
                    os.system(command + STD_TO_LOG)
                    if enableLog and not check_global( "stealth_mode" ):
                        signal.signal( signal.SIGCHLD, signal.SIG_IGN ) # without zombie
                        Popen( [ MAINFOLDER + "/myconnector-check-xfreerdp-errors" ] )
            else:
                options.msg_error ( "%s FreeRDP (%s) %s!" % ( _("Version"),
                                    freerdpVersion, _("does not meet the minimum requirements") ), options.log.warning )
        else:
            options.msg_error ( "FreeRDP %s!" % _("not installed"), options.log.warning )

class Remmina:
    """Connection via Remmina"""
    cfg = {}
    f_name = ".tmp.remmina"
    def create_cfg_file( self, args ):
        """Create configuration file for connect"""
        server, login = options.searchSshUser( args[ "server" ] )
        args[ "server" ] = server
        if login: args[ "username" ] = login
        args[ "ssh_username" ] = args.get( "username" , "" )
        self.cfg[ "name" ] += args.get( "name" , server )
        f = open( "%s/%s" % ( WORKFOLDER, self.f_name ), "w" )
        f.write( "[remmina]\n" )
        protocol = args[ "protocol" ].upper()
        for key in self.cfg.keys():
            default = CONFIGS[ protocol ][ key ] if key in CONFIGS[ protocol ] else self.cfg[ key ]
            self.cfg[ key ] = args.get( key, default )
            if key == "protocol": self.cfg[ key ] = protocol
            print( key, self.cfg[ key ], sep = "=", file = f )
        f.close()

    def start( self, parameters, window = False ):
        """Run connection via Remmina"""
        self.create_cfg_file( parameters )
        options.log.info( "Remmina: %s %s %s: %s", _("connecting via the protocol"), self.cfg[ "protocol" ],
                           _("to the server"), self.cfg[ "server" ] )
        knock = parameters.get( "knocking", "" )
        if knock:
            cmd = "knock %s %s" % ( sub( ":.*", "", parameters[ "server" ] ), knock )
            options.log.info( cmd )
            os.system( "%s%s" % ( cmd, STD_TO_LOG ) )
        command = "remmina -c \"%s/%s\"" % ( WORKFOLDER, self.f_name )
        options.log.info( command )
        os.system( "cd $HOME && %s%s" % ( command, STD_TO_LOG ) )

class RdpRemmina( Remmina ):
    """Remmina RDP connection"""
    def __init__( self ):
        self.cfg = { "disableclipboard"       : "0",
                     "clientname"             : "",
                     "quality"                : "0",
                     "console"                : "0",
                     "sharesmartcard"         : "0",
                     "resolution"             : "",
                     "group"                  : "",
                     "password"               : "",
                     "name"                   : "RDP-connection: ",
                     "shareprinter"           : "0",
                     "security"               : "",
                     "protocol"               : "RDP",
                     "execpath"               : "",
                     "disablepasswordstoring" : "1",
                     "sound"                  : "off",
                     "username"               : "",
                     "sharefolder"            : "",
                     "domain"                 : "",
                     "viewmode"               : "3",
                     "server"                 : "",
                     "colordepth"             : "32",
                     "window_maximize"        : "1",
                     "window_width"           : "800",
                     "window_height"          : "600",
                     "exec"                   : "" }
        self.f_name = ".tmp_RDP.remmina"

class VncRemmina( Remmina ):
    """Remmina VNC connection"""
    def __init__( self ):
        self.cfg = { "keymap"                 : "",
                     "quality"                : "9",
                     "disableencryption"      : "0",
                     "colordepth"             : "24",
                     "hscale"                 : "0",
                     "group"                  : "",
                     "password"               : "",
                     "name"                   : "VNC-connection: ",
                     "viewonly"               : "0",
                     "disableclipboard"       : "0",
                     "protocol"               : "VNC",
                     "vscale"                 : "0",
                     "username"               : "",
                     "disablepasswordstoring" : "1",
                     "showcursor"             : "0",
                     "disableserverinput"     : "0",
                     "server"                 : "",
                     "aspectscale"            : "0",
                     "window_maximize"        : "1",
                     "window_width"           : "800",
                     "window_height"          : "600",
                     "viewmode"               : "1" }
        self.f_name = ".tmp_VNC.remmina"

class NxRemmina( Remmina ):
    """Remmina NX connection"""
    def __init__( self ):
        self.cfg = { "name"                   : "NX-connection: ",
                     "protocol"               : "NX",
                     "quality"                : "0",
                     "server"                 : "",
                     "disableencryption"      : "0",
                     "resolution"             : "",
                     "group"                  : "",
                     "password"               : "",
                     "username"               : "",
                     "NX_privatekey"          : "",
                     "showcursor"             : "0",
                     "disableclipboard"       : "0",
                     "window_maximize"        : "1",
                     "window_width"           : "800",
                     "window_height"          : "600",
                     "viewmode"               : "4",
                     "disablepasswordstoring" : "1",
                     "exec"                   : "" }
        self.f_name = ".tmp_NX.remmina"

class XdmcpRemmina( Remmina ):
    """Remmina XDMCP connection"""
    def __init__( self ):
        self.cfg = { "resolution"             : "",
                     "group"                  : "",
                     "password"               : "",
                     "name"                   : "XDMCP-connection: ",
                     "protocol"               : "XDMCP",
                     "once"                   : "0",
                     "showcursor"             : "0",
                     "server"                 : "",
                     "colordepth"             : "0",
                     "window_maximize"        : "1",
                     "viewmode"               : "1",
                     "window_width"           : "800",
                     "window_height"          : "600",
                     "disablepasswordstoring" : "1",
                     "exec"                   : "" }
        self.f_name = ".tmp_XDMCP.remmina"

class SftpRemmina( Remmina ):
    """Remmina SFTP connection"""
    def __init__( self ):
        self.cfg = { "name"                   : "SFTP-connection: ",
                     "protocol"               : "SFTP",
                     "ssh_auth"               : "0",
                     "ssh_charset"            : "UTF-8",
                     "ssh_privatekey"         : "",
                     "username"               : "",
                     "ssh_username"           : "",
                     "group"                  : "",
                     "password"               : "",
                     "execpath"               : "/",
                     "server"                 : "",
                     "window_maximize"        : "0",
                     "window_height"          : "600",
                     "window_width"           : "800",
                     "ftp_vpanedpos"          : "360",
                     "viewmode"               : "0",
                     "disablepasswordstoring" : "1" }
        self.f_name = ".tmp_SFTP.remmina"

class SshRemmina( Remmina ):
    """Remmina SSH connection"""
    def __init__( self ):
        self.cfg = { "name"                   : "SSH-connection: ",
                     "protocol"               : "SSH",
                     "ssh_auth"               : "0",
                     "ssh_charset"            : "UTF-8",
                     "ssh_privatekey"         : "",
                     "group"                  : "",
                     "password"               : "",
                     "username"               : "",
                     "ssh_username"           : "",
                     "server"                 : "",
                     "window_maximize"        : "0",
                     "window_width"           : "500",
                     "window_height"          : "500",
                     "viewmode"               : "0",
                     "disablepasswordstoring" : "1",
                     "exec"                   : "" }
        self.f_name = ".tmp_SSH.remmina"

class SpiceRemmina( Remmina ):
    """Remmina SPICE connection"""
    def __init__( self ):
        self.cfg = { "name"                   : "SPICE-connection: ",
                     "protocol"               : "SPICE",
                     "ssh_auth"               : "0",
                     "disableclipboard"       : "0",
                     "ssh_privatekey"         : "",
                     "usertls"                : "0",
                     "ssh_username"           : "",
                     "enableaudio"            : "0",
                     "password"               : "",
                     "cacert"                 : "",
                     "server"                 : "",
                     "ssh_loopback"           : "0",
                     "resizeguest"            : "0",
                     "sharesmartcard"         : "0",
                     "ssh_server"             : "",
                     "viewonly"               : "0",
                     "disablepasswordstoring" : "1" }
        self.f_name = ".tmp_SPICE.remmina"

class Vmware:
    """Класс для настройки соединения к VMWare серверу"""
    def start( self, args, window = False ):
        if vmwareCheck():
            if type(args) == str:
                command = 'vmware-view -q -s ' + args
                options.log.info( "VMware: %s %s", _("Connecting to the server"), args )
                options.log.info( command )
            else:
                command = 'vmware-view -q -s %s' %  args[ "server" ]
                if args.get( "username", "" ): command += " -u %s" % args[ "username" ]
                if args.get( "domain",   "" ): command += " -d %s" % args[ "domain"   ]
                if args.get( "fullscreen", "False" ) == "True": command += " --fullscreen"
                options.log.info( "VMware:  %s %s", _("Connecting to the server"), args[ "server" ] )
                options.log.info( command )
                if args.get( "passwd",   "" ): command += " -p %s" % quote( args[ "passwd" ] )
            os.system(command + STD_TO_LOG)
        else:
            options.msg_error( "VMware Horizon Client %s!" % _("not installed"), options.log.warning )

def _missCitrix():
    """Message for user, if Citrix Receiver not installed"""
    options.msg_error( "Citrix Receiver/Workspace %s!" % _("not installed"), options.log.warning )

class Citrix:
    """Класс для настройки ICA-соединения к Citrix-серверу"""
    def start( self, args, window = False ):
        if type(args) == str:
            addr = args
        else:
            addr = args [ "server" ]
        if citrixCheck():
            options.log.info( "Citrix: %s %s", _("Connecting to the server"), addr )
            os.system( "/opt/Citrix/ICAClient/util/storebrowse --addstore " + addr + STD_TO_LOG.replace( "&", "" ) )
            os.system('/opt/Citrix/ICAClient/selfservice --icaroot /opt/Citrix/ICAClient' + STD_TO_LOG)
        else: _missCitrix()

    def preferences():
        if citrixCheck():
            options.log.info( "Citrix: %s." % _("Opening the program settings") )
            os.system('/opt/Citrix/ICAClient/util/configmgr --icaroot /opt/Citrix/ICAClient' + STD_TO_LOG)
        else: _missCitrix()

class Web:
    """Класс для настройки подключения к WEB-ресурсу"""
    def start(self, args, window = False ):
        if type(args) == str:
            addr = args
        else:
            addr = args [ "server" ]
        if  not addr.find("://") != -1:
            addr = "http://" + addr
        command = 'xdg-open "' + addr + '"'
        options.log.info( "WWW: %s %s", _("Opening a web resource"), addr )
        options.log.info( command )
        os.system ( command + STD_TO_LOG)

class FileServer:
    """Класс для настройки подключения к файловому серверу"""
    def start( self, args, window = False ):
        _exec = CONFIG.get( "fs", "xdg-open" )
        if not _exec: _exec = "xdg-open"
        _exec += ' "'
        if type(args) == str:
            command = _exec + args + '"'
            server = args
        else:
            try:
                protocol, server = args[ "server" ].split("://")
            except:
                server = args[ "server" ]
                try:
                    protocol = args[ "type" ]
                except KeyError:
                    options.msg_error( _("The FS connection configuration file is corrupted - the type is missing!"), options.log.exception )
                    return 1
            command = _exec + protocol + "://"
            if args.get( "domain" , "" ): command += "%s;" % args[ "domain" ]
            if args.get( "user" , ""   ): command += "%s@" % args[ "user" ]
            command += server
            if args.get( "folder" , "" ): command += "/%s" % args[ "folder" ]
            command += '"'
            if protocol == "file":
                command = '%s%s"' % ( _exec, args.get( "folder" , "" ))
        options.log.info( "%s %s. %s:", _("Connecting to a file server"), server, _("Launch Command") )
        options.log.info( command )
        os.system (command + STD_TO_LOG)

class X2goClient:
    """Class for connect to X2GO server"""
    def start( self, args, window = False ):
        if x2goCheck():
            if type(args) == str:
                command = "pyhoca-cli -N --add-to-known-hosts --server %s" % args
                options.log.info( "X2GO: %s %s", _("Connecting to the server"), args )
                options.log.info( command )
            else:
                server = args[ "server" ]
                username = args.get( "username", "" )
                command = "pyhoca-cli -N --add-to-known-hosts --server %s" % server
                if username: command += " --user %s" % args[ "username" ]
                if args.get( "port",     "22"   ): command += " --port %s" % args[ "port" ]
                if args.get( "session",  "MATE" ): command += " --command %s" % args[ "session" ]
                geometry = args.get( "geometry", "fullscreen" )
                if geometry: command += " --geometry %s" % args[ "geometry" ]
                if args.get( "printers", "False" ) == "True": command += " --printing"
                if args.get( "sound", "False"    ) == "True": command += " --sound pulse"
                options.log.info( "X2GO: %s %s. %s:", _("Connecting to the server"), server, _("Launch Command") )
                options.log.info( command )
                password = args.get( "passwd", "" )
                if not password:
                    try:
                        password = keyring.get_password( server, username )
                    except Exception as e:
                        options.log.error( e )
                        password = ""
                if password:
                    password = quote( password )
                else:
                    new_username, password = passwd( server, username, args.get( "file", "" ), window )
                    if new_username == username or not new_username:
                        pass
                    else:
                        command = command.replace( "--user %s" % username, "--user %s" % new_username )
                command += " --password %s" % password
            if password != False: #if there is not password
                os.system( command + STD_TO_LOG )
                if enableLog and not check_global( "stealth_mode" ):
                    signal.signal( signal.SIGCHLD, signal.SIG_IGN ) # without zombie
                    Popen( [ MAINFOLDER + "/myconnector-check-x2go-errors" ] )
        else:
            options.msg_error ( _("The 'pyhoca-cli' client for X2GO is not installed!"), options.log.warning )

class VirtViewer:
    """Class for connect to SPICE server"""
    def start( self, args, window = False ):
        if virtvCheck():
            if type(args) == str:
                command = "remote-viewer -v spice://%s" % args
                options.log.info( "SPICE: %s %s", _("Connecting to the server"), args )
                options.log.info( command )
            else:
                server = args[ "server" ]
                command = "remote-viewer -v spice://%s --title %s" %  ( server, args.get( "name", server ) )
                if args.get( "fullscreen", "False" ) == "True": command += " --full-screen"
                options.log.info( "SPICE:  %s %s", _("Connecting to the server"), server )
                options.log.info( command )
            os.system(command + STD_TO_LOG)
        else:
            options.msg_error ( _("The 'remote-viewer' client for SPICE is not installed!"), options.log.warning )

class Terminal:
    """Class for connect to SSH server"""
    def start( self, args, window = False ):
        _exec = CONFIG.get( "ssh_terminal", "x-emulator-terminal" )
        server, login = options.searchSshUser( args[ "server" ] )
        try:
            server, port = server.split(":")
        except:
            port = ""
        command = "%s -t \"%s\" -e \"ssh %s" %  ( _exec, args.get( "name", server ), server )
        user = args.get( "username" , ""   ) if not login else login
        if user: command += " -l%s" % user
        if port: command += " -p%s" % port
        knock = args.get( "knocking", "" )
        if knock:
            cmd = "knock %s %s" % ( sub( ":.*", "", server ), knock )
            options.log.info( cmd )
            os.system( "%s%s" % ( cmd, STD_TO_LOG ) )
        command += "\""
        options.log.info( "SSH:  %s %s", _("Connecting to the server"), server )
        options.log.info( command )
        os.system(command + STD_TO_LOG)

def definition( name ):
    """Функция определения протокола"""
    protocols = { "VNC"    : VncRemmina(),
                  "VNC1"   : VncViewer(),
                  "RDP"    : RdpRemmina(),
                  "RDP1"   : XFreeRdp(),
                  "NX"     : NxRemmina(),
                  "XDMCP"  : XdmcpRemmina(),
                  "SSH"    : SshRemmina(),
                  "SSH1"   : Terminal(),
                  "SFTP"   : SftpRemmina(),
                  "VMWARE" : Vmware(),
                  "CITRIX" : Citrix(),
                  "WEB"    : Web(),
                  "SPICE"  : SpiceRemmina(),
                  "SPICE1" : VirtViewer(),
                  "FS"     : FileServer(),
                  "X2GO"   : X2goClient() }
    if name in protocols:
        return protocols[ name ]
    else:
        return None

def citrixCheck():
    """Фунцкия проверки наличия в системе Citrix Receiver"""
    check = int( check_output( "%s/dev/null 2>&1; echo $?" % CITRIX_CHECK, shell=True, universal_newlines=True ).strip() )
    check = not bool(check)
    return check

def vmwareCheck():
    """Фунцкия проверки наличия в системе VMware Horizon Client"""
    check = int( check_output( "which vmware-view > /dev/null 2>&1; echo $?", shell=True, universal_newlines=True ).strip() )
    check = not bool(check)
    return check

def x2goCheck():
    """Checking exist pyhoca-cli"""
    check = int( check_output( "which pyhoca-cli > /dev/null 2>&1; echo $?", shell=True, universal_newlines=True ).strip() )
    check = not bool(check)
    return check

def virtvCheck():
    """Checking exist remote-viewer"""
    check = int( check_output( "which remote-viewer > /dev/null 2>&1; echo $?", shell=True, universal_newlines=True ).strip() )
    check = not bool(check)
    return check

def freerdpCheckVersion():
    """Фунцкия определения версии FreeRDP"""
    version = check_output( "%s /version; exit 0" % XFREERDP_PATH, shell=True, universal_newlines=True ).strip().split( '\t' )
    version = version[0].split(" "); version = version[4].split("-")[0];
    return version

def freerdpCheckFloatbar():
    """Checking for existence /floatbar in FreeRDP"""
    check = int( check_output( "%s --help | grep floatbar > /dev/null; echo $?" % XFREERDP_PATH, shell=True, universal_newlines=True ).strip() )
    check = not bool(check)
    return check

def passwd( server, username, filename, window = False):
    """Authentication window"""
    from myconnector.dialogs import Password
    dialog = Password( username, window )
    username, password, save = dialog.run()
    if password == False:
        options.log.info( _("The connection was canceled by the user!") )
    else:
        if save and password:
            try:
                keyring.set_password( str( server ), str( username ), str( password ) )
            except Exception as e:
                options.log.error( e )
            resaveFromAuth( filename, username )
    return( username, password )

def resaveFromAuth( filename, username ):
    """Resave connection from Authentication Window"""
    try:
        connection = "%s/%s" % ( WORKFOLDER, filename )
        conf = ConfigParser( interpolation = None )
        conf.read( connection )
        conf[ "myconnector" ][ "domain" ] = ""
        conf[ "myconnector" ][ "username" ] = username
        with open( connection, "w" ) as fileMyc:
            conf.write( fileMyc )
    except Exception as e:
        options.log.error( e )

if __name__ == "__main__":
    pass
