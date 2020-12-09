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

.. _Receiver: https://www.citrix.com/downloads/citrix-receiver/linux/
.. _`Workspace App`: https://www.citrix.com/downloads/workspace-app/linux/
.. _`VMware Horizon Client`: https://my.vmware.com/web/vmware/downloads/details?downloadGroup=CART21FQ3_LIN64_550&productId=863

Установка
=========

~~~~~~~~~
Alt Linux
~~~~~~~~~

Актуальная версия пакета всегда доступна в репозиториях::

    $ su -
    # apt-get update
    # apt-get install myconnector

~~~~~~~~~~~~~~~~~~~
Linux Mint & Ubuntu
~~~~~~~~~~~~~~~~~~~

Для оптимальной работы приложения необходимо установить следующие пакеты:

* libgtk-3-0 (версия 3.10 и выше);
* python3 (>=3.2);
* python3-gi (>=3.2);
* remmina (>=1.0);
* freerdp-x11 (>=1.2.0) (для Ubuntu14/Mint17), freerdp2-x11 (Ubuntu18/Mint19);
* vncviewer;
* python3-keyring.

Все данные программы можно установить либо в *Менеджере пакетов Synaptic*, либо через командную строку::

    $ sudo apt-get update
    $ sudo apt-get install libgtk-3-0 python3 python3-gi remmina vncviewer python3-keyring

Не обязательными, но необходимыми для полного функционала программы являются:

* Citrix Receiver_/`Workspace App`_ (icaclient)
* `VMware Horizon Client`_ (vmware-view)

После этого можно устанавливать MyConnector. Готовый бинарный пакет для установки можно скачать `здесь <http://get.myconnector.ru>`_. Также можно собственноручно собрать пакет по `инструкции <https://github.com/MyConnector/MyConnector/blob/master/deb/README.md>`_ или установить напрямую из исходников с помощью утилиты `make`.

~~~~~~~~~~
git & make
~~~~~~~~~~

После установки всех зависимостей (для mint/ubuntu - см. выше, для alt - указаны в `spec-файле <https://github.com/MyConnector/MyConnector/blob/master/myconnector.spec#L16>`_ в секциях requires)::

    $ git clone https://github.com/ekorneechev/MyConnector
    $ cd MyConnector
    $ git checkout <release> # по умолчанию 'master', список релизов: `git tag -l`
    $ sudo make install


