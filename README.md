Code is bad, need refactoring and commenting.
But working :)

Требуются Python3, pip и Tesseract

# Установка и запуск

## Установка необходимых компонентов

Установка необходимых компонентов в Ubuntu или Debian:

`sudo apt install build-essential python3-dev python3-pip python3-venv tesseract-ocr tesseract-ocr-eng tesseract-ocr-rus`

## Создание виртуального окружения

В папке с проектом создаётся виртуальное окружение командой:

`python3 -m venv .`

Активация:

`source bin/activate`

Установка необходимых python-пакетов в виртуальное окружение:

`pip install -r requirements.txt`

## Работа с проектом

Для активации виртуального окружения необходимо выполнить

`source bin/activate`

Запуск скрипта:

`python bot.py`

Не забудьте указать настройки скрипта в файле `bot.txt`.
`API_TOKEN` для Telegram можно получить с помощью бота [@BotFather](https://telegram.me/botfather)

**Важно**: Когда вы закончили работу в виртуальном окружении проекта,
перед переключением в глобальное окружение или другое виртуальное,
его сперва нужно деактивировать:

`deactivate`
