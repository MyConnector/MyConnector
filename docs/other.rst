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

Прочие возможности
==================

Открытие файлов .myc, .ctor, .rdp и .remmina

В программе есть возможность открытия файлов .ctor, .rdp и .remmina. Для этого в пункте меню "Файл" выберите "Открыть" либо дважды щелкните на нем в файловом менеджере. После выбора необходимого файла будет произведена попытка соединения - если файл не содержит параметров или соединение производится не через настроенную программу, то отобразится соответствующая ошибка. В другом случае - произойдет успешное подключение к серверу.

Импорт файла .ctor

Вы также можете не только подключиться через сохраненный файл, но и импортировать параметры из этого файла либо для изменения параметров, либо для сохранения в свой список подключений. Для этого в пункте меню "Файл" выберите "Импорт...", после этого откроется диалог открытия файла, а после его выбора откроется окно дополнительных параметров того типа подключения, который записан в данный файл.

Ведение логов

Располагаются в рабочей папке программы: ~/.myconnector/logs. Файл all.log содержит отладочную информацию от запускаемых программ, а myconnector.log - информацию по работе самого MyConnector (три уровня сообщений: info, warning и error) и ошибки в его работе. В "Параметрах программы" есть возможность отключения ведения логов.

Справка по программе Connector

Ссылка на данную страницу Wiki всегда доступна из приложения - пункт меню "Справка". Там же краткие сведения о программе и об ее разработчике. Также справочную страницу можно просмотреть и на компьютере::

    man myconnector
    myconnector --help