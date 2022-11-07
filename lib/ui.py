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

from gi.repository import ( Gtk,
                            Gdk,
                            GdkPixbuf,
                            GLib,
                            Gio )
from myconnector.connector import *
from myconnector.config import *
from myconnector.config import _

def viewStatus(bar, message):
    """Функция отображения происходящих действий в строке состояния"""
    bar.push(bar.get_context_id ("statusbar"), message)

def connectFile(filename, openFile = False):
    """Connect to the server with file .myc"""
    try:
        parameters = options.loadFromFile(filename)
        if parameters != None:
            protocol = parameters[ "protocol" ]
            program  = parameters.get( "program", "" )
            if program == "freerdp":
                try:
                    parameters[ "passwd" ] = keyring.get_password( parameters[ "server" ] ,parameters[ "username" ] )
                except Exception as e:
                    options.log.error( e )
                    password = ""
            connect = definition( changeProgram( protocol, program ) )
            if connect:
                if parameters.get( "server", "" ):
                    connect.start( parameters )
                else:
                    options.msg_error( _("Server not specified!"), options.log.error )
            else:
                options.msg_error( "%s: %s" % ( _("Unsupported protocol"), protocol ), options.log.error )
    except KeyError:
        options.msg_error( "%s %s: %s." % ( _("Error in the file"), filename.replace( "tmp_", "" ),
                           _("protocol not specified") ),  options.log.exception )

def connectFileRdp(filename):
    """Connect to the server with file .rdp"""
    if CONFIG[ "rdp" ] == "freerdp":
        tmpfile =  "%s/.tmp.rdp" % WORKFOLDER
        os.system('cp -r "%s" "%s"' % (filename, tmpfile))
        os.system('xfreerdp "%s" -sec-nla %s' % (tmpfile, STD_TO_LOG))
    else:
        os.system('remmina --connect "%s" %s' % (filename, STD_TO_LOG))

def connectFileRemmina(filename):
    """Connect to the server with file .remmina"""
    os.system('remmina --connect "%s" %s' % (filename, STD_TO_LOG))

def openFile(filename):
    """Open file connection (.myc, .rdp or .remmina)"""
    ext = Path(filename).suffix.lower()
    options.log.info( "%s %s" % ( _("The file opens"), filename ) )
    if ext == ".myc":
        tmpname = 'tmp_' + os.path.basename(filename)
        os.system('cp "%s" "%s/%s"' % (filename, WORKFOLDER, tmpname))
        os.chdir( WORKFOLDER )
        connectFile(tmpname, True)
        os.remove(tmpname)
    elif ext == ".rdp": connectFileRdp(filename)
    elif ext == ".remmina": connectFileRemmina(filename)
    elif ext == ".ctor":
        options.msg_error( _("Outdated format file! Use 'ctor2myc' or 'Import' from menu."), options.log.error )
    else: options.msg_error( _("Unsupported file type!"), options.log.error )

def initSignal(gui):
    """Функция обработки сигналов SIGHUP, SIGINT и SIGTERM
       SIGINT - KeyboardInterrupt (Ctrl+C)
       Thanks: http://stackoverflow.com/questions/26388088/python-gtk-signal-handler-not-working/26457317#26457317"""
    def install_glib_handler(sig):
        unix_signal_add = None

        if hasattr(GLib, "unix_signal_add"):
            unix_signal_add = GLib.unix_signal_add
        elif hasattr(GLib, "unix_signal_add_full"):
            unix_signal_add = GLib.unix_signal_add_full

        if unix_signal_add:
            unix_signal_add(GLib.PRIORITY_HIGH, sig, gui.onDeleteWindow, sig)
        else:
            print("Can't install GLib signal handler, too old gi.")

    SIGS = [getattr(signal, s, None) for s in "SIGINT SIGTERM SIGHUP".split()]
    for sig in filter(None, SIGS):
        GLib.idle_add(install_glib_handler, sig, priority=GLib.PRIORITY_HIGH)

def startDebug():
    """Start show log files online (uses xterm)"""
    if options.enableLog and not check_global( "stealth_mode" ):
        os.system( 'for i in all myconnector; do xterm -T "MyConnector DEBUG - $i.log" -e "tail -f %s/$i.log" & done' % LOGFOLDER )
        options.log.info( _("The program is running in debug mode.") )
    else:
        print ( _("Logging is disabled. Debugging is not possible!") )

def quitApp():
    """Quit application"""
    options.log.info ( _("The MyConnector is forcibly closed (from cmdline).") )
    os.system( "pkill [my]?connector" )

def getSaveConnections( fileFromConnection = "" ):
    """List of save connections from files in WORKFOLDER"""
    saves  = []
    groups = []
    image = Gtk.Image()
    image.new_from_icon_name( APP, 1 )
    for mycfile in os.listdir( WORKFOLDER ):
        if mycfile != fileFromConnection: # pass editing file
            if Path( mycfile ).suffix.lower() == ".myc":
                conf = ConfigParser( interpolation = None )
                try:
                    conf.read( "%s/%s" % ( WORKFOLDER, mycfile ) )
                    name     = conf[ "myconnector" ].get( "name",  "" )
                    group    = conf[ "myconnector" ].get( "group", "" )
                    protocol = conf[ "myconnector" ][ "protocol" ].upper()
                    if check_global( "stealth_mode") and not ROOT:
                        server = protocol = group = ""
                        icon = image.get_pixbuf()
                    else:
                        server = conf[ "myconnector" ][ "server" ]
                        icon = GdkPixbuf.Pixbuf.new_from_file( "%s/%s.png" % ( ICONFOLDER, protocol ) )
                    if not name: name = mycfile
                    save = [ name, group, protocol, server, mycfile, icon ]
                    saves.append( save )
                    if group: groups.append( group )
                except Exception as e:
                    options.log.error( e )
    return saves, list( set( groups ) ) #unique groups

def changeProgram( protocol, program = "" ):
    """Return {RDP,VNC,SPICE}1 if program not remmina"""
    protocol = protocol.upper()
    if program:
        if program in [ "freerdp", "vncviewer", "virtviewer" ]:
            return "%s1" % protocol
        else: return protocol
    try:
        if CONFIG[ protocol ] != "remmina" and protocol != "FS": protocol += "1"
    except KeyError: pass
    return protocol

def protocol_not_found( name ):
    options.msg_error( "%s ('%s') - %s!" % ( _("The connection configuration file is corrupted"), name,
                       _("the protocol is missing") ), options.log.exception )

def server_not_found( name ):
    options.msg_error( "%s ('%s') - %s!" % ( _("The connection configuration file is corrupted"), name,
                       _("the server is missing") ), options.log.exception )

def editConfig():
    "Editing program settings from CLI"
    if check_global( "system_config" ) and not ROOT:
        print( _("Access denied!") )
        return 126
    if ROOT:
        config = "/etc/%s/%s.conf" % ( APP, APP )
    else:
        config = "%s/%s.conf" % ( USERFOLDER, APP )
    with open( config ) as f:
        current = f.read()
    editor = os.getenv( "EDITOR" )
    if not editor: editor = os.getenv( "VISUAL" )
    if not editor: editor = "vi"
    OK = False
    while not OK:
        res = os.system( "%s %s" % ( editor, config ) )
        with open( config ) as f:
            result = f.read()
        if current == result:
            print( _("Config file has not been changed.") )
            OK = True
        else:
            _config = ConfigParser( interpolation = None )
            try:
                text = _("Config file has been changed")
                _config.read( config )
                tmp = _config[ APP ]
                OK = True
                print( "%s." % text )
                options.log.info( "%s %s." % ( text, _("from CLI") ) )
            except:
                text = "%s, %s" % ( text, _("but contains errors! Press any key to fix it...") )
                os.system( "read -s -n 1 -p \"%s\"; echo" % text )
    return res

class TrayIcon:
    """Класс, описывающий индикатор и меню в трее (пока только для MATE)
       Thanks: https://eax.me/python-gtk/"""
    def __init__(self, icon, menu):
        self.menu = menu
        self.ind = Gtk.StatusIcon()
        self.ind.set_from_icon_name(icon)
        self.ind.connect('popup-menu', self.onTrayMenu)
        self.ind.set_tooltip_text( "%s MyConnector" % _("Program") )

    def onTrayMenu(self, icon, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon,
                        button, time)

    def connect(self, callback):
        self.ind.connect('activate', callback)

    def hide(self):
        self.ind.set_visible(False)

    def show(self):
        self.ind.set_visible(True)

