.. MyConnector
.. Copyright (C) 2014-2020 Evgeniy Korneechev <ek@myconnector.ru>

.. This program is free software; you can redistribute it and/or
.. modify it under the terms of the version 2 of the GNU General
.. Public License as published by the Free Software Foundation.

.. This program is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with this program. If not, see http://www.gnu.org/licenses/.

Использование в командной строке
================================

::

    $ myconnector --help
    usage: myconnector [options]

    MyConnector - remote desktop client.

    positional arguments:
      FILE                  name of the file (.myc, .remmina, .rdp)

    optional arguments:
      -h, --help            show this help message and exit
      -c CONNECTION, --connection CONNECTION
                        name of the saved connection
      -f FILE, --file FILE  name of the file (.myc, .remmina, .rdp)
      -l, --list            list of the saved connections
      --kiosk <option>      KIOSK mode control ('--kiosk help' for more information)
      -v, --version         show the application version
      -d, --debug           show log files online
      -q, --quit            quit the application

    Do not specify parameters for starting the GUI.

    $ myconnector --kiosk help
    myconnector --kiosk - MyConnector KIOSK mode control

    Usage: myconnector --kiosk <option>

    Options:
      enable        enable the standalone mode;
      edit          edit config file for enable/disable the mode (will use
                    any the editor defines by VISUAL or EDITOR, default: vi);
      disable       disable the mode;
      status        display current status of the mode;
      help          show this text and exit.

    See also: man myconnector-kiosk
