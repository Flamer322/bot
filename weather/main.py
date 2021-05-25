from weather import config
from weather.config import *

print("Starting")

bot = telebot.TeleBot(config.token)

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INT,
    city TEXT,
    time_h TEXT,
    time_m TEXT);
""")
conn.commit()


@bot.message_handler(content_types=["text"])
def start(message):
    """
    adfduksaghio

    :param message:soobshenie
    :return:govno
    """
    if message.text == "/start":
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        list_items = ["Добавить", "Удалить", "Изменить"]
        for item in list_items:
            markup.add(item)
        bot.send_message(message.chat.id, "Привет", reply_markup=markup)
    elif message.text == "Добавить":
        set_city(message)
    elif message.text == "Удалить":
        del_st(message)
    elif message.text == "Изменить":
        bot.send_message(message.chat.id, "WIP")
    else:
        bot.send_message(message.from_user.id, "Начните работу с ботом\n\nИспользуйте команду /start")


def del_st(message):
    """"Удаление записи с прогнозом погоды из базы данных

    Принимает на вход сообщение, содержащее информацию о прогнозе, после чего удаляет нужный прогноз из расписания.
    """
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT city, time_h, time_m FROM users WHERE user_id = ?", (message.from_user.id,))
    entries = cur.fetchall()
    if not entries:
        bot.send_message(message.from_user.id, "Вы не добавляли никаких прогнозов")
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Я передумал(а)")
        for entry in entries:
            markup.add(entry[0] + "\n" + entry[1] + ":" + entry[2])
        bot.send_message(message.chat.id, "Выбери прогноз, который нужно удалить", reply_markup=markup)
        bot.register_next_step_handler(message, start)


def set_city(message):
    """Функция установки города

    Принимает на вход сообщение, содержащее информацию о городе, после чего вызывает функцию получения города get_city()
    """
    bot.send_message(message.from_user.id, "Укажите Ваш город")
    bot.register_next_step_handler(message, get_city)


def get_city(message):
    """"Функция получения города и проверки его корректности

    Принимает на вход строковую переменную с информацией о городе,
    после чего вызывает функцию установки времени set_time() или выводит сообщение о неверном вводе города.
    """
    if message.text == "/start":
        return start(message)

    city = abb_to_city(message.text)
    city_id = get_city_id(config.city)
    if not city_id:
        wrong_city(message)
    elif config.changed:
        keyboard_confirmation(message)
        config.changed = False
    else:
        set_time(message)


def set_time(message):
    """Функция установки времени для отправки сообщения с прогнозом погоды

    Принимает на вход сообщение, содержащее информацию о времени,
    после чего вызывает функцию получения времени.
    """
    bot.send_message(message.from_user.id, "Выберите время (Москва, UTC+3), в которое Вы желаете получать прогноз"
                                     "\n\nУкажите время в формате ЧЧ:ММ")
    bot.register_next_step_handler(message, get_time)


def get_time(message):
    """"Функция получения времени и проверки его корректности

    Принимает на вход строковую переменную с информацией о времени,
    после чего вызывает функцию подтверждения keyboard_confirmation() или выводит сообщение о неверном вводе времени.
    """
    if message.text == "/start":
        return start(message)
    if re.fullmatch(r"^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", message.text):
        separator_index = message.text.find(":")
        config.time_h = message.text[0:separator_index]
        config.time_m = message.text[separator_index + 1:len(message.text)]

        if int(config.time_h) < 10:
            config.time_h = "0" + config.time_h

        if int(config.time_m) < 10:
            config.time_m = "0" + config.time_m

        keyboard_confirmation(message)
    else:
        wrong_time(message)


def keyboard_confirmation(message):
    """Функция подтверждения добавления желаемого прогноза

    Принимает на вход сообщение (информацию об отправителе сообщения), выводит две кнопки "Да" и "Нет",
    результат выбора которых передаётся в обработчик ответов.
    """
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
    keyboard.add(key_yes)
    # key_set_city = types.InlineKeyboardButton(text="Изменить город", callback_data="set_city")
    # keyboard.add(key_set_city)
    # key_set_time = types.InlineKeyboardButton(text="Изменить время", callback_data="set_time")
    # keyboard.add(key_set_time)
    key_no = types.InlineKeyboardButton(text="Нет", callback_data="no")
    keyboard.add(key_no)

    question = "Ваш город " + config.city + ".\nВы хотите получать прогноз в " + \
               config.time_h + ":" + config.time_m + ".\n\nВерно?"
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


def wrong_city(message):
    """Функция информирования о неправильном вводе города

    На вход получает информацию об отправителе сообщения,
    после чего передаёт обработчику информацию о вызове функции получения города.
    """
    bot.send_message(message.from_user.id, "Неправильное название города."
                                     "\nПожалуйста, попробуй ещё раз")
    bot.register_next_step_handler(message, get_city)


def wrong_time(message):
    """Функция информирования о неправильном вводе времени

    На вход получает информацию об отправителе сообщения,
    после чего передаёт обработчику информацию о вызове функции получения времени.
    """
    bot.send_message(message.from_user.id, "Неправильно введено время."
                                     "\nПожалуйста, введите время ещё раз")
    bot.register_next_step_handler(message, get_time)


def get_city_id(city):
    """Функция получения идентификатора города

    На вход получает сообщение с информацией о городе,
    после чего отправляет GET-запрос к OpenWeatherMap API, в результате получает идентификатор
    или сообщение о вызванном исключении, если не удалось получить JSON с информацией.
    """
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': config.key})
        data = res.json()
        city_id = data['list'][0]['id']
        return city_id
    except Exception as e:
        print("Exception (find):", e)
        pass


def get_weather(city):
    """Функция получения погоды

    На вход получает сообщение с информацией о городе,
    после чего отправляет GET-запрос к OpenWeaterMap API, в результате получает данные о погоде
    или сообщение о вызванном исключении, если не удалось получить JSON с информацией.
    """
    city_id = get_city_id(city)
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': config.key})
        data = res.json()
        conditions = data['weather'][0]['description']
        temp = round(data['main']['temp'])
        return (conditions, temp)
    except Exception as e:
        print("Exception (weather):", e)
        pass


def abb_to_city(message):
    """Функция преобразования сокращений в название города

    На вход получает сообщение, содержащее сокращённое название города, проверяет его наличие в словаре
    и, в случае успеха, возвращает название города.
    """
    if d.get(message.upper()):
        return d.get(message.upper())
    return message


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    """Обработчик ответов пользователей

    На вход принимает ответ (подтверждение или отказ) пользователя в виде строк 'yes'/'no'
    При положительном ответе информация заносится в базу данных, иначе выводит подсказку о начале работы с ботом.
    """
    if call.data == "yes":
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        user = (call.message.chat.id, config.city, config.time_h, config.time_m)
        cur.execute("SELECT user_id FROM users WHERE user_id = ? AND city = ? AND time_h = ? AND time_m = ?", user)
        users = cur.fetchall()
        if not users:
            cur.execute("INSERT INTO users VALUES(?, ?, ?, ?);", user)
            conn.commit()
            bot.send_message(call.message.chat.id, "Вы будете получать прогноз каждый день в указанное время")
        else:
            bot.send_message(call.message.chat.id, "Вы уже добавили такой прогноз")
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Введите команду /start")
    # elif call.data == "set_city":
    #    config.changed = True
    #    return set_city(call.message)
    # elif call.data == "set_time":
    #    return set_time(call.message)


def mail():
    """Функция отправления прогноза погоды

    Непрерывно получает время, если оно совпадает со временем прогноза из базы данных,
    то вызывается функция получения прогноза погоды, а затем отправляется соответствующему пользователю.
    """
    left = (60 - datetime.datetime.now().second)
    while (left > 0):
        if left % 5 == 0:
            print(str(left) + "s left")
        time.sleep(1)
        left -= 1

    while True:
        now_h = datetime.datetime.now().hour
        now_m = datetime.datetime.now().minute

        if now_h < 10:
            now_h = "0" + str(now_h)
        else:
            now_h = str(now_h)

        if now_m < 10:
            now_m = "0" + str(now_m)
        else:
            now_m = str(now_m)

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute("SELECT user_id, city FROM users WHERE time_h = ? AND time_m = ?", (now_h, now_m))

        users = cur.fetchall()

        for user in users:
            weather = get_weather(user[1])
            message = user[1] + "\nПогода: " + weather[0] + "\nТемпература: " + str(weather[1])
            bot.send_message(user[0], message)

        time.sleep(60)


mail = threading.Thread(target=mail, args=(), daemon=True)
mail.start()

bot.polling(none_stop=True, interval=0)
