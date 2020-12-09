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

Список сохраненных подключений
==============================

Расположен в нижней части главного окна программы.

Сохраненные подключения в списке представляют собой файлы с расширением .myc, сохраняемые в домашней папке текущего пользователя в папке .myconnector. Эти файлы возможно открывать на других компьютерах с установленным MyConnector.

При двойном щелчке на одном из подключений произойдет запуск требуемой программы для соединения (или нажатие правой кнопкой мыши на нужном соединении и далее выбрать пункт меню "Подключение").

Также через нажатие правой кнопки мыши на любом из сохраненных соединений, Вы можете выбрать пункт "Изменить" - тогда откроется окно дополнительных настроек данного подключения с заполненными полями. При выборе пункта "Копировать" - откроется такое же окно, однако при сохранении добавится новое подключение с измененными Вами параметрами. При выборе пункта "Удалить" - Вы удалите подключение из списка.

Пункт данного меню "Сохранить ярлык" позволяет создать кнопку запуска приложения MyConnector с быстрым подключением к выбранному соединению в любом месте на Вашем компьютере (по умолчанию на рабочем столе). Также это можно сделать простым перетаскиванием подключения в нужное место. Формат команды::

    myconnector -c <имя_подключения>

