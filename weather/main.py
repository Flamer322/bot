from weather import config
from weather.config import *

bot = telebot.TeleBot(config.token)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INT,
    city TEXT,
    time TEXT);
""")
conn.commit()


def start_msg(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    list_items = ["Добавить", "Удалить", "Изменить", "Прогноз"]
    for item in list_items:
        markup.add(item)
    bot.send_message(chat_id, "Выберите пункт меню", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def start(message):
    """
    adfduksaghio

    :param message:soobshenie
    :return:govno
    """
    if message.text == "/start":
        start_msg(message.chat.id)
    elif message.text == "Добавить":
        set_city(message)
    elif message.text == "Удалить":
        del_1(message)
    elif message.text == "Изменить":
        ch_1(message)
    elif message.text == "Прогноз":
        ff_1(message)
    else:
        start_msg(message.from_user.id)


def ff_1(message):
    bot.send_message(message.from_user.id, "Укажите Ваш город")
    bot.register_next_step_handler(message, ff_2)


def ff_2(message):
    if message.text == "/start":
        return start(message)
    config.city = abb_to_city(message.text)
    city_id = get_city_id(config.city)
    if not city_id:
        wrong_city(message, ff_1)
    else:
        weather = get_weather(config.city)
        text = config.city + "\nПогода: " + str(weather[0]) + "\nТемпература: " + str(weather[1]) \
               + "°C\nСкорость ветра: " + str(weather[2]) + " м/с\nНаправление ветра: " + str(weather[3])
        response = requests.get("http://openweathermap.org/img/wn/" + weather[4] + "@4x.png")
        file = open("image.png", "wb")
        file.write(response.content)
        file.close()
        img = open("image.png", "rb")
        bot.send_photo(message.from_user.id, img, text)
        start_msg(message.from_user.id)


def ch_1(message):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT city, time FROM users WHERE user_id = ?", (message.from_user.id,))
    entries = cur.fetchall()
    if not entries:
        bot.send_message(message.from_user.id, "Вы не добавляли никаких прогнозов")
        start_msg(message.from_user.id)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Я передумал(а)")
        for entry in entries:
            markup.add(entry[0] + "\n" + entry[1])
        bot.send_message(message.chat.id, "Выберите прогноз, который нужно изменить", reply_markup=markup)
        bot.register_next_step_handler(message, ch_2)


def ch_2(message):
    if message.text == "Я передумал(а)":
        start(message)
    else:
        if re.search(r"\n([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", message.text):
            text = message.text.split("\n")
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT user_id, city, time FROM users WHERE user_id = ? AND city = ? AND time = ?",
                        (message.from_user.id, text[0], text[1]))
            entries = cur.fetchall()
            if not entries:
                bot.send_message(message.from_user.id, "Введён неправильный прогноз")
            else:
                config.city = text[0]
                config.time = text[1]
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                list_items = ["Город", "Время", "Город и время"]
                for item in list_items:
                    markup.add(item)
                bot.send_message(message.from_user.id, "Что вы хотите изменить", reply_markup=markup)
                bot.register_next_step_handler(message, ch_3)
        else:
            bot.send_message(message.from_user.id, "Введён неправильный прогноз")
            start_msg(message.from_user.id)


def ch_3(message):
    if message.text in ["Город", "Время", "Город и время"]:
        if message.text == "Город":
            bot.send_message(message.from_user.id, "Укажите новый город")
            bot.register_next_step_handler(message, ch_c)
        elif message.text == "Время":
            bot.send_message(message.from_user.id, "Выберите новое время (Москва, UTC+3), в которое Вы желаете получать"
                                                   " прогноз\n\nУкажите время в формате ЧЧ:ММ")
            bot.register_next_step_handler(message, ch_t)
        else:
            bot.send_message(message.from_user.id, "Укажите новый город")
            bot.register_next_step_handler(message, ch_ct1)
    else:
        start_msg(message.from_user.id)


def ch_c(message):
    if message.text == "/start":
        return start(message)
    config.new_city = abb_to_city(message.text)
    city_id = get_city_id(config.new_city)
    if not city_id:
        wrong_city(message, ch_c)
    else:
        config.new_time = config.time
        ch_4(message.from_user.id)


def ch_t(message):
    if message.text == "/start":
        return start(message)
    if re.fullmatch(r"^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", message.text):
        config.new_time = message.text
        config.new_city = config.city
        ch_4(message.from_user.id)
    else:
        wrong_time(message, ch_t)


def ch_ct1(message):
    if message.text == "/start":
        return start(message)
    config.new_city = abb_to_city(message.text)
    city_id = get_city_id(config.new_city)
    if not city_id:
        wrong_city(message, ch_ct1)
    else:
        bot.send_message(message.from_user.id, "Выберите новое время (Москва, UTC+3), в которое Вы желаете получать"
                                               " прогноз\n\nУкажите время в формате ЧЧ:ММ")
        bot.register_next_step_handler(message, ch_ct2)


def ch_ct2(message):
    if message.text == "/start":
        return start(message)
    if re.fullmatch(r"^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", message.text):
        config.new_time = message.text
        ch_4(message.from_user.id)
    else:
        wrong_time(message, ch_ct2)


def ch_4(user_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = ? AND city = ? AND time = ?",
                (user_id, config.city, config.time))
    cur.execute("DELETE FROM users WHERE user_id = ? AND city = ? AND time = ?",
                (user_id, config.new_city, config.new_time))
    cur.execute("INSERT INTO users VALUES(?, ?, ?);",
                (user_id, config.new_city, config.new_time))
    conn.commit()
    bot.send_message(user_id, "Прогноз изменён")
    start_msg(user_id)


def del_1(message):
    """"Удаление записи с прогнозом погоды из базы данных

    Принимает на вход сообщение, содержащее информацию о прогнозе, после чего удаляет нужный прогноз из расписания.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT city, time FROM users WHERE user_id = ?", (message.from_user.id,))
    entries = cur.fetchall()
    if not entries:
        bot.send_message(message.from_user.id, "Вы не добавляли никаких прогнозов")
        start_msg(message.from_user.id)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Я передумал(а)")
        for entry in entries:
            markup.add(entry[0] + "\n" + entry[1])
        bot.send_message(message.chat.id, "Выберите прогноз, который нужно удалить", reply_markup=markup)
        bot.register_next_step_handler(message, del_2)