class Gui(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="ru.myconnector.MyConnector", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.prefClick = False
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain( APP )
        self.builder.add_from_file( "%s/gui.ui" % UIFOLDER )
        self.conn_note = self.builder.get_object( "list_connect" )
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("main_window")
        self.window.set_title( "MyConnector" )
        self.statusbar = self.builder.get_object("statusbar")
        self.liststore = { "RDP"    : self.builder.get_object( "liststore_RDP"    ),
                           "VNC"    : self.builder.get_object( "liststore_VNC"    ),
                           "SSH"    : self.builder.get_object( "liststore_SSH"    ),
                           "SFTP"   : self.builder.get_object( "liststore_SFTP"   ),
                           "VMWARE" : self.builder.get_object( "liststore_VMWARE" ),
                           "CITRIX" : self.builder.get_object( "liststore_CITRIX" ),
                           "XDMCP"  : self.builder.get_object( "liststore_XDMCP"  ),
                           "NX"     : self.builder.get_object( "liststore_NX"     ),
                           "WEB"    : self.builder.get_object( "liststore_WEB"    ),
                           "SPICE"  : self.builder.get_object( "liststore_SPICE"  ),
                           "FS"     : self.builder.get_object( "liststore_FS"     ),
                           "X2GO"   : self.builder.get_object( "liststore_X2GO"   ) }

        self.liststore_connect = Gtk.ListStore( str, str, str, str, str, GdkPixbuf.Pixbuf )
        self.setSavesToListstore()
        self.filterConnections = self.liststore_connect.filter_new()
        self.filterConnections.set_visible_func(self.listFilter) #добавление фильтра для поиска
        self.currentFilter = ''
        self.sortedFiltered = Gtk.TreeModelSort(model = self.filterConnections)
        try: default_sort = int( CONFIG[ 'sort' ] )
        except KeyError: default_sort = 0
        self.sortedFiltered.set_sort_column_id(default_sort, Gtk.SortType.ASCENDING)
        self.treeview = self.builder.get_object("treeview_connections")
        self.treeview.set_model(self.sortedFiltered)
        self.treeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE)
        self.treeview.connect("drag-data-get", self.onDragLabel)
        self.treeview.drag_source_add_uri_targets()
        if FIRSTRUN:
            connections = "%s/.connector/connections.db" % HOMEFOLDER
            if os.path.exists( connections ):
                if os.path.getsize( connections ):
                    self.importFromConnector( connections )
        self.getServersFromDb()
        try: default_tab = CONFIG[ 'tab' ]
        except KeyError: default_tab = '0'
        self.combo_protocols = self.builder.get_object( "combo_protocols" )
        self.combo_protocols.set_active_id( default_tab )
        self.conn_note.set_current_page(int(default_tab))
        self.labelRDP   = self.builder.get_object( "label_default_RDP"   )
        self.labelVNC   = self.builder.get_object( "label_default_VNC"   )
        self.labelSPICE = self.builder.get_object( "label_default_SPICE" )
        self.labelFS    = self.builder.get_object( "label_default_FS"    )
        self.initLabels( self.labelRDP, self.labelVNC, self.labelFS, self.labelSPICE )
        self.trayDisplayed = False
        self.tray_submenu = self.builder.get_object( "tray_submenu"                )
        self.recent_menu  = self.builder.get_object( "menu_file_recent_conn_list"  )
        recent_files      = self.builder.get_object( "menu_file_recent_files_list" )
        if check_global( "system_folder" ):
            recent_files.set_sensitive( False )
        self.initRecentMenu()
        if check_option( 'tray' ): self.trayDisplayed = self.initTray()
        if check_option( 'check_version' ):
            signal.signal( signal.SIGCHLD, signal.SIG_IGN ) # without zombie
            Popen( [ "%s/myconnector-check-version" % MAINFOLDER, VERSION ] )
        try:
            from myconnector.kiosk import enabled
            self.menu_kiosk = self.builder.get_object("menu_file_kiosk")
            self.menu_kiosk.set_sensitive( enabled() )
        except ImportError:
            options.log.warning( _("The mode KIOSK unavailable, package is not installed.") )
        self.local_docs = self.builder.get_object( "help_prog_offline" )
        if not os.path.exists( LOCALDOCS ): self.local_docs.set_sensitive( False )
        if check_global( "stealth_mode" ) and not ROOT:
            self.treeview.set_headers_visible( False )

    def initGroups( self ):
        g = Gtk.ListStore( str )
        records, groups = getSaveConnections()
        for group in groups:
            g.append( [ group ] )
        groups_citrix = self.builder.get_object( "combo_CITRIX_group" )
        groups_web    = self.builder.get_object( "combo_WEB_group"    )
        groups_citrix.set_model( g )
        groups_web.set_model( g )
        return( g )

    def createDesktopFile(self, filename, nameConnect, nameDesktop):
        """Create desktop-file for connection"""
        with open(filename,"w") as label:
            label.write(DESKTOP_INFO)
        with open(filename,"a") as label:
            label.write('Exec=%s"%s"\n' % (EXEC, nameConnect))
            label.write('Name=%s\n' % nameDesktop)
        os.system('chmod 755 \"%s\"' % filename)

    def onDragLabel(self, widget, drag_context, data, info, time):
        """Drag-and-Drop for create desktop-file of the connection"""
        table, indexRow = self.treeview.get_selection().get_selected()
        nameConnect = table[indexRow][0]
        nameUnicode = nameConnect.encode()
        if len(nameConnect) == len(nameUnicode):
            filename = "/tmp/%s.desktop" % nameConnect
        else: filename = "/tmp/%s.desktop" % nameUnicode
        self.createDesktopFile(filename, nameConnect, nameConnect)
        data.set_uris(["file://%s" % filename])

    def do_activate(self):
        """Обязательный обработчик для Gtk.Application"""
        self.add_window(self.window)
        self.showWin()

    def showWin(self):
        self.window.show_all()
        self.window.present()

    def initTray(self):
        """Инициализация индикатора в системном лотке"""
        self.menu_tray = self.builder.get_object("menu_tray")
        self.iconTray = TrayIcon( "myconnector", self.menu_tray )
        self.iconTray.connect(self.onShowWindow)
        self.initSubmenuTray()
        self.menu_tray.show_all()
        return True

    def initSubmenuTray(self):
        """Инициализация списка сохраненных подключений в меню из трея"""
        exist = False
        for item in self.tray_submenu.get_children(): item.destroy() #очищение меню перед его заполнением
        records, groups = getSaveConnections()
        menus = {}
        for group in groups:
            group_item = Gtk.MenuItem( group )
            self.tray_submenu.append( group_item )
            menus[ group ] = Gtk.Menu()
            group_item.set_submenu( menus[ group ] )
        for record in records:
            exist = True
            name, group, protocol = record[0], record[1], record[2]
            item = Gtk.ImageMenuItem(name)
            image = Gtk.Image()
            if check_global( "stealth_mode" ) and not ROOT:
                image.new_from_icon_name( APP, 1 )
            else:
                image.set_from_pixbuf( GdkPixbuf.Pixbuf.new_from_file( "%s/%s.png" % ( ICONFOLDER, protocol )))
            item.set_image(image)
            item.connect( "activate", self.onSaveConnect, name )
            if group:
                menus[ group ].append( item )
            else:
                self.tray_submenu.append( item )
        if not exist:
            tray_noexist = Gtk.MenuItem( "<%s>" % _("no saved connections") )
            tray_noexist.set_sensitive(False)
            self.tray_submenu.append(tray_noexist)
        self.tray_submenu.show_all()

    def initLabels(self, rdp, vnc, fs, spice):
        """Display on the main window the program name for RDP, VNC, SPICE and FS"""
        rdp.set_text  ( "(%s)" % CONFIG.get( "rdp"   ) )
        vnc.set_text  ( "(%s)" % CONFIG.get( "vnc"   ) )
        fs.set_text   ( "(%s)" % CONFIG.get( "fs"    ) )
        spice.set_text( "(%s)" % CONFIG.get( "spice" ) )

    def onDeleteWindow(self, *args):
        """Закрытие программы"""
        if args[0] == 2:
            msg = "KeyboardInterrupt: MyConnector %s!" % _("is closed")
            options.log.info (msg)
            print ('\n' + msg)
        self.quit()

    def onViewAbout(self, *args):
        """Создает диалоговое окно 'О программе'"""
        about = Gtk.AboutDialog( parent = self.window )
        about.set_program_name( "MyConnector (ex. Connector)" )
        about.set_comments( _("A frontend program for remote administration "
              "of computers with various OS. Most common connection types are supported.") )
        about.set_version( "%s (release: %s)" % ( VERSION, RELEASE ) )
        about.set_website( "http://myconnector.ru" )
        about.set_website_label( "http://myconnector.ru" )
        about.set_license(
            "MyConnector\n\n"
            "This program is free software; you can redistribute it and/or\n"
            "modify it under the terms of the version 2 of the GNU General\n"
            "Public License as published by the Free Software Foundation.\n\n"
            "This program is distributed in the hope that it will be useful,\n"
            "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
            "GNU General Public License for more details.\n\n"""
            "You should have received a copy of the GNU General Public License\n"
            "along with this program. If not, see http://www.gnu.org/licenses/." )
        about.set_copyright(
            "© Korneechev E.A., 2014-2022\n"
            "ek@myconnector.ru" )
        about.set_logo_icon_name( "myconnector" )
        about.run()
        about.destroy()

    def createOpenDialog(self, title):
        """Создание диалога открытия файла"""
        dialog = Gtk.FileChooserDialog(title, self.window,
            Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.addFilters(dialog)
        dialog.set_current_folder(HOMEFOLDER)
        return dialog

    def onOpenFile(self, *args):
        """Открытие файла для мгновенного подключения"""
        dialog = self.createOpenDialog( _("Opening the connection configuration file") )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            openFile(filename)
            viewStatus( self.statusbar, "%s %s " % ( _("Open the file"), filename ) )
        else:
            viewStatus( self.statusbar, _("The file is not selected!") )
        dialog.destroy()

    def onImportFile(self, *args):
        """Открытие файла для изменения и дальнейшего подключения"""
        dialog = self.createOpenDialog( _("Importing the connection configuration file") )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            parameters = options.loadFromFile( filename, _import = True )
            if parameters != None:
                try:
                    protocol = parameters [ "protocol" ].upper()
                except KeyError:
                    protocol_not_found( filename )
                    dialog.destroy()
                    return None
                if protocol in [ "CITRIX", "WEB" ]:
                    try:
                        self.onWCEdit( "", parameters[ "server" ], protocol, parameters.get( "group", "" ) )
                    except KeyError:
                        server_not_found( filename )
                        dialog.destroy()
                        return None
                else:
                    analogEntry = self.AnalogEntry( protocol, parameters )
                    self.onButtonPref( analogEntry, parameters.get( "name", "" ) )
                msg = "%s %s " % ( _("Imported the file"), filename )
                options.log.info ( msg )
                viewStatus( self.statusbar, msg )
        else:
            viewStatus( self.statusbar, _("The file is not selected!") )
        dialog.destroy()

    def addFilters(self, dialog):
        filter_myc = Gtk.FileFilter()
        filter_myc.set_name( "MyConnector" )
        filter_myc.add_pattern( "*.myc" )
        dialog.add_filter( filter_myc )
        filter_ctor = Gtk.FileFilter()
        filter_ctor.set_name( "Connector" )
        filter_ctor.add_pattern( "*.ctor" )
        dialog.add_filter( filter_ctor )
        filter_rdp = Gtk.FileFilter()
        filter_rdp.set_name( "RDP (Windows)" )
        filter_rdp.add_pattern("*.rdp")
        filter_rdp.add_pattern("*.RDP")
        filter_rdp.add_pattern("*.rdpx")
        dialog.add_filter(filter_rdp)
        filter_remmina = Gtk.FileFilter()
        filter_remmina.set_name( "Remmina" )
        filter_remmina.add_pattern("*.remmina")
        dialog.add_filter(filter_remmina)
        filter_any = Gtk.FileFilter()
        filter_any.set_name( _("All files") )
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def onButtonConnect(self, entry):
        """Сигнал кнопке для быстрого подключения к указанному в entry серверу"""
        server = entry.get_text()
        protocol = entry.get_name()
        if server:
            name = changeProgram( protocol )
            connect = definition( name )
            if self.prefClick: #если нажата кнопка Доп. Параметры
                parameters = self.applyPreferences( name )
                parameters[ "server" ] = server
                namesave = self.pref_builder.get_object( "entry_%s_name" % protocol ).get_text()
                if namesave:
                    parameters[ "name" ] = namesave
                if name == "RDP1" or name == "VMWARE" or name == "X2GO":
                    self.saveKeyring ( parameters.copy() )
            else:
                try: parameters = CONFIGS[ name ]
                except KeyError:
                    try: parameters = DEF_PROTO[ name ].copy()
                    except KeyError: parameters = server
            try:
                parameters[ "server"   ] = server
                parameters[ "protocol" ] = protocol
            except Exception as e:
                options.log.error( e )
            connect.start(parameters)
            viewStatus( self.statusbar, "%s %s... "% ( _("Connecting to the server"), server ) )
            if not check_global( "system_folder" ):
                self.writeServerInDb(entry)
        else:
            viewStatus( self.statusbar, _("Enter the server address...").replace( "...", "") )

    def onCitrixPref(self, *args):
        Citrix.preferences()

    def onButtonPref(self, entry_server, nameConnect = ''):
        """Дополнительные параметры подключения к серверу.
        Доступно как с кнопки, так и из пункта меню 'Подключение'"""
        self.window.set_sensitive( False )
        self.pref_window = Gtk.Window()
        self.prefClick = True #для определения нажатия на кнопку Доп. параметры
        protocol = entry_server.get_name()
        server   = entry_server.get_text()
        self.pref_window.set_title( "%s: %s" % ( protocol, _("connection parameters") ) )
        self.pref_window.set_icon_from_file( "%s/%s.png" % ( ICONFOLDER, protocol ) )
        self.pref_window.set_position(Gtk.WindowPosition.CENTER)
        self.pref_window.set_resizable(False)
        self.pref_window.set_modal(True)
        self.pref_window.resize(400, 400)
        self.pref_builder = Gtk.Builder()
        self.pref_builder.set_translation_domain( APP )
        self.pref_builder.add_from_file( "%s/protocols.ui" % UIFOLDER )
        self.pref_builder.connect_signals(self)
        if 'loadParameters' in dir(entry_server): #если изменяется или копируется соединение, то загружаем параметры (фэйковый класс Entry)
            parameters = entry_server.loadParameters()
            name = changeProgram( protocol, parameters.get( "program", "" ) )
        else: #иначе (новое подключение), пытаемся загрузить дефолтные настройки
            name = changeProgram( protocol )
            try: parameters = CONFIGS[ name ]
            except KeyError:
                try:
                    parameters = DEF_PROTO[ name ].copy()
                except KeyError:
                    parameters = None
            if type(parameters) == dict:
                parameters[ "server" ] = server
        entryName = self.pref_builder.get_object( "entry_%s_name" % name )
        if nameConnect: entryName.set_text( nameConnect )
        box = self.pref_builder.get_object( "box_%s" % name )
        combo = self.pref_builder.get_object( "combo_%s" % name )
        model_addresses = self.liststore[ protocol ]
        combo.set_model( model_addresses )
        completion_addresses = Gtk.EntryCompletion()
        completion_addresses.set_model( model_addresses )
        completion_addresses.set_text_column( 0 )
        serv = self.pref_builder.get_object( "entry_%s_serv" % name )
        serv.set_text( server )
        serv.set_completion( completion_addresses )
        cancel = self.pref_builder.get_object( "button_%s_cancel" % name )
        cancel.connect( "clicked", self.onCancel, self.pref_window )
        self.pref_window.connect( "delete-event", self.onClose )
        entryGroup = self.pref_builder.get_object( "entry_%s_group" % name )
        try: entryGroup.set_text( parameters.get( "group", "" ) )
        except Exception as e:
            options.log.error( e )
        combo_groups = self.pref_builder.get_object( "combo_%s_group" % name )
        model_groups = self.initGroups()
        combo_groups.set_model( model_groups )
        completion_groups = Gtk.EntryCompletion()
        completion_groups.set_model( model_groups )
        completion_groups.set_text_column( 0 )
        entryGroup.set_completion( completion_groups )
        button_default = self.pref_builder.get_object( "button_%s_default" % name )
        if check_global( "system_config" ) and not ROOT:
            button_default.set_sensitive( False )
            button_default.set_tooltip_text( _("Unavailable! System settings are used!") )
        self.initPreferences( name )
        self.setPreferences( name, parameters )
        self.pref_window.add(box)
        self.pref_window.show_all()

    def setPreferences(self, protocol, args):
        """В этой функции параметры загружаются из сохраненного файла"""
        if not args: return False
        if protocol == "VNC1":
            if args.getboolean( "fullscreen" ): self.VNC_viewmode.set_active( True )
            if args.getboolean( "viewonly"   ): self.VNC_viewonly.set_active( True )
            if args.getboolean( "listen"     ): self.VNC_listen.set_active(   True )
            self.VNC_port.set_text( args.get( "listen_port", "" ) )

        if protocol == "VNC":
            self.VNC_user.set_text(         args.get( "username",   "" ) )
            self.VNC_quality.set_active_id( args.get( "quality",    "" ) )
            self.VNC_color.set_active_id(   args.get( "colordepth", "" ) )
            if args.get( "viewmode" , "1" ) == "4"   : self.VNC_viewmode.set_active(   True )
            if args.getboolean( "viewonly"          ): self.VNC_viewonly.set_active(   True )
            if args.getboolean( "disableencryption" ): self.VNC_crypt.set_active(      True )
            if args.getboolean( "disableclipboard"  ): self.VNC_clipboard.set_active(  True )
            if args.getboolean( "showcursor"        ): self.VNC_showcursor.set_active( True )
            else: self.VNC_showcursor.set_active( False )

        if protocol == "VMWARE":
            self.VMWARE_user.set_text( args.get( "username", "" ) )
            self.VMWARE_domain.set_text( args.get( "domain", "" ) )
            if args.getboolean( "fullscreen" ): self.VMWARE_fullscreen.set_active( True )
            if not check_option( "passwd_off" ):
                try:
                    password = keyring.get_password( args.get( "server", "" ), args.get( "username", "" ) )
                except Exception as e:
                    options.log.error( e )
                    password = ""
                if args.getboolean( "passwdsave" ) or password: self.VMWARE_pwdsave.set_active( True )
                if not password: password = args.get( "passwd", "" )
                self.VMWARE_password.set_text( password )
            else:
                self.VMWARE_pwdsave.set_sensitive( False )

        if protocol == "XDMCP":
            self.XDMCP_color.set_active_id( args.get( "colordepth", "" ) )
            self.XDMCP_exec.set_text(       args.get( "exec",       "" ) )
            if args.get( "viewmode", "" ) == "4": self.XDMCP_viewmode.set_active(      True )
            if not args.get( "resolution", "" ) : self.XDMCP_resol_default.set_active( True )
            else:
                XDMCP_resol_hand = self.pref_builder.get_object( "radio_XDMCP_resol_hand" )
                XDMCP_resol_hand.set_active( True )
                self.XDMCP_resolution.set_active_id( args[ "resolution" ] )
            if args.getboolean( "once"         ): self.XDMCP_once.set_active(          True )
            if args.getboolean( "showcursor"   ): self.XDMCP_showcursor.set_active(    True )

        if protocol == "SSH":
            self.SSH_user.set_text(             args.get( "username",       "" ) )
            self.SSH_path_keyfile.set_filename( args.get( "ssh_privatekey", "" ) )
            self.SSH_charset.set_text(          args.get( "ssh_charset",    "" ) )
            self.SSH_exec.set_text(             args.get( "exec",           "" ) )
            self.SSH_knock.set_text(            args.get( "knocking",       "" ) )
            if   args.get( "ssh_auth" ) == "3": self.SSH_publickey.set_active( True )
            elif args.get( "ssh_auth" ) == "1": self.SSH_keyfile.set_active(   True )
            else:
                SSH_pwd = self.pref_builder.get_object( "radio_SSH_pwd" )
                SSH_pwd.set_active( True )

        if protocol == "SFTP":
            self.SFTP_user.set_text(             args.get( "username",          "" ) )
            self.SFTP_path_keyfile.set_filename( args.get( "ssh_privatekey",    "" ) )
            self.SFTP_charset.set_text(          args.get( "ssh_charset",       "" ) )
            self.SFTP_execpath.set_text(         args.get( "execpath",          "" ) )
            self.SFTP_knock.set_text(             args.get( "knocking",          "" ) )
            if   args.get( "ssh_auth" ) == "3": self.SFTP_publickey.set_active( True )
            elif args.get( "ssh_auth" ) == "1": self.SFTP_keyfile.set_active(   True )
            else:
                SFTP_pwd = self.pref_builder.get_object( "radio_SFTP_pwd" )
                SFTP_pwd.set_active( True )

        if protocol == "NX":
            self.NX_user.set_text(         args.get ( "username", "" ) )
            self.NX_quality.set_active_id( args.get ( "quality",  "" ) )
            self.NX_exec.set_text(         args.get ( "exec",     "" ) )
            if not args.get ( "resolution", "" ): self.NX_resol_window.set_active(   True )
            else:
                NX_resol_hand = self.pref_builder.get_object( "radio_NX_resol_hand" )
                NX_resol_hand.set_active( True )
                self.NX_resolution.set_active_id( args[ "resolution" ] )
            if args.get ( "viewmode", "" ) == "4"  : self.NX_viewmode.set_active(    True )
            if not args.get ( "nx_privatekey", "" ): self.NX_keyfile.set_active(    False )
            else:
                self.NX_keyfile.set_active( True )
                self.NX_path_keyfile.set_filename( args[ "nx_privatekey" ] )
            if args.getboolean( "disableencryption" ): self.NX_crypt.set_active(     True )
            if args.getboolean( "disableclipboard"  ): self.NX_clipboard.set_active( True )

        if protocol == "RDP":
            self.RDP_user.set_text(         args.get( "username",   "" ) )
            self.RDP_domain.set_text(       args.get( "domain",     "" ) )
            self.RDP_color.set_active_id(   args.get( "colordepth", "" ) )
            self.RDP_quality.set_active_id( args.get( "quality",    "" ) )
            self.RDP_sound.set_active_id(   args.get( "sound",      "" ) )
            if not args.get( "resolution", "" ): self.RDP_resol_default.set_active(   True )
            else:
                RDP_resol_hand = self.pref_builder.get_object( "radio_RDP_resol_hand" )
                RDP_resol_hand.set_active( True )
                self.RDP_resolution.set_active_id( args[ "resolution" ] )
            if args.get( "viewmode", "" ) == "3": self.RDP_viewmode.set_active(       True )
            else: self.RDP_viewmode.set_active( False )
            if not args.get( "sharefolder", "" ): self.RDP_share_folder.set_active(  False )
            else:
                self.RDP_share_folder.set_active( True )
                self.RDP_name_folder.set_filename( args[ "sharefolder" ] )
            if args.getboolean( "shareprinter"     ): self.RDP_printers.set_active(   True )
            if args.getboolean( "disableclipboard" ): self.RDP_clipboard.set_active( False )
            if args.getboolean( "sharesmartcard"   ): self.RDP_cards.set_active(      True )

        if protocol == "RDP1":
            self.RDP_user.set_text(       args.get( "username",   "" ) )
            self.RDP_domain.set_text(     args.get( "domain",     "" ) )
            self.RDP_gserver.set_text(    args.get( "gserver",    "" ) )
            self.RDP_guser.set_text(      args.get( "guser",      "" ) )
            self.RDP_gdomain.set_text(    args.get( "gdomain",    "" ) )
            self.RDP_gpasswd.set_text(    args.get( "gpasswd",    "" ) )
            self.RDP_color.set_active_id( args.get( "color",      "" ) )
            self.RDP_userparams.set_text( args.get( "userparams", "" ) )
            if args.getboolean( "fullscreen" ): self.RDP_fullscreen.set_active(    True )
            elif args.get( "resolution",  "" ):
                RDP_resol_hand = self.pref_builder.get_object( "radio_RDP1_resol_hand"  )
                RDP_resol_hand.set_active( True )
                self.RDP_resolution.set_text( args[ "resolution" ] )
            elif args.getboolean( "workarea" ): self.RDP_workarea.set_active(      True )
            else: self.RDP_resol_default.set_active( True )
            if args.getboolean( "clipboard"  ): self.RDP_clipboard.set_active(     True )
            else: self.RDP_clipboard.set_active( False )
            if not args.get( "folder", ""    ): self.RDP_share_folder.set_active( False )
            else:
                self.RDP_share_folder.set_active( True )
                self.RDP_name_folder.set_filename( args[ "folder" ] )
            if args.getboolean( "admin"      ): self.RDP_admin.set_active(         True )
            if args.getboolean( "smartcards" ): self.RDP_cards.set_active(         True )
            if args.getboolean( "printers"   ): self.RDP_printers.set_active(      True )
            if args.getboolean( "sound"      ): self.RDP_sound.set_active(         True )
            if args.getboolean( "microphone" ): self.RDP_microphone.set_active(    True )
            if args.getboolean( "multimon"   ): self.RDP_multimon.set_active(      True )
            if args.getboolean( "compression" ):
                self.RDP_compression.set_active( True )
                self.RDP_compr_level.set_active_id( args.get( "compr_level", "0" ) )
            if args.getboolean( "fonts"      ): self.RDP_fonts.set_active(         True )
            if args.getboolean( "aero"       ): self.RDP_aero.set_active(          True )
            if args.getboolean( "drag"       ): self.RDP_drag.set_active(          True )
            if args.getboolean( "animation"  ): self.RDP_animation.set_active(     True )
            if args.getboolean( "theme"      ): self.RDP_theme.set_active(         True )
            if args.getboolean( "wallpapers" ): self.RDP_wallpapers.set_active(    True )
            if args.getboolean( "nsc"        ): self.RDP_nsc.set_active(           True )
            if args.getboolean( "jpeg" ):
                self.RDP_jpeg.set_active( True )
                self.RDP_jpeg_quality.set_value( float( args.get( "jpeg_quality", "80" ) ) )
            if args.getboolean( "usb"        ): self.RDP_usb.set_active(           True )
            if args.getboolean( "disable_nla"): self.RDP_nla.set_active(           True )
            if args.getboolean( "span"       ): self.RDP_span.set_active(          True )
            if args.getboolean( "desktop"    ): self.RDP_desktop.set_active(       True )
            if args.getboolean( "downloads"  ): self.RDP_down.set_active(          True )
            if args.getboolean( "documents"  ): self.RDP_docs.set_active(          True )
            if args.getboolean( "gdi"        ): self.RDP_gdi.set_active(           True )
            if args.getboolean( "reconnect"  ): self.RDP_reconnect.set_active(    False )
            if args.getboolean( "certignore" ): self.RDP_certignore.set_active(    True )
            if args.getboolean( "glyph"      ): self.RDP_glyph.set_active(         True )
            if not check_option( "passwd_off" ):
                try:
                    password = keyring.get_password( args.get( "server", "" ), args.get( "username", "" ) )
                except Exception as e:
                    options.log.error( e )
                    password = ""
                if args.getboolean( "passwdsave" ) or password: self.RDP_pwdsave.set_active( True )
                if not password: password = args.get( "passwd", "" )
                self.RDP_pwd.set_text( password )
            else:
                self.RDP_pwdsave.set_sensitive( False )
            self.RDP_security.set_active_id( args.get( "security", "False" ) )

        if protocol == "SPICE":
            if args.getboolean( "usetls"           ): self.SPICE_tls.set_active(        True )
            if args.getboolean( "viewonly"         ): self.SPICE_viewonly.set_active(   True )
            if args.getboolean( "resizeguest"      ): self.SPICE_resize.set_active(     True )
            if args.getboolean( "disableclipboard" ): self.SPICE_clipboard.set_active( False )
            if args.getboolean( "sharesmartcard"   ): self.SPICE_cards.set_active(      True )
            if args.getboolean( "enableaudio"      ): self.SPICE_sound.set_active(      True )
            if not args.get(    "cacert", ""       ): self.SPICE_CA.set_active(        False )
            else:
                self.SPICE_CA.set_active( True )
                self.SPICE_cacert.set_filename( args[ "cacert" ] )

        if protocol == "FS":
            self.FS_user.set_text(      args.get( "user",   "" ) )
            self.FS_domain.set_text(    args.get( "domain", "" ) )
            self.FS_folder.set_text(    args.get( "folder", "" ) )
            self.FS_type.set_active_id( args.get( "type",   "" ) )

        if protocol == "X2GO":
            username = args.get( "username", "" )
            self.X2GO_user.set_text( username   )
            self.X2GO_session.set_text(  args.get( "session",  "" ) )
            self.X2GO_port.set_text(     args.get( "port",     "" ) )
            geometry = args.get( "geometry", "fullscreen" )
            if geometry in ( "fullscreen", "" ):
                self.X2GO_fullscreen.set_active( True )
                self.X2GO_geometry.set_sensitive( False )
                self.X2GO_geometry.set_text( "" )
            else:
                self.X2GO_geometry_hand = self.pref_builder.get_object( "radio_X2GO_geometry"   )
                self.X2GO_geometry_hand.set_active( True )
                self.X2GO_geometry.set_text( geometry )
            if not check_option( "passwd_off" ):
                try:
                    password = keyring.get_password( args.get( "server", "" ), username )
                except Exception as e:
                    options.log.error( e )
                    password = ""
                if args.getboolean( "passwdsave" ) or password: self.X2GO_pwdsave.set_active( True )
                if not password: password = args.get( "passwd", "" )
                self.X2GO_pwd.set_text( password )
            else:
                self.X2GO_pwdsave.set_sensitive( False )
            if args.getboolean( "printers"   ): self.X2GO_print.set_active(      True )
            if args.getboolean( "sound"      ): self.X2GO_sound.set_active(      True )

        if protocol == "SPICE1":
            if args.getboolean( "fullscreen" ): self.SPICE_fullscreen.set_active( True )

    def initPreferences( self, protocol ):
        """В этой функции определяются различные для протоколов параметры"""
        if protocol == "RDP": #remmina
            self.RDP_user          = self.pref_builder.get_object( "entry_RDP_user"          )
            self.RDP_domain        = self.pref_builder.get_object( "entry_RDP_dom"           )
            self.RDP_color         = self.pref_builder.get_object( "entry_RDP_color"         )
            self.RDP_quality       = self.pref_builder.get_object( "entry_RDP_quality"       )
            self.RDP_resolution    = self.pref_builder.get_object( "entry_RDP_resolution"    )
            self.RDP_viewmode      = self.pref_builder.get_object( "check_RDP_fullscreen"    )
            self.RDP_resol_default = self.pref_builder.get_object( "radio_RDP_resol_default" )
            self.RDP_share_folder  = self.pref_builder.get_object( "check_RDP_folder"        )
            self.RDP_name_folder   = self.pref_builder.get_object( "RDP_share_folder"        )
            self.RDP_printers      = self.pref_builder.get_object( "check_RDP_printers"      )
            self.RDP_clipboard     = self.pref_builder.get_object( "check_RDP_clipboard"     )
            self.RDP_sound         = self.pref_builder.get_object( "entry_RDP_sound"         )
            self.RDP_cards         = self.pref_builder.get_object( "check_RDP_cards"         )
            self.RDP_name_folder.set_current_folder( HOMEFOLDER )

        if protocol == "RDP1": #freerdp
            self.RDP_user          = self.pref_builder.get_object( "entry_RDP1_user"          )
            self.RDP_domain        = self.pref_builder.get_object( "entry_RDP1_dom"           )
            self.RDP_color         = self.pref_builder.get_object( "entry_RDP1_color"         )
            self.RDP_resolution    = self.pref_builder.get_object( "entry_RDP1_resolution"    )
            self.RDP_fullscreen    = self.pref_builder.get_object( "radio_RDP1_fullscreen"    )
            self.RDP_resol_default = self.pref_builder.get_object( "radio_RDP1_resol_default" )
            self.RDP_share_folder  = self.pref_builder.get_object( "check_RDP1_folder"        )
            self.RDP_name_folder   = self.pref_builder.get_object( "RDP1_share_folder"        )
            self.RDP_clipboard     = self.pref_builder.get_object( "check_RDP1_clipboard"     )
            self.RDP_guser         = self.pref_builder.get_object( "entry_RDP1_guser"         )
            self.RDP_gdomain       = self.pref_builder.get_object( "entry_RDP1_gdom"          )
            self.RDP_gserver       = self.pref_builder.get_object( "entry_RDP1_gserv"         )
            self.RDP_gpasswd       = self.pref_builder.get_object( "entry_RDP1_gpwd"          )
            self.RDP_admin         = self.pref_builder.get_object( "check_RDP1_adm"           )
            self.RDP_cards         = self.pref_builder.get_object( "check_RDP1_cards"         )
            self.RDP_printers      = self.pref_builder.get_object( "check_RDP1_printers"      )
            self.RDP_sound         = self.pref_builder.get_object( "check_RDP1_sound"         )
            self.RDP_microphone    = self.pref_builder.get_object( "check_RDP1_microphone"    )
            self.RDP_multimon      = self.pref_builder.get_object( "check_RDP1_multimon"      )
            self.RDP_compression   = self.pref_builder.get_object( "check_RDP1_compression"   )
            self.RDP_compr_level   = self.pref_builder.get_object( "entry_RDP1_compr_level"   )
            self.RDP_fonts         = self.pref_builder.get_object( "check_RDP1_fonts"         )
            self.RDP_aero          = self.pref_builder.get_object( "check_RDP1_aero"          )
            self.RDP_drag          = self.pref_builder.get_object( "check_RDP1_drag"          )
            self.RDP_animation     = self.pref_builder.get_object( "check_RDP1_animation"     )
            self.RDP_theme         = self.pref_builder.get_object( "check_RDP1_theme"         )
            self.RDP_wallpapers    = self.pref_builder.get_object( "check_RDP1_wallpapers"    )
            self.RDP_nsc           = self.pref_builder.get_object( "check_RDP1_nsc"           )
            self.RDP_jpeg          = self.pref_builder.get_object( "check_RDP1_jpeg"          )
            self.RDP_jpeg_quality  = self.pref_builder.get_object( "scale_RDP1_jpeg"          )
            self.RDP_usb           = self.pref_builder.get_object( "check_RDP1_usb"           )
            self.RDP_nla           = self.pref_builder.get_object( "check_RDP1_nla"           )
            self.RDP_workarea      = self.pref_builder.get_object( "radio_RDP1_workarea"      )
            self.RDP_span          = self.pref_builder.get_object( "check_RDP1_span"          )
            self.RDP_desktop       = self.pref_builder.get_object( "check_RDP1_desktop"       )
            self.RDP_down          = self.pref_builder.get_object( "check_RDP1_down"          )
            self.RDP_docs          = self.pref_builder.get_object( "check_RDP1_docs"          )
            self.RDP_gdi           = self.pref_builder.get_object( "check_RDP1_gdi"           )
            self.RDP_reconnect     = self.pref_builder.get_object( "check_RDP1_reconnect"     )
            self.RDP_certignore    = self.pref_builder.get_object( "check_RDP1_certignore"    )
            self.RDP_pwd           = self.pref_builder.get_object( "entry_RDP1_pwd"           )
            self.RDP_pwdsave       = self.pref_builder.get_object( "check_RDP1_pwd"           )
            if check_option( "passwd_off" ): self.RDP_pwdsave.set_sensitive( False      )
            self.RDP_glyph         = self.pref_builder.get_object( "check_RDP1_glyph"         )
            self.RDP_userparams    = self.pref_builder.get_object( "entry_RDP1_userparams"    )
            self.RDP_security      = self.pref_builder.get_object( "entry_RDP1_security"      )
            self.RDP_resolution.set_sensitive( False )
            self.RDP_name_folder.set_current_folder( HOMEFOLDER )

        if protocol == "NX":
            self.NX_user         = self.pref_builder.get_object( "entry_NX_user"         )
            self.NX_keyfile      = self.pref_builder.get_object( "check_NX_keyfile"      )
            self.NX_path_keyfile = self.pref_builder.get_object( "NX_keyfile"            )
            self.NX_quality      = self.pref_builder.get_object( "entry_NX_quality"      )
            self.NX_resolution   = self.pref_builder.get_object( "entry_NX_resolution"   )
            self.NX_viewmode     = self.pref_builder.get_object( "check_NX_fullscreen"   )
            self.NX_resol_window = self.pref_builder.get_object( "radio_NX_resol_window" )
            self.NX_exec         = self.pref_builder.get_object( "entry_NX_exec"         )
            self.NX_crypt        = self.pref_builder.get_object( "check_NX_crypt"        )
            self.NX_clipboard    = self.pref_builder.get_object( "check_NX_clipboard"    )
            self.NX_path_keyfile.set_current_folder( HOMEFOLDER )

        if protocol == "VNC": #remmina
            self.VNC_user       = self.pref_builder.get_object( "entry_VNC_user"       )
            self.VNC_color      = self.pref_builder.get_object( "entry_VNC_color"      )
            self.VNC_quality    = self.pref_builder.get_object( "entry_VNC_quality"    )
            self.VNC_viewmode   = self.pref_builder.get_object( "check_VNC_fullscreen" )
            self.VNC_viewonly   = self.pref_builder.get_object( "check_VNC_viewonly"   )
            self.VNC_showcursor = self.pref_builder.get_object( "check_VNC_showcursor" )
            self.VNC_crypt      = self.pref_builder.get_object( "check_VNC_crypt"      )
            self.VNC_clipboard  = self.pref_builder.get_object( "check_VNC_clipboard"  )

        if protocol == "VNC1": #vncviewer
            self.VNC_server   = self.pref_builder.get_object( "entry_VNC1_serv"       )
            self.VNC_viewmode = self.pref_builder.get_object( "check_VNC1_fullscreen" )
            self.VNC_viewonly = self.pref_builder.get_object( "check_VNC1_viewonly"   )
            self.VNC_listen   = self.pref_builder.get_object( "check_VNC1_listen"     )
            self.VNC_port     = self.pref_builder.get_object( "entry_VNC1_port"       )

        if protocol == "XDMCP":
            self.XDMCP_color         = self.pref_builder.get_object( "entry_XDMCP_color"         )
            self.XDMCP_resolution    = self.pref_builder.get_object( "entry_XDMCP_resolution"    )
            self.XDMCP_viewmode      = self.pref_builder.get_object( "check_XDMCP_fullscreen"    )
            self.XDMCP_resol_default = self.pref_builder.get_object( "radio_XDMCP_resol_default" )
            self.XDMCP_showcursor    = self.pref_builder.get_object( "check_XDMCP_showcursor"    )
            self.XDMCP_once          = self.pref_builder.get_object( "check_XDMCP_once"          )
            self.XDMCP_exec          = self.pref_builder.get_object( "entry_XDMCP_exec"          )

        if protocol == "SSH":
            self.SSH_user         = self.pref_builder.get_object( "entry_SSH_user"      )
            self.SSH_publickey    = self.pref_builder.get_object( "radio_SSH_publickey" )
            self.SSH_keyfile      = self.pref_builder.get_object( "radio_SSH_keyfile"   )
            self.SSH_path_keyfile = self.pref_builder.get_object( "SSH_keyfile"         )
            self.SSH_exec         = self.pref_builder.get_object( "entry_SSH_exec"      )
            self.SSH_charset      = self.pref_builder.get_object( "entry_SSH_charset"   )
            self.SSH_knock        = self.pref_builder.get_object( "entry_SSH_knock"     )
            self.SSH_path_keyfile.set_current_folder( HOMEFOLDER )

        if protocol == "SFTP":
            self.SFTP_user         = self.pref_builder.get_object( "entry_SFTP_user"      )
            self.SFTP_publickey    = self.pref_builder.get_object( "radio_SFTP_publickey" )
            self.SFTP_keyfile      = self.pref_builder.get_object( "radio_SFTP_keyfile"   )
            self.SFTP_path_keyfile = self.pref_builder.get_object( "SFTP_keyfile"         )
            self.SFTP_execpath     = self.pref_builder.get_object( "entry_SFTP_execpath"  )
            self.SFTP_charset      = self.pref_builder.get_object( "entry_SFTP_charset"   )
            self.SFTP_knock        = self.pref_builder.get_object( "entry_SFTP_knock"     )
            self.SFTP_path_keyfile.set_current_folder( HOMEFOLDER )

        if protocol == "VMWARE":
            self.VMWARE_user       = self.pref_builder.get_object( "entry_VMWARE_user"       )
            self.VMWARE_domain     = self.pref_builder.get_object( "entry_VMWARE_dom"        )
            self.VMWARE_password   = self.pref_builder.get_object( "entry_VMWARE_pwd"        )
            self.VMWARE_pwdsave    = self.pref_builder.get_object( "check_VMWARE_pwd"        )
            if check_option( "passwd_off" ): self.VMWARE_pwdsave.set_sensitive( False  )
            self.VMWARE_fullscreen = self.pref_builder.get_object( "check_VMWARE_fullscreen" )

        if protocol == "SPICE":
            self.SPICE_tls       = self.pref_builder.get_object( "check_SPICE_tls"       )
            self.SPICE_viewonly  = self.pref_builder.get_object( "check_SPICE_viewonly"  )
            self.SPICE_resize    = self.pref_builder.get_object( "check_SPICE_resize"    )
            self.SPICE_clipboard = self.pref_builder.get_object( "check_SPICE_clipboard" )
            self.SPICE_cards     = self.pref_builder.get_object( "check_SPICE_cards"     )
            self.SPICE_sound     = self.pref_builder.get_object( "check_SPICE_sound"     )
            self.SPICE_CA        = self.pref_builder.get_object( "check_SPICE_CA"        )
            self.SPICE_cacert    = self.pref_builder.get_object( "SPICE_CA"              )

        if protocol == "FS":
            self.FS_user   = self.pref_builder.get_object( "entry_FS_user"   )
            self.FS_domain = self.pref_builder.get_object( "entry_FS_dom"    )
            self.FS_folder = self.pref_builder.get_object( "entry_FS_folder" )
            self.FS_type   = self.pref_builder.get_object( "entry_FS_type"   )
            self.FS_server = self.pref_builder.get_object( "entry_FS_serv"   )

        if protocol == "X2GO":
            self.X2GO_user       = self.pref_builder.get_object( "entry_X2GO_user"       )
            self.X2GO_pwd        = self.pref_builder.get_object( "entry_X2GO_pwd"        )
            self.X2GO_pwdsave    = self.pref_builder.get_object( "check_X2GO_pwd"        )
            if check_option( "passwd_off" ): self.X2GO_pwdsave.set_sensitive(False )
            self.X2GO_session    = self.pref_builder.get_object( "entry_X2GO_session"    )
            self.X2GO_port       = self.pref_builder.get_object( "entry_X2GO_port"       )
            self.X2GO_fullscreen = self.pref_builder.get_object( "radio_X2GO_fullscreen" )
            self.X2GO_geometry   = self.pref_builder.get_object( "entry_X2GO_geometry"   )
            self.X2GO_print      = self.pref_builder.get_object( "check_X2GO_print"      )
            self.X2GO_sound      = self.pref_builder.get_object( "check_X2GO_sound"      )
            self.X2GO_geometry.set_sensitive( False )

        if protocol == "SPICE1":
            self.SPICE_fullscreen = self.pref_builder.get_object( "check_SPICE1_fullscreen" )

    def applyPreferences( self, protocol ):
        """В этой функции параметры для подключения собираются из окна Доп. параметры в список"""

        if protocol == "VMWARE":
            args = dict(
                username   = self.VMWARE_user.get_text(),
                domain     = self.VMWARE_domain.get_text(),
                passwd     = self.VMWARE_password.get_text(),
                passwdsave = "True" if self.VMWARE_pwdsave.get_active() else "False",
                fullscreen = str( self.VMWARE_fullscreen.get_active() ) )

        if protocol == "RDP":
            args = dict(
                username         = self.RDP_user.get_text(),
                domain           = self.RDP_domain.get_text(),
                colordepth       = self.RDP_color.get_active_id(),
                quality          = self.RDP_quality.get_active_id(),
                sound            = self.RDP_sound.get_active_id(),
                sharefolder      = self.RDP_name_folder.get_filename() if self.RDP_share_folder.get_active() else "",
                viewmode         = "3" if self.RDP_viewmode.get_active()      else "0",
                resolution       = ""  if self.RDP_resol_default.get_active() else self.RDP_resolution.get_active_id(),
                shareprinter     = "1" if self.RDP_printers.get_active()      else "0",
                disableclipboard = "0" if self.RDP_clipboard.get_active()     else "1",
                sharesmartcard   = "1" if self.RDP_cards.get_active()         else "0" )

        if protocol == "RDP1":
            args = dict(
                username    = self.RDP_user.get_text(),
                domain      = self.RDP_domain.get_text(),
                color       = self.RDP_color.get_active_id(),
                gserver     = self.RDP_gserver.get_text(),
                guser       = self.RDP_guser.get_text(),
                gdomain     = self.RDP_gdomain.get_text(),
                gpasswd     = self.RDP_gpasswd.get_text(),
                userparams  = self.RDP_userparams.get_text(),
                passwd      = self.RDP_pwd.get_text(),
                security    = self.RDP_security.get_active_id(),
                folder      = self.RDP_name_folder.get_filename() if self.RDP_share_folder.get_active() else "",
                fullscreen  = "True"  if self.RDP_fullscreen.get_active() else "False",
                clipboard   = "True"  if self.RDP_clipboard.get_active()  else "False",
                admin       = "True"  if self.RDP_admin.get_active()      else "False",
                smartcards  = "True"  if self.RDP_cards.get_active()      else "False",
                printers    = "True"  if self.RDP_printers.get_active()   else "False",
                sound       = "True"  if self.RDP_sound.get_active()      else "False",
                microphone  = "True"  if self.RDP_microphone.get_active() else "False",
                multimon    = "True"  if self.RDP_multimon.get_active()   else "False",
                fonts       = "True"  if self.RDP_fonts.get_active()      else "False",
                aero        = "True"  if self.RDP_aero.get_active()       else "False",
                drag        = "True"  if self.RDP_drag.get_active()       else "False",
                animation   = "True"  if self.RDP_animation.get_active()  else "False",
                theme       = "True"  if self.RDP_theme.get_active()      else "False",
                wallpapers  = "True"  if self.RDP_wallpapers.get_active() else "False",
                nsc         = "True"  if self.RDP_nsc.get_active()        else "False",
                usb         = "True"  if self.RDP_usb.get_active()        else "False",
                disable_nla = "True"  if self.RDP_nla.get_active()        else "False",
                span        = "True"  if self.RDP_span.get_active()       else "False",
                desktop     = "True"  if self.RDP_desktop.get_active()    else "False",
                downloads   = "True"  if self.RDP_down.get_active()       else "False",
                documents   = "True"  if self.RDP_docs.get_active()       else "False",
                gdi         = "True"  if self.RDP_gdi.get_active()        else "False",
                reconnect   = "False" if self.RDP_reconnect.get_active()  else "True",
                certignore  = "True"  if self.RDP_certignore.get_active() else "False",
                passwdsave  = "True"  if self.RDP_pwdsave.get_active()    else "False",
                glyph       = "True"  if self.RDP_glyph.get_active()      else "False" )
            args[ "workarea"   ] = "False"
            args[ "resolution" ] = ""
            if self.RDP_workarea.get_active(): args[ "workarea" ] = "True"
            elif self.RDP_resol_default.get_active(): pass
            else: args[ "resolution" ] = self.RDP_resolution.get_text()
            if self.RDP_compression.get_active():
                args[ "compression"  ] = "True"
                args[ "compr_level"  ] = self.RDP_compr_level.get_active_id()
            else:
                args[ "compression"  ] = "False"
                args[ "compr_level"  ] = "None"
            if self.RDP_jpeg.get_active():
                args[ "jpeg"         ] = "True"
                args[ "jpeg_quality" ] = str( self.RDP_jpeg_quality.get_value() )
            else:
                args[ "jpeg"         ] = "False"
                args[ "jpeg_quality" ] = "None"

        if protocol == "NX":
            args = dict(
                username          = self.NX_user.get_text(),
                quality           = self.NX_quality.get_active_id(),
                nx_privatekey     = self.NX_path_keyfile.get_filename() if self.NX_keyfile.get_active() else "",
                disableencryption = "1" if self.NX_crypt.get_active()        else "0",
                disableclipboard  = "1" if self.NX_clipboard.get_active()    else "0",
                viewmode          = "4" if self.NX_viewmode.get_active()     else "1",
                resolution        = ""  if self.NX_resol_window.get_active() else self.NX_resolution.get_active_id() )
            args[ "exec" ] = self.NX_exec.get_text()

        if protocol == "VNC":
            args = dict(
                username          = self.VNC_user.get_text(),
                quality           = self.VNC_quality.get_active_id(),
                colordepth        = self.VNC_color.get_active_id(),
                disableencryption = "1" if self.VNC_crypt.get_active()      else "0",
                disableclipboard  = "1" if self.VNC_clipboard.get_active()  else "0",
                viewmode          = "4" if self.VNC_viewmode.get_active()   else "1",
                showcursor        = "1" if self.VNC_showcursor.get_active() else "0",
                viewonly          = "1" if self.VNC_viewonly.get_active()   else "0" )

        if protocol == "VNC1":
            args = dict(
                fullscreen  = str( self.VNC_viewmode.get_active() ),
                viewonly    = str( self.VNC_viewonly.get_active() ),
                listen      = str( self.VNC_listen.get_active()   ),
                listen_port = self.VNC_port.get_text()              )

        if protocol == "XDMCP":
            args = dict(
                colordepth = self.XDMCP_color.get_active_id(),
                viewmode   = "4" if self.XDMCP_viewmode.get_active()      else "1",
                resolution = ""  if self.XDMCP_resol_default.get_active() else self.XDMCP_resolution.get_active_id(),
                showcursor = "1" if self.XDMCP_showcursor.get_active()    else "0",
                once       = "1" if self.XDMCP_once.get_active()          else "0" )
            args[ "exec" ] = self.XDMCP_exec.get_text()

        if protocol == "SSH":
            args = dict(
                username    = self.SSH_user.get_text(),
                knocking    = self.SSH_knock.get_text(),
                ssh_charset = self.SSH_charset.get_text() )
            args[ "exec"  ] = self.SSH_exec.get_text()
            if self.SSH_publickey.get_active():
                args[ "ssh_auth"   ] = "3"
            elif self.SSH_keyfile.get_active():
                args[ "ssh_auth"   ] = "1"
            else: args[ "ssh_auth" ] = "0"
            if args[ "ssh_auth" ] == "1":
                args[ "ssh_privatekey" ] = self.SSH_path_keyfile.get_filename()

        if protocol == "SFTP":
            args = dict(
                username    = self.SFTP_user.get_text(),
                knocking    = self.SFTP_knock.get_text(),
                ssh_charset = self.SFTP_charset.get_text(),
                execpath    = self.SFTP_execpath.get_text() )
            if self.SFTP_publickey.get_active():
                args[ "ssh_auth"   ] = "3"
            elif self.SFTP_keyfile.get_active():
                args[ "ssh_auth"   ] = "1"
            else: args[ "ssh_auth" ] = "0"
            if args[ "ssh_auth" ] == "1":
                args[ "ssh_privatekey" ] = self.SFTP_path_keyfile.get_filename()

        if protocol == "SPICE":
            args = dict(
                usetls           = "1" if self.SPICE_tls.get_active()       else "0",
                viewonly         = "1" if self.SPICE_viewonly.get_active()  else "0",
                resizeguest      = "1" if self.SPICE_resize.get_active()    else "0",
                disableclipboard = "0" if self.SPICE_clipboard.get_active() else "1",
                sharesmartcard   = "1" if self.SPICE_cards.get_active()     else "0",
                enableaudio      = "1" if self.SPICE_sound.get_active()     else "0",
                cacert           = self.SPICE_cacert.get_filename() if self.SPICE_CA.get_active() else "" )

        if protocol == "FS":
            args = dict(
                user   = self.FS_user.get_text(),
                domain = self.FS_domain.get_text(),
                folder = self.FS_folder.get_text(),
                type   = self.FS_type.get_active_id() )

        if protocol == "X2GO":
            args = dict(
                username   = self.X2GO_user.get_text(),
                passwd     = self.X2GO_pwd.get_text(),
                session    = self.X2GO_session.get_text(),
                port       = self.X2GO_port.get_text(),
                passwdsave = "True" if self.X2GO_pwdsave.get_active()    else "False",
                printers   = "True" if self.X2GO_print.get_active()      else "False",
                sound      = "True" if self.X2GO_sound.get_active()      else "False",
                geometry   = "fullscreen" if self.X2GO_fullscreen.get_active() else self.X2GO_geometry.get_text() )

        if protocol == "SPICE1":
            args = dict(
                fullscreen = "True" if self.SPICE_fullscreen.get_active() else "False" )

        return args

    def onCancel( self, button, win ):
        self.closeWin( win )

    def onClose( self, win, *args ):
        self.closeWin( win )

    def closeWin( self, window ):
        window.destroy()
        self.window.set_sensitive( True )
        self.prefClick = False
        if hasattr( self, "fileCtor" ): self.fileCtor = ""

    def onFolderChoose(self, widget, *args):
        """При нажатии на выбор папки в окне доп. параметров"""
        widget.set_active(True)

    def createDb(self, filename):
        """Создает пустой файл БД (или любой другой)"""
        f = open( "%s/%s" % ( WORKFOLDER, filename ),"w" )
        f.close()

    def getServersFromDb(self):
        """Чтение списка ранее посещенных серверов из файла"""
        try:
            for server in open( "%s/servers.db" % WORKFOLDER ):
                try: #попытка прочитать протокол/сервер
                    protocol, address = server.strip().split(':::')
                    self.liststore[protocol].append([address])
                except Exception as e:
                    options.log.error( e )
        except FileNotFoundError:
            options.log.warning( _("The list of servers (servers.db) was not found, an empty one was created.") )
            self.createDb("servers.db")

    def setSavesToListstore(self):
        """Set the list of save connections to ListStore"""
        self.liststore_connect.clear()
        records, groups = getSaveConnections()
        for record in records:
            self.liststore_connect.append( record )

    def writeServerInDb(self, entry):
        """Запись сервера в файл со списком ранее посещенных серверов"""
        db = open( "%s/servers.db" % WORKFOLDER , "r+" )
        protocol = entry.get_name().replace( "1", "" )
        address  = entry.get_text()
        record, thereis = protocol + ':::' + address, False
        for server in db:
            #проверка на наличие сервера в базе
            if record == server.strip(): thereis = True
        if not thereis:
            print (record, file = db)
            self.liststore[protocol].append([address])
        db.close()

    def onResolutionSet(self, widget):
        """Отображение списка разрешений"""
        try: widget.set_button_sensitivity(Gtk.SensitivityType.ON)
        except: widget.set_sensitive(True)

    def offResolutionSet(self, widget):
        """Скрытие списка разрешений"""
        try: widget.set_button_sensitivity(Gtk.SensitivityType.OFF)
        except: widget.set_sensitive(False)

    def onComprSet(self, widget):
        """Настройка чувствительности списка уровней сжатия"""
        if widget.get_button_sensitivity() == Gtk.SensitivityType.ON:
            widget.set_button_sensitivity(Gtk.SensitivityType.OFF)
        else: widget.set_button_sensitivity(Gtk.SensitivityType.ON)

    def onJpegSet(self, widget):
        """Настройка видимости установки качества кодека JPEG"""
        if widget.get_opacity(): widget.set_opacity(0)
        else: widget.set_opacity(1)

    def onListenVNC(self, widget):
        """Actions if VNC listening mode is enabled"""
        if widget.get_opacity():
            widget.set_opacity(0)
            self.VNC_server.set_sensitive( True )
        else:
            widget.set_opacity(1)
            self.VNC_server.set_text( "localhost" )
            self.VNC_server.set_sensitive( False )

    def onSpanOn(self, widget):
        """Настройка зависимости чувствительности ключа /span от /multimon"""
        if widget.get_sensitive():
            widget.set_sensitive(0)
            widget.set_active(0)
        else: widget.set_sensitive(1)

    def onProperties(self, *args):
        """Окно параметров приложения"""
        window = options.Properties(self)

    def saveFileCtor( self, name, protocol, server ):
        """Connect file (.myc) creation"""
        filename = ( "%s_%s.myc" % ( name.replace( " ", "_" ), protocol ) ).lower()
        options.log.info( "%s: %s - %s - %s", _("Added a new connection"), protocol, name, server )
        return filename

    def resaveFileCtor(self, name, protocol, server):
        """Пересохранение подключения с тем же именем файла .myc"""
        fileName = self.fileCtor
        options.log.info( "%s (%s)", _("The connection was changed"), name )
        return fileName

    def getProgram( self, name ):
        if name == "RDP1":
            return "freerdp"
        if name == "VNC1":
            return "vncviewer"
        if name == "SPICE1":
            return "virtviewer"
        if name in [ "RDP", "VNC", "SPICE" ]:
            return "remmina"
        else:
            return None

    def onButtonSave(self, entry):
        """Сохранение параметров для дальнейшего подключения с ними"""
        server   = entry.get_text()
        name     = entry.get_name()
        protocol = name.replace( "1", "" )
        parameters = self.applyPreferences( name )
        namesave = self.pref_builder.get_object( "entry_%s_name"  % name ).get_text()
        group    = self.pref_builder.get_object( "entry_%s_group" % name ).get_text()
        error = ""
        if namesave == "":
            error = _("Specify a name for the connection!")
        elif self.searchName( namesave ):
            error = _("The same connection name is already in use!")
        else:
            parameters[ "name"     ] = namesave
            parameters[ "protocol" ] = protocol
            parameters[ "server"   ] = server
            parameters[ "group"    ] = group
            if ( name == "RDP1" or name == "VMWARE" or name == "X2GO" ) and parameters.get ( "username", "" ):
                self.saveKeyring ( parameters.copy() )
                parameters [ "passwd" ] = ""
            program = self.getProgram( name )
            if program: parameters[ "program" ] = program
            if hasattr( self, "fileCtor" ): #checking - edit or new connection
                if self.fileCtor: newfile = False
                else: newfile = True
            else: newfile = True
            if newfile:
                fileName = self.saveFileCtor( namesave, protocol, server )
            else:
                fileName = self.resaveFileCtor( namesave, protocol, server )
            options.saveInFile( fileName, parameters )
            self.setSavesToListstore()
            self.pref_window.destroy()
            self.prefClick = False
            if group: self.initGroups()
            self.initSubmenuTray()
            viewStatus( self.statusbar, "%s (%s)..." % ( _("The connection is saved"), namesave ) )
            self.fileCtor = ""
            self.currentFilter = namesave
            self.filterConnections.refilter()
            self.treeview.set_cursor( 0 )
            self.currentFilter = ""
            self.filterConnections.refilter()
            self.window.set_sensitive( True )
        if error:
            viewStatus( self.statusbar, error )
            self.errorDialog( error )

    def onWCSave(self, entry):
        """Сохранение подключения к Citrix или WEB"""
        server = entry.get_text()
        protocol = entry.get_name()
        name  = self.builder.get_object( "entry_%s_name"  % protocol ).get_text()
        group = self.builder.get_object( "entry_%s_group" % protocol ).get_text()
        error = ""
        if name == "":
            error = _("Specify a name for the connection!")
        elif server == "":
            error = _("Server not specified!")
        elif self.searchName( name ):
            error = _("The same connection name is already in use!")
        else:
            parameters = { "name"     : name,
                           "protocol" : protocol,
                           "group"    : group,
                           "server"   : server }
            if hasattr( self, "fileCtor" ): #checking - edit or new connection
                if self.fileCtor: newfile = False
                else: newfile = True
            else: newfile = True
            if newfile:
                fileName = self.saveFileCtor( name, protocol, server )
            else:
                fileName = self.resaveFileCtor( name, protocol, server )
            options.saveInFile(fileName, parameters)
            self.setSavesToListstore()
            if group: self.initGroups()
            self.initSubmenuTray()
            viewStatus( self.statusbar, "%s (%s)..." % ( _("The connection is saved"), name ) )
            self.fileCtor = ""
        if error:
            viewStatus( self.statusbar, error )
            self.errorDialog( error )

    def onWCEdit(self, name, server, protocol, group ):
        """Функция изменения Citrix или WEB-подключения """
        if protocol == "CITRIX": index_tab = 6
        if protocol == "WEB":    index_tab = 9
        self.conn_note.set_current_page(index_tab)
        entry_serv  = self.builder.get_object( "entry_serv_%s"  % protocol )
        entry_name  = self.builder.get_object( "entry_%s_name"  % protocol )
        entry_group = self.builder.get_object( "entry_%s_group" % protocol )
        protocols   = self.builder.get_object( "combo_protocols" )
        protocols.set_active_id( str( index_tab ) )
        entry_serv.set_text(  server )
        entry_name.set_text(  name   )
        entry_group.set_text( group  )

    def onWCMenu(self, item):
        """Open WEB / CITRIX tab from main menu"""
        protocol = item.get_name()
        self.onWCEdit( "", "", protocol, "" )

    def onSaveConnect(self, *args):
        """Connect to save connection from main window or tray"""
        if type( args[ 0 ] ) == Gtk.TreeView: #from list_connect
            table, indexRow = args[0].get_selection().get_selected()
            if indexRow == None:
                viewStatus( self.statusbar, _("Select a connection from the list!") )
                return None
            else:
                nameConnect, fileCtor = table[ indexRow ][ 0 ], table[ indexRow ][ 4 ]
        else: #from tray
            nameConnect = args[ 1 ]
            fileCtor = self.filenameFromName( nameConnect )
        parameters = options.loadFromFile(fileCtor, self.window)
        if parameters is not None: #если файл .myc имеет верный формат
            parameters[ "name" ] = nameConnect
            parameters[ "file" ] = fileCtor
            try:
                name = changeProgram( parameters[ "protocol" ], parameters.get( "program", "" ) )
            except KeyError:
                protocol_not_found( nameConnect )
                return None
            server = parameters.get( "server", "" )
            if not server:
                server_not_found( nameConnect )
                return None
            if ( name == "RDP1" or name == "VMWARE" or name == "X2GO" ) and parameters.getboolean( "passwdsave" ):
                try:
                    parameters[ "passwd" ] = keyring.get_password( server, parameters.get( "username", "" ) )
                except Exception as e:
                    options.log.error( e )
                    password = ""
            viewStatus( self.statusbar, "%s \"%s\"..." % ( _("Connecting to"), nameConnect ) )
            connect = definition( name )
            if not check_global( "system_folder" ):
                self.writeConnectionInRecent( nameConnect, parameters[ "protocol" ] )
            connect.start( parameters, self.window )

    def onPopupMenu(self, widget, event):
        """Контекстное меню списка сохраненных подключений"""
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            menu = self.builder.get_object("menu_popup")
            if check_global( "system_folder" ) and not ROOT:
                self.builder.get_object( "menu_popup_edit"   ).set_sensitive( False )
                self.builder.get_object( "menu_popup_rename" ).set_sensitive( False )
                self.builder.get_object( "menu_popup_copy"   ).set_sensitive( False )
                self.builder.get_object( "menu_popup_del"    ).set_sensitive( False )
            if check_global( "stealth_mode" ) and not ROOT:
                self.builder.get_object( "menu_popup_text"   ).set_sensitive( False )
            menu.popup(None, None, None, None, event.button, event.time)

    def onPopupEdit(self, treeView):
        """Изменение выбранного подключения"""
        table, indexRow = treeView.get_selection().get_selected()
        if indexRow == None:
            viewStatus( self.statusbar, _("Select a connection from the list!") )
            return None
        else:
            nameConnect, self.fileCtor = table[ indexRow ][ 0 ], table[ indexRow ][ 4 ]
        parameters = options.loadFromFile(self.fileCtor, self.window)
        if parameters is not None: #если файл .myc имеет верный формат
            try:
                protocol = parameters [ "protocol" ].upper()
            except KeyError:
                protocol_not_found( nameConnect )
                return None
            if protocol in [ "CITRIX", "WEB" ]:
                try:
                    self.onWCEdit( nameConnect, parameters [ "server" ], protocol, parameters.get( "group", "" ) )
                except KeyError:
                    server_not_found( nameConnect )
                    return None
            else:
                analogEntry = self.AnalogEntry( protocol, parameters )
                self.onButtonPref( analogEntry, nameConnect )

    def onPopupCopy(self, treeView):
        """Копирование выбранного подключения"""
        table, indexRow = treeView.get_selection().get_selected()
        if indexRow == None:
            viewStatus( self.statusbar, _("Select a connection from the list!") )
            return None
        else:
            nameConnect, fileCtor = table[ indexRow ][ 0 ], table[ indexRow ][ 4 ]
        parameters = options.loadFromFile( fileCtor, self.window )
        if parameters is not None: #если файл .myc имеет верный формат
            try:
                protocol = parameters[ "protocol" ].upper()
            except KeyError:
                protocol_not_found( nameConnect )
                return None
            nameConnect = "%s (%s)" % ( nameConnect, _("copy") )
            if protocol in [ "CITRIX", "WEB" ]:
                try:
                    self.onWCEdit( nameConnect, parameters[ "server" ], protocol, parameters.get( "group", "" ) )
                except KeyError:
                    server_not_found( nameConnect )
                    return None
            else:
                analogEntry = self.AnalogEntry( protocol, parameters )
                self.onButtonPref( analogEntry, nameConnect )

    class AnalogEntry:
        """Класс с методами аналогичными методам Gtk.Entry и реализующий
           инициализацию сохраненных параметров подключения в окне параметров"""
        def __init__(self, name, parameters):
            self.name = name
            self.parameters = parameters
        def get_name( self ):
            return self.name
        def get_text( self ):
            try:
                return self.parameters[ "server" ]
            except KeyError:
                return ""
        def loadParameters( self ):
            return self.parameters

    def onPopupRemove(self, treeView):
        """Удаление выбранного подключения из списка, БД и файла с его настройками"""
        table, indexRow = treeView.get_selection().get_selected()
        if indexRow == None:
            viewStatus( self.statusbar, _("Select a connection from the list!") )
            return None
        else:
            name = table[ indexRow ][ 0 ]
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, _("Delete this connection:") )
        dialog.format_secondary_text(name)
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            fileMyc = table[ indexRow ][ 4 ]
            parameters = options.loadFromFile( fileMyc )
            try:
                keyring.delete_password( parameters.get( "server", "" ), parameters.get( "username", "" ) )
            except Exception as e:
                options.log.error( e )
            mycfile = "%s/%s" % ( WORKFOLDER, fileMyc )
            if os.path.isfile( mycfile ):
                os.remove( mycfile )
            autostart_shortcut = "%s/.config/autostart/%s.desktop" % ( HOMEFOLDER, name )
            if os.path.isfile( autostart_shortcut ):
                os.remove( autostart_shortcut )
            self.setSavesToListstore()
            options.log.info( "%s (%s)!", _("Connection deleted"), name )
            self.initSubmenuTray()
        dialog.destroy()

    def onPopupSave(self, treeView):
        """Creation desktop-file for the connection from popup menu"""
        dialog = Gtk.FileChooserDialog( _("Save a shortcut to this connection"), self.window,
            Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        current_folder = (HOMEFOLDER + DESKFOLDER.replace('$HOME','')).replace('"','')
        dialog.set_current_folder(current_folder)
        table, indexRow = treeView.get_selection().get_selected()
        if indexRow == None:
            viewStatus( self.statusbar, _("Select a connection from the list!") )
            return None
        else:
            nameConnect = table[ indexRow ][ 0 ]
        dialog.set_current_name(nameConnect + '.desktop')
        dialog.set_do_overwrite_confirmation(True) #запрос на перезапись одноименного файла
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = dialog.get_filename()
            name = name.replace(".desktop","")
            filename = name + ".desktop"
            self.createDesktopFile(filename, nameConnect, os.path.basename(name))
            viewStatus( self.statusbar, "%s \"%s\"..." % ( _("Saved in"), filename ) )
            options.log.info( "%s \"%s\" %s: \"%s\"", _("For connection"), nameConnect,
                              _("saved quick access shortcut"), filename )
        dialog.destroy()

    def onPopupText(self, treeView):
        """Open with Text Editor"""
        table, indexRow = treeView.get_selection().get_selected()
        if indexRow == None:
            viewStatus( self.statusbar, _("Select a connection from the list!") )
            return None
        else:
            name, fileMyc = table[ indexRow ][ 0 ], table[ indexRow ][ 4 ]
        editor = CONFIG.get( "editor", "pluma" )
        status = "%s \"%s\" %s..." %  ( _("The connection"), name, _("opens in a text editor") )
        options.log.info( status )
        try:
            Popen( [ editor, "%s/%s" % ( WORKFOLDER, fileMyc ) ] )
        except FileNotFoundError:
            status = "%s - %s - %s!" % ( _("The text editor"), editor, _("not found") )
            options.log.error( status )
        except PermissionError:
            status = "%s %s!" % ( _("The text editor"), _("is not specified") )
            options.log.error( status )
        viewStatus( self.statusbar, status )

    def onPopupAutostart( self, treeView ):
        """Configure connection autostart"""
        table, indexRow = treeView.get_selection().get_selected()
        if indexRow == None:
            viewStatus( self.statusbar, _("Select a connection from the list!") )
            return None
        else:
            name, fileMyc, protocol = table[ indexRow ][ 0 ], table[ indexRow ][ 4 ], table[ indexRow ][ 2 ]
            ##### for http://bugs.myconnector.ru/22 #############################
            if protocol == "FS" and ( CONFIG.get( "fs", "" ) == "caja" or
            check_output( "xdg-mime query default 'inode/directory'", shell=True,
            universal_newlines=True ).strip() == "caja-folder-handler.desktop" ):
                warning = Gtk.MessageDialog( self.window, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "%s " % _("Attention!") )
                warning.format_secondary_text("%s Caja.\n%s http://bugs.myconnector.ru/22" %
                                             ( _("There may be problems with the work of"), _("See") ) )
                warning.run()
                warning.destroy()
            #####################################################################
        parameters = options.loadFromFile( fileMyc )
        state = parameters.getboolean( "autostart" )
        dialog = Gtk.MessageDialog( self.window, 0, Gtk.MessageType.QUESTION,
                                    Gtk.ButtonsType.YES_NO, "%s - \"%s\"" % ( _("Connection autostart"), name ) )
        status = _("enabled") if state else _("disabled")
        question = _("Turn it off?") if state else _("Turn it on?")
        dialog.format_secondary_text( "%s: %s. %s" % ( _("Current status"), status, question ) )
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            new_state = not state
            parameters[ "autostart" ] = str( new_state )
            options.saveInFile( fileMyc, parameters )
            shortcut = "%s/.config/autostart/%s.desktop" % ( HOMEFOLDER, name )
            if new_state:
                os.makedirs( "%s/.config/autostart" % HOMEFOLDER, exist_ok = True )
                self.createDesktopFile( shortcut, name, name )
            else:
                if os.path.isfile( shortcut ):
                    os.remove( shortcut )
        dialog.destroy()

    def listFilter(self, model, iter, data):
        """Функция для фильтра подключений в списке"""
        row = ''
        if self.currentFilter == '':
            return True
        else:
            for i in range(4):
                row += model[iter][i] #объединяем поля в одну строку для поиска в ней символов
            #https://ru.stackoverflow.com/questions/812170
            en2ru = dict( zip( map( ord, "qwertyuiop[]asdfghjkl;'zxcvbnm,./`" 'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~' ),
                                          "йцукенгшщзхъфывапролджэячсмитьбю.ё" "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё" ) )
            ru2en = dict( zip( map( ord, "йцукенгшщзхъфывапролджэячсмитьбю.ё" "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё" ),
                                          "qwertyuiop[]asdfghjkl;'zxcvbnm,./`" 'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~')  )
            if row.upper().find( self.currentFilter.translate( en2ru ).upper()) != -1:
                return True
            elif row.upper().find( self.currentFilter.translate( ru2en ).upper()) != -1:
                return True
            else: return False

    def onSearchConnect(self, entry):
        """Функция осуществления поиска по списку подключений"""
        self.currentFilter = entry.get_text()
        self.filterConnections.refilter()

    def onSearchReset(self, entry):
        """Сброс фильтрации и очистка поля поиска"""
        entry.set_text('')
        self.currentFilter = ''
        self.filterConnections.refilter()

    def inputName(self, button):
        """Функция, активирующая кнопку Сохранить после ввода имени соединения"""
        if not check_global( "system_folder" ) or ROOT:
            button.set_sensitive( True )

    def onWiki(self, *args):
        """Открытие wiki в Интернете"""
        os.system ('xdg-open "http://wiki.myconnector.ru/"')

    def onShowWindow(self, *args):
        if self.window.is_active():
            self.onHideWindow(self)
        else: self.showWin()

    def onHideWindow(self, *args):
        if check_option( 'tray' ):
            self.window.hide()
            if not self.trayDisplayed: self.trayDisplayed = self.initTray()
            return True
        else:
            self.quit()

    def onButtonDefault(self, entry):
        """Сохранение параметров подключений по умолчанию"""
        name = entry.get_name()
        args = self.applyPreferences( name )
        for key in args.keys():
            CONFIGS[ name ][ key ] = args[ key ]
        config_save()
        viewStatus( self.statusbar, _("The default settings are saved.") )

    def saveKeyring(self, parameters):
        """Сохранение пароля в связу ключей и отметки об этом в файл подключения"""
        if parameters.get( "passwdsave", "False" ) == "True":
            try:
                keyring.set_password( parameters [ "server" ], parameters [ "username" ], parameters [ "passwd" ] )
            except Exception as e:
                options.log.error( e )

        else:
            try:
                keyring.delete_password( parameters [ "server" ],  parameters [ "username" ] )
            except Exception as e:
                options.log.error( e )

    def onDeveloper(self, *args):
        """Кнопка 'Связь с разработчиком'"""
        os.system ('xdg-open "mailto:ek@myconnector.ru"')

    def onBugs(self, *args):
        """Кнопка 'Сообщить об ошибке'"""
        os.system ('xdg-open "http://bugs.myconnector.ru/"')

    def fixServerForLocal(self, widget):
        """Установка значения поля сервер в 'localhost' при выборе 'Локальный каталог'"""
        if self.FS_type.get_active_id() == "file" and not widget.get_text() : widget.set_text("localhost")

    def onKiosk(self, *args):
        """Button 'Mode KIOSK'"""
        from myconnector.kiosk import Kiosk
        window = Kiosk( self.window )

    def filenameFromName( self, name ):
        """Определение имени конфигурационного файла подключения по имени подключения"""
        records, groups = getSaveConnections()
        for record in records:
            if record[0] == name:
                return record[4]
        return False

    def searchName( self, name ):
        """Существует ли подключение с указанным именем"""
        thereIsFile = self.fileCtor if hasattr( self, "fileCtor" ) else ""
        records, groups = getSaveConnections( thereIsFile )
        for record in records:
            if record[0] == name:
                return True
        return False

    def protocolChange( self, widget ):
        """Change protocol on main window"""
        self.conn_note.set_current_page( int( widget.get_active_id() ) )

    def importFromConnector( self, connections ):
        """Autoimport connections from Connector"""
        dialog = Gtk.MessageDialog( self.window, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO,
                                    "%s (Connector)." % _("Connection files of the old version of the program were detected") )
        dialog.format_secondary_text( _("Should I import them into this version?") )
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            for connect in open( connections ):
                try:
                    record   = connect.strip().split( ":::" )
                    name     = record[ 0 ].replace( "/", "" )
                    ctorfile = "%s/.connector/%s" % ( HOMEFOLDER, record[ 3 ] )
                    mycfile  = "%s/%s_import.myc" % ( WORKFOLDER, name.lower() )
                    code     = call( "ctor2myc %s %s >> %s/import.log 2>&1" % ( ctorfile, mycfile, LOGFOLDER ), shell = True )
                    if code == 0:
                        with open( mycfile, "a" ) as f:
                            print( "name = %s" % name, file = f )
                except Exception as e:
                    options.log.error( e )
            self.setSavesToListstore()
        dialog.destroy()

    def onFind( self, widget ):
        """Set focus to search entry"""
        widget.grab_focus()

    def onChangeSecutiry( self, sec_list ):
        """Disable/enable checkbox 'disable_nla' in relation to security"""
        sec = sec_list.get_active_id()
        if sec in ( "nla", "ext" ):
            self.RDP_nla.set_active( False )
            self.RDP_nla.set_sensitive( False )
        else:
            self.RDP_nla.set_sensitive( True )

    def errorDialog( self, text ):
        from myconnector.dialogs import Error
        err = Error( text )
        err.run()

    def onRecentFile( self, item ):
        """Opening a recent file (for connect) from menu"""
        filename = item.get_current_uri().replace( "file://", "" )
        Popen( [ APP, filename ] )

    def writeConnectionInRecent( self, name, protocol ):
        """Write the connection name to the recent connections file"""
        fname = "%s:::%s\n" % ( protocol, name )
        if os.path.exists( RECENTFILE ):
            with open( RECENTFILE ) as recent_file:
                recent_connections = recent_file.readlines()
            try:
                recent_connections.remove( fname )
            except:
                pass
            recent_connections.insert( 0, fname )
        else:
            recent_connections = [ fname ]
        with open( RECENTFILE, "w" ) as recent_file:
            recent_file.writelines( recent_connections[ 0:5 ] )
        self.initRecentMenu()

    def initRecentMenu( self ):
        """Initial menu of the recent connections"""
        for item in self.recent_menu.get_children(): item.destroy()
        if os.path.exists( RECENTFILE ):
            with open( RECENTFILE ) as recent_file:
                recent_connections = recent_file.readlines()
        else:
            empty = Gtk.MenuItem( " " )
            empty.set_sensitive( False )
            self.recent_menu.append( empty )
            return( 1 )
        for connection in recent_connections:
            try:
                protocol, name = connection.strip().split(':::')
                connection_item = Gtk.ImageMenuItem( name )
                image = Gtk.Image()
                image.set_from_pixbuf( GdkPixbuf.Pixbuf.new_from_file( "%s/%s.png" % ( ICONFOLDER, protocol )))
                connection_item.set_image( image )
                connection_item.connect( "activate", self.onSaveConnect, name )
                self.recent_menu.append( connection_item )
            except:
                pass
        self.recent_menu.show_all()

    def onPopupRename( self, treeView ):
        """Rename connection in main window"""
        table, index = treeView.get_selection().get_selected()
        if index == None:
            viewStatus( self.statusbar, _("Select a connection from the list!") )
            return None
        else:
            old_name = table[ index ][ 0 ]
        base_model_iter = table.convert_iter_to_child_iter( index ) #for change after save
        from myconnector.dialogs import Rename
        rename = Rename( old_name )
        self.window.set_sensitive( False )
        new_name = rename.run()
        error = ""
        if new_name == "":
            error = _("Specify a name for the connection!")
        elif self.searchName( new_name ) and ( new_name != old_name ):
            error = _("The same connection name is already in use!")
        elif new_name and ( new_name != old_name ):
            fileMyc = "%s/%s" % ( WORKFOLDER, table[ index ][ 4 ] )
            Popen( ["sed", "-i", "s/^name.*/name = %s/g" % new_name, fileMyc ] )
            self.filterConnections.set_value( base_model_iter, 0, new_name )
            info = _("The connection was renamed")
            options.log.info( "%s (%s -> %s)", info , old_name, new_name )
            viewStatus( self.statusbar, "%s." % info )
        if error:
            viewStatus( self.statusbar, error )
            self.errorDialog( error )
        self.window.set_sensitive( True )

    def onWikiOffline(self, *args):
        """Open local documentation"""
        Popen( [ "xdg-open", LOCALDOCS ] )

def connect( name ):
    """Start connection by name"""
    myc_file = Gui.filenameFromName( None, name )
    if myc_file:
        options.log.info( "%s: %s" % ( _("Starting a saved connection"), name ) )
        connectFile( myc_file )
    else:
        options.msg_error( "\"%s\": %s!" % ( name, _("no connection with this name was found") ), options.log.error )
        exit( 1 )

def main( name ):
    """Main function"""
    if name:
        if name[0] == "'": name = name.replace( "'", "" ) #for KIOSK (mode=2)
        if os.path.isfile( name ): openFile( name )
        else:
            options.msg_error( "\"%s\": %s!" % ( name, _("file not found") ), options.log.error )
            exit( 1 )
    else:
        gui = Gui()
        initSignal(gui)
        gui.run(None)
        options.checkLogFile(LOGFILE); options.checkLogFile(STDLOGFILE)

