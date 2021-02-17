import re
import time
import requests
import telebot
import sqlite3
import threading
import datetime
from telebot import types

print("Starting")

f = open("key.txt", "r")
key = f.read()
key = key.rstrip('\n')

f = open("token.txt", "r")
token = f.read()
token = token.rstrip('\n')

bot = telebot.TeleBot(token)

conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INT,
    city TEXT,
    time_h TEXT,
    time_m TEXT);
""")
conn.commit()

city = ""
time_h = 0
time_m = 0

@bot.message_handler(content_types=["text"])
def start(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Город?")
        bot.register_next_step_handler(message, get_city)
    else:
        bot.send_message(message.from_user.id, "Напиши /start")


def get_city(message):
    global city
    city = message.text
    bot.send_message(message.from_user.id, "В какое время по МСК тебе отправлять прогноз?"
                                           "\nВ формате ЧЧ:ММ")
    bot.register_next_step_handler(message, get_time)


def get_time(message):
    global time_h
    global time_m
    if re.fullmatch(r"\d\d:\d\d", message.text):
        time_h = int(message.text[0:2])
        time_m = int(message.text[3:5])
        if time_h < 24 and time_m < 60:
            time_h = str(time_h)
            if time_m < 10:
                time_m = "0" + str(time_m)
            else:
                time_m = str(time_m)
            keyboard = types.InlineKeyboardMarkup()
            key_yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
            keyboard.add(key_yes)
            key_no = types.InlineKeyboardButton(text="Нет", callback_data="no")
            keyboard.add(key_no)
            question = "Твой город - " + city + ". Отправлять прогноз в " + \
                       time_h + ":" + time_m + ". Верно?"
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
        else:
            wrong_time(message)
    else:
        wrong_time(message)


def wrong_time(message):
    bot.send_message(message.from_user.id, "Неправильно введено время. Пожалуйста, введите время ещё раз")
    bot.register_next_step_handler(message, get_time)


def get_weather(city):
    city_id = 0
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': key})
        data = res.json()
        city_id = data['list'][0]['id']
    except Exception as e:
        print("Exception (find):", e)
        pass

    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': key})
        data = res.json()
        conditions = data['weather'][0]['description']
        temp = round(data['main']['temp'])
        return (conditions, temp)
    except Exception as e:
        print("Exception (weather):", e)
        pass


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        user = (call.message.chat.id, city, time_h, time_m)\

        cur.execute("SELECT user_id FROM users WHERE user_id = \"" + str(user[0]) +
                    "\" AND city = \"" + user[1] + "\" AND time_h = \"" + user[2] +
                    "\" AND time_m = \"" + user[3] + "\"")

        users = cur.fetchall()
        if not users:
            cur.execute("INSERT INTO users VALUES(?, ?, ?, ?);", user)
        conn.commit()
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Напиши /start")


def mail():
    left = (60 - datetime.datetime.now().second)
    while (left > 0):
        if left % 5 == 0:
            print(str(left) + "s left")
        time.sleep(1)
        left -= 1

    while True:
        now_h = str(datetime.datetime.now().hour)
        now_m = datetime.datetime.now().minute
        if now_m< 10:
            now_m = "0" + str(now_m)
        else:
            now_m = str(now_m)
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute("SELECT user_id, city FROM users WHERE time_h = \"" + now_h +
                    "\" AND time_m = \"" + now_m + "\"")

        users = cur.fetchall()

        for user in users:
            weather = get_weather(user[1])
            message = user[1] + "\nПогода: " + weather[0] + "\nТемпература: " + str(weather[1])
            bot.send_message(user[0], message)

        time.sleep(60)


mail = threading.Thread(target=mail, args=(), daemon=True)
mail.start()

bot.polling(none_stop=True, interval=0)