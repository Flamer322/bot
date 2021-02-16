import re
import time
import telebot
import threading
import datetime
from telebot import types

print("Starting")

bot = telebot.TeleBot("1594121133:AAFncSvyiQeogakz4HvSBA1bDkY77cvftrg")

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
    bot.send_message(message.from_user.id, "В какое время по МСК тебе отправлять прогноз?\nВ формате ЧЧ:ММ")
    bot.register_next_step_handler(message, get_time)


def get_time(message):
    global time_h
    global time_m
    if re.fullmatch(r"\d\d:\d\d", message.text):
        time_h = int(message.text[0:2])
        time_m = int(message.text[3:5])
        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text="Нет", callback_data="no")
        keyboard.add(key_no)
        question = "Твой город - " + city + ". Отправлять прогноз в " + str(time_h) + ":" + str(time_m) + ". Верно?"
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        now = datetime.datetime.now()
        bot.send_message(call.message.chat.id, str(call.message.chat.id) + " " + now.strftime("%H:%M"))
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Напиши /start")


def mail():
    now = datetime.datetime.now().second
    time.sleep(60 - now)

    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        bot.send_message(410124654, now)
        time.sleep(60)


mail = threading.Thread(target=mail, args=(), daemon=True)
mail.start()

bot.polling(none_stop=True, interval=0)