def del_2(message):
    if message.text == "Я передумал(а)":
        start_msg(message.from_user.id)
    else:
        if re.search(r"\n([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", message.text):
            text = message.text.split("\n")
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT user_id, city, time FROM users WHERE user_id = ? AND city = ? AND time = ?",
                        (message.from_user.id, text[0], text[1]))
            entries = cur.fetchall()
            if not entries:
                bot.send_message(message.from_user.id, "Введён неправильный прогноз")
                del_1(message)
            else:
                bot.send_message(message.from_user.id, "Прогноз удалён")
                cur.execute("DELETE FROM users WHERE user_id = ? AND city = ? AND time = ?",
                            (message.from_user.id, text[0], text[1]))
                conn.commit()
                start_msg(message.from_user.id)
        else:
            bot.send_message(message.from_user.id, "Введён неправильный прогноз")
            del_1(message)


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
    config.city = abb_to_city(message.text)
    city_id = get_city_id(config.city)
    if not city_id:
        wrong_city(message, get_city)
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
        config.time = message.text.zfill(5)
        keyboard_confirmation(message)
    else:
        wrong_time(message, get_time)


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
               config.time + ".\n\nВерно?"
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


def wrong_city(message, function):
    """Функция информирования о неправильном вводе города

    На вход получает информацию об отправителе сообщения,
    после чего передаёт обработчику информацию о вызове функции получения города.
    """
    bot.send_message(message.from_user.id, "Неправильное название города."
                                           "\nПожалуйста, попробуй ещё раз")
    bot.register_next_step_handler(message, function)


def wrong_time(message, function):
    """Функция информирования о неправильном вводе времени

    На вход получает информацию об отправителе сообщения,
    после чего передаёт обработчику информацию о вызове функции получения времени.
    """
    bot.send_message(message.from_user.id, "Неправильно введено время."
                                           "\nПожалуйста, введите время ещё раз")
    bot.register_next_step_handler(message, function)


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
        wind = round(data['wind']['speed'], 1)
        windd = data['wind']['deg']
        icon = data['weather'][0]['icon']
        if windd == 0:
            windd = 'С'
        elif 0 < windd < 90:
            windd = 'СВ'
        elif windd == 90:
            windd = 'В'
        elif 90 < windd < 180:
            windd = 'ЮВ'
        elif windd == 180:
            windd = 'В'
        elif 180 < windd < 270:
            windd = 'ЮЗ'
        elif windd == 270:
            windd = 'З'
        else:
            windd = 'СЗ'
        return conditions, temp, wind, windd, icon
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
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        user = (call.message.chat.id, config.city, config.time)
        cur.execute("SELECT user_id FROM users WHERE user_id = ? AND city = ? AND time = ?", user)
        users = cur.fetchall()
        if not users:
            cur.execute("INSERT INTO users VALUES(?, ?, ?);", user)
            conn.commit()
            bot.send_message(call.message.chat.id, "Вы будете получать прогноз каждый день в указанное время")
        else:
            bot.send_message(call.message.chat.id, "Вы уже добавили такой прогноз")
    elif call.data == "no":
        print("TO DO")
    start_msg(call.message.chat.id)
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
    sleep(left)

    while True:
        now = datetime.datetime.now().strftime("%H:%M")

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("SELECT user_id, city FROM users WHERE time = ?", (now,))

        users = cur.fetchall()

        for user in users:
            weather = get_weather(user[1])
            message = user[1] + "\nПогода: " + weather[0] + "\nТемпература: " + str(weather[1]) \
                      + "\nСкорость ветра: " + str(weather[2]) + " м/с\nНаправление ветра: " + weather[3]
            bot.send_message(user[0], message)
            start_msg(user[0])

        sleep(60)


mail = threading.Thread(target=mail, args=(), daemon=True)
mail.start()

bot.polling(none_stop=True, interval=0)
