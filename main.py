import config
from config import *

print("Starting")

bot = telebot.TeleBot(config.token)

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INT,
    city TEXT,
    time TEXT);
""")
conn.commit()


def start_msg(chat_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    list_items = ["Добавить", "Удалить", "Изменить"]
    for item in list_items:
        markup.add(item)
    bot.send_message(chat_id, "Выберите пункт меню", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def start(message):
    if message.text == "/start":
        start_msg(message.chat.id)
    elif message.text == "Добавить":
        set_city(message)
    elif message.text == "Удалить":
        del_1(message)
    elif message.text == "Изменить":
        ch_1(message)
    else:
        start_msg(message.from_user.id)


def ch_1(message):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT city, time FROM users WHERE user_id = ?", (message.from_user.id,))
    entries = cur.fetchall()
    if not entries:
        bot.send_message(message.from_user.id, "Вы не добавляли никаких прогнозов")
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
            conn = sqlite3.connect("users.db")
            cur = conn.cursor()
            cur.execute("SELECT user_id, city, time FROM users WHERE user_id = ? AND city = ? AND time = ?",
                        (message.from_user.id, text[0], text[1]))
            entries = cur.fetchall()
            if not entries:
                bot.send_message(message.from_user.id, "Введён неправильный прогноз")
            else:
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
            print("1")
        elif message.text == "Время":
            print("2")
        else:
            print("3")
    else:
        print("4")
    start_msg(message.from_user.id)


def del_1(message):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT city, time FROM users WHERE user_id = ?", (message.from_user.id,))
    entries = cur.fetchall()
    if not entries:
        bot.send_message(message.from_user.id, "Вы не добавляли никаких прогнозов")
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add("Я передумал(а)")
        for entry in entries:
            markup.add(entry[0] + "\n" + entry[1])
        bot.send_message(message.chat.id, "Выберите прогноз, который нужно удалить", reply_markup=markup)
        bot.register_next_step_handler(message, del_2)


def del_2(message):
    if message.text == "Я передумал(а)":
        start(message)
    else:
        if re.search(r"\n([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", message.text):
            text = message.text.split("\n")
            conn = sqlite3.connect("users.db")
            cur = conn.cursor()
            cur.execute("SELECT user_id, city, time FROM users WHERE user_id = ? AND city = ? AND time = ?",
                        (message.from_user.id, text[0], text[1]))
            entries = cur.fetchall()
            if not entries:
                bot.send_message(message.from_user.id, "Введён неправильный прогноз")
            else:
                bot.send_message(message.from_user.id, "Прогноз удалён")
                cur.execute("DELETE FROM users WHERE user_id = ? AND city = ? AND time = ?",
                            (message.from_user.id, text[0], text[1]))
                conn.commit()
        else:
            bot.send_message(message.from_user.id, "Введён неправильный прогноз")
        start_msg(message.from_user.id)


def set_city(message):
    bot.send_message(message.from_user.id, "Укажите Ваш город")
    bot.register_next_step_handler(message, get_city)


def get_city(message):
    if message.text == "/start":
        return start(message)
    config.city = abb_to_city(message.text)
    city_id = get_city_id(config.city)
    if not city_id:
        wrong_city(message)
    elif config.changed:
        keyboard_confirmation(message)
        config.changed = False
    else:
        set_time(message)


def set_time(message):
    bot.send_message(message.from_user.id, "Выберите время (Москва, UTC+3), в которое Вы желаете получать прогноз"
                                           "\n\nУкажите время в формате ЧЧ:ММ")
    bot.register_next_step_handler(message, get_time)


def get_time(message):
    if message.text == "/start":
        return start(message)
    if re.fullmatch(r"^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", message.text):
        config.time = message.text
        keyboard_confirmation(message)
    else:
        wrong_time(message)


def keyboard_confirmation(message):
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


def wrong_city(message):
    bot.send_message(message.from_user.id, "Неправильное название города."
                                           "\nПожалуйста, попробуй ещё раз")
    bot.register_next_step_handler(message, get_city)


def wrong_time(message):
    bot.send_message(message.from_user.id, "Неправильно введено время."
                                           "\nПожалуйста, введите время ещё раз")
    bot.register_next_step_handler(message, get_time)


def get_city_id(city):
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
    city_id = get_city_id(city)
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': config.key})
        data = res.json()
        conditions = data['weather'][0]['description']
        temp = round(data['main']['temp'])
        return conditions, temp
    except Exception as e:
        print("Exception (weather):", e)
        pass


def abb_to_city(message):
    if d.get(message.upper()):
        return d.get(message.upper())
    return message


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        user = (call.message.chat.id, config.city, config.time)
        cur.execute("SELECT user_id FROM users WHERE user_id = ? AND city = ? AND time = ?", user)
        users = cur.fetchall()
        if not users:
            cur.execute("INSERT INTO users VALUES(?, ?, ?)", user)
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
    left = (60 - datetime.datetime.now().second)
    while left > 0:
        if left % 5 == 0:
            print(str(left) + "s left")
        sleep(1)
        left -= 1

    while True:
        now = datetime.datetime.now().strftime("%H:%M")

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute("SELECT user_id, city FROM users WHERE time = ?", (now,))

        users = cur.fetchall()

        for user in users:
            weather = get_weather(user[1])
            message = user[1] + "\nПогода: " + weather[0] + "\nТемпература: " + str(weather[1])
            bot.send_message(user[0], message)

        sleep(60)


mail = threading.Thread(target=mail, args=(), daemon=True)
mail.start()

bot.polling(none_stop=True, interval=0)
