# Телеграм бот для проекта Concert Mates
Для запуска обязательно должен быть в корне проекта файл **.env** с указанным в нём токеном бота, формата
**BOT_TOKEN="_TOKEN_"**

## Развертка
```bash 
pip install poetry 
poetry install
```

## Запуск бота
```bash
python bot.py
```

## Запуск слушателя брокера сообщений
```bash
python broker_listener.py
```
