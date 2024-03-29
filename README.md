# WeatherBot

**[WeatherBot](https://test.pypi.org/project/WeatherBotKB/)** — простой инструмент на основе [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI), 
который позволяет запустить собственного бота, пользователи которого могут получать  прогноз погоды из любой точки мира в желаемое время. 

## Описание

**WeatherBot**, как и другие Telegram-боты, реализован на взаимодействии пользователя и бота посредством чата Telegram.
  

Бот предоставляет пользовательское меню для удобного обращения с его командами.


На протяжении работы с ботом пользователю предоставляются подсказки, упрощая тем самым
работу с интерфейсом.

Команды представлены на естественном языке, доступном каждому пользователю. 


С помощью этих команд можно составить удобное для себя расписание,
по которому будет высылаться прогноз погоды.


Список доступных команд:
* **Старт** *(/start)* — команда, инициирующая начало работы с ботом;
* **Добавить** — команда для добавления прогноза погоды, с указанием города и времени;
* **Удалить** — команда для удаления из расписания события отправления сообщения с прогнозом;
* **Изменить** — команда для изменения города и/или времени для существующего прогноза из списка.

Ознакомиться с документацией вы можете по [ссылке](https://studentwebmirea.000webhostapp.com/)

## Установка

Используйте менеджер пакетов [pip (The Python Package Installer)](https://pip.pypa.io/en/stable/) 
для установки WeatherBot.

```bash
pip install -i https://test.pypi.org/simple/ WeatherBotKB
```

## Зависимости проекта

*requirements.txt*
```bash 
requests
pyTelegramBotAPI
```
