.. MyConnector
.. Copyright (C) 2014-2023 Evgeniy Korneechev <ek@myconnector.ru>

.. This program is free software; you can redistribute it and/or
.. modify it under the terms of the version 2 of the GNU General
.. Public License as published by the Free Software Foundation.

.. This program is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU General Public License for more details.

.. You should have received a copy of the GNU General Public License
.. along with this program. If not, see http://www.gnu.org/licenses/.

.. _rst-cli:

Использование в командной строке
================================

Настроен ``bash completion`` (автоподстановка параметров по нажатию клавиши :guilabel:`&Tab`).

Ниже приведены страницы документации, входящие в состав пакета.

::

    $ myconnector --help
    usage: myconnector [options]

    MyConnector - клиент удаленного рабочего стола.

    positional arguments:
      FILE                  имя файла подключения (.myc, .remmina, .rdp)

    optional arguments:
      -h, --help            показать эту справку и выйти
      -c CONNECTION, --connection CONNECTION
                            имя сохраненного подключения
      -f FILE, --file FILE  имя файла подключения (.myc, .remmina, .rdp)
      -l, --list            список сохраненных подключений
      -e, --edit            редактировать конфигурационный файл (будет использоваться
                            редактор, указанный в VISUAL или EDITOR, по умолчанию vi)
      --kiosk <option>      Управление режимом КИОСКа ('--kiosk help' для подробной информации)
      -v, --version         показать версию приложения
      -d, --debug           отображение журнала работы в режиме реального времени
      -q, --quit            закрыть все копии приложения

    Не указывайте опций для запуска графического интерфейса.

    Copyright (C) 2014-2023 Evgeniy Korneechev <ek@myconnector.ru>

    $ man myconnector
    НАИМЕНОВАНИЕ
           MyConnector - remote desktop client.

    СИНТАКСИС
           myconnector [options]

    ОПИСАНИЕ
           Программа-фронтэнд  для  удаленного  администрирования  компьютеров с различными операционными системами. Поддерживается большинство распространенных типов подключения (RDP, VNC,
           X2GO, Citrix, VMware, etc).

    ОПЦИИ
           <без опций>
              Запустить программу в режиме графического интерфейса.

           -c CONNECTION, --connection CONNECTION
              Подключиться к сохраненному подключению по его имени.

           FILE, -f FILE, --file FILE
              Подключиться с помощью файла подключения (.myc, .remmina, .rdp).

           -l, --list
              Вывести список сохраненных подключений.

           -e, --edit
              Редактировать конфигурационный файл.

           --kiosk <option>
              Управление режимом КИОСК (подробнее: '--kiosk help').

           -v, --version
              Вывести информацию о версии программы и завершить работу.

           -d, --debug
              Запуск программы в режиме отображения журналов работы в реальном времени.

           -h, --help
              Вывести краткую справку и завершить работу.

           -q, --quit
              Закрыть все существующие копии программы.

    $ myconnector --kiosk help
    myconnector --kiosk - Управление режимом КИОСКа

    Использование: myconnector --kiosk <option>

    Опции:
      enable        включить простой режим (запуск программы MyConnector);
      edit          редактировать конфигурационный файл (будет использоваться
                    редактор, указанный в VISUAL или EDITOR, по умолчанию: vi);
      disable       отключить режим;
      status        показать текущий статус режима;
      help          показать эту справку и выйти.

    См. также: man myconnector-kiosk

    Copyright (C) 2014-2023 Evgeniy Korneechev <ek@myconnector.ru>

    $ man myconnector-kiosk
    НАИМЕНОВАНИЕ
           myconnector-kiosk - Mode KIOSK for 'MyConnector'

    ОПИСАНИЕ
           Конфигурационный файл режима КИОСК программы MyConnector - /etc/myconnector/kiosk.conf

           mode - один из следующих режимов работы:
              "0" - КИОСК отключен
              "1" - запуск программы MyConnector в режиме КИОСК
              "2" - соединение с сохраненным подключением
              "3" - ВЕБ-киоск

           file - файл подключения для mode=2

           url - URL для ВЕБ-киоска

           user - имя пользователя для режима КИОСК

           autologin - управление автовходом пользователя
              True,Yes - включен
              False,No - отключен

           ctrl_disabled - отключение "Ctrl" в ВЕБ-киоске
              True,Yes - отключен
              False,No - включен
