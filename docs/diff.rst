.. MyConnector
.. Copyright (C) 2014-2021 Evgeniy Korneechev <ek@myconnector.ru>

.. This program is free software; you can redistribute it and/or
.. modify it under the terms of the version 2 of the GNU General
.. Public License as published by the Free Software Foundation.

.. This program is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with this program. If not, see http://www.gnu.org/licenses/.

.. |date| date:: %d.%m.%Y

.. |connector|   image:: _img/connector.png
.. |right|       image:: _img/right.png
.. |myconnector| image:: _img/myconnector.png

.. _rst-diff:

Отличия от Connector
====================

|connector| |right| |myconnector|

MyConnector является обновленной версией программы `Connector <https://github.com/ekorneechev/connector>`_. Основные отличия (на |date|):

* обновленный графический интерфейс;
* текстовый формат файлов подключений ``.myc`` (с автоимпортом подключений из Connector), что означает возможную правку и создание подключений с помощью любого текстового редактора (плюс возможность открыть через контекстное меню списка подключений);
* возможность группировки в списке сохраненных подключений;
* импорт подключений RDP, Remmina (и формата .ctor);
* интерфейс командной строки для настройки :ref:`rst-kiosk`;
* X2GO-подключение (консольный клиент pyhoca-cli);
* добавлен англоязычный интерфейс (i18n);
* возможность настройки автозапуска подключения при входе пользователя;
* режим прослушивания для vncviewer.

С основными отличиями можете ознакомиться на странице первого кандидата в релиз `2.0.rc0 <https://github.com/MyConnector/MyConnector/projects/3>`_.

