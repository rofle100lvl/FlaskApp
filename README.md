# FlaskApp
Проект выполнен на базе Python 3.8, Flask 1.1.2 с использованием SQLite3

Локальный запуск:
-----------------
Для локального тестирования достаточно скачать проект, активировать виртуальное окружение, подключить все зависимости из requirments.txt.

Развёртывание на сервере:
-------------------------
Для развёртывании на сервере необходимо подключить apache2 и wsgi, затем перенести FlaskApp в /var/www/

Также необходимо задать cfg для apache сделать это можно командой <b>sudo nano /etc/apache2/sites-available/FlaskApp.conf</b>

После этого перезапускаем службу apache командой service apache2 restart и проект успешно развёрнут на сервере

Для вопросов и предложений:
>tg: @NeKrutoOchen
>vk: https://vk.com/rofle100lvl
