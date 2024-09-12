# Task_board
Создаем свой собственный канбан

Для запуска API потребуется:

1) создать конфиг файл *settings.toml* (чуть позже запилю скрипт, который его сам генерит),

ключи будут следующие
```
[API]
host = "127.0.0.1"
port = 5000 +
debug = false

[MYSQL]
host = "localhost"
user = "db_user_name"
password =  "db_passwd"
database = "db_name"

[JWT]
secret = "your_secret_key"
alg = "HS256"

[TEST_DB]
host = "localhost"
user = "test_db_user"
password = "test_db_passwd"
database = "test_db_name"
echo = false
```
2) установить venv, прописав команду в консоли
```
python3 -m venv venv
```
затем активировать его
```
source venv/bin/activate
```

3) установить нужные зависимости командой
```
pip install -r requirements.txt
```
4) прописать proxypass для вашего порта */to_do_list* в конфиге вашего вебсервера
5) запустить файл main.py

## Документация API (swagger)
*to_do_list/docs*