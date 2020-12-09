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

Доступ к файловым ресурсам
==========================

Имеется возможность подключения к сетевым файловым ресурсам, организованным по распространенным протоколам: FTP, SMB, WebDAV и AFP (все поддерживаемые файловым менеджером caja в среде MATE).

Программа для открытия ресурсов указывается в параметрах программы. По умолчанию, устанавливается команда xdg-open.

Для подключения к сетевым файловым ресурсам в строке адреса (как на главном окне, так и в дополнительных параметрах) обязательно указание протокола подключения:

* ``ftp://`` - для подключения к FTP-серверу;
* ``sftp://`` - для подключения по протоколу SFTP;
* ``smb://`` - ресурсы Windows, доступные по протоколу SMB;
* ``dav://`` или ``davs://`` - подключение через WebDAV (расширение протокола HTTP или HTTPS);
* ``afp://`` - доступ к файлам Mac OS (протокол AFP);
* ``file://`` - открытие локального каталога (например, ``file:///home/user``).

Для быстрого подключения из главного окна программы можно использовать следующий формат адреса (в квадратных скобках указываются необязательные параметры, их также можно указать в окне дополнительных настроек подключения)::

    Протокол://[Имя_пользователя@]Сервер[:Порт]/[Папка]
