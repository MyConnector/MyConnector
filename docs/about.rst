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

.. |copy| unicode:: 0xA9
.. |name| replace:: MyConnector

.. _FreeRDP: https://www.freerdp.com/
.. _RealVNC: https://www.realvnc.com/
.. _TigerVNC: https://tigervnc.org/
.. _Remmina: https://remmina.org/
.. _Receiver: https://www.citrix.com/downloads/citrix-receiver/linux/
.. _`Workspace App`: https://www.citrix.com/downloads/workspace-app/linux/
.. _`VMware Horizon Client`: https://my.vmware.com/web/vmware/downloads/details?downloadGroup=CART21FQ3_LIN64_550&productId=863

Описание
========

|name| - инструмент системного администратора для осуществления удаленного доступа к компьютерам с различными операционными системами с использованием распространенных типов подключения - таких как RDP, VNC, NX, XDMCP, SSH, SFTP, SPICE и технологий Citrix и VMware. C помощью |name| также есть возможность подключения к web-ресурсам и файловым серверам (:ref:`rst-fs`).

Преимущества данной программы:

* все необходимые программы удаленного доступа собраны в одной программе - |name|, нет необходимости искать нужную;
* есть возможность как быстрого подключения, так и с определенными параметрами;
* GUI-интерфейс для работы с программой FreeRDP (удаленный доступ по протоколу RDP);
* возможность сохранять кнопку быстрого подключения в любое место компьютера;
* ведение списка сохраненных подключений с возможностью группировки;
* ведение логов, как самой программы, так и каждого подключения;
* :ref:`rst-kiosk`.

Программа написана на Python (3-ей версии) с использованием GTK+ для графического интерфейса.

|name| является программой, реализующей интерфейс для пользователя к предустановленным программам для запуска их с введенными параметрами. Такими программами на данный момент являются:

* FreeRDP_;
* Клиенты VNC - RealVNC_ или TigerVNC_;
* Remmina_;
* Citrix Receiver_/`Workspace App`_ (ICA Client);
* `VMware Horizon Client`_.

Copyright |copy| 2014-2020 Evgeniy Korneechev <ek@myconnector.ru>
