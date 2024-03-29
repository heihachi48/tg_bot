import telebot
from telebot import types
import psycopg2
from datetime import datetime


def connect_to_database():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="0312",
            host="localhost",
            port="5432",
            database="postgres"
        )
        print("Connected to PostgreSQL database!")
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None


bot = telebot.TeleBot('7115522268:AAFoTHMK--OYTBFi-l773-vFCRkaG5BVv38')


def send_commands_list(message):
    commands_list = ""
    # commands_list += "/start - Начать использование бота\n"
    commands_list += "/help - Показать список команд\n"
    commands_list += "/add - Добавить данные\n"
    commands_list += "/delete - Удалить данные\n"
    commands_list += "/edit - Изменить данные\n"
    commands_list += "/user_info - Получить информацию о пользователе\n"
    commands_list += "/exit - Завершить сессию работы с ботом\n"
    bot.send_message(message.chat.id, commands_list, parse_mode='html')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Здравствуйте! Чтобы узнать функционал бота, пропишите команду /help', parse_mode='html')


# @bot.message_handler(func=lambda message: message.text == 'Начать')
# def start_button_handler(message):
#     bot.send_message(message.chat.id, 'Здравствуйте! Чтобы узнать функционал бота, пропишите команду /help')


@bot.message_handler(commands=['help'])
def help_command(message):
    send_commands_list(message)


@bot.message_handler(commands=['add'])
def add_command(message):
    bot.send_message(message.chat.id, 'Какие данные вы хотите добавить?')


@bot.message_handler(commands=['delete'])
def delete_command(message):
    bot.send_message(message.chat.id, 'Какие данные вы хотите удалить?')


@bot.message_handler(commands=['edit'])
def edit_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    edit_student_button = types.KeyboardButton('Изменить записи о студенте')
    penis_button = types.KeyboardButton('prekol')
    back_button = types.KeyboardButton('Назад')
    markup.add(edit_student_button, penis_button, back_button)
    bot.send_message(message.chat.id, 'Какие данные вы хотите изменить?', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Изменить записи о студенте')
def edit_student_handler(message):
    bot.send_message(message.chat.id, 'А чего изменять, если базы нет')


@bot.message_handler(commands=['user_info'])
def user_info_command(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_info = f"ID: {user_id}\nИмя: {first_name}\n"
    if last_name:
        user_info += f"Фамилия: {last_name}\n"
    user_info += f"Дата начала использования бота: {date}"

    bot.send_message(message.chat.id, user_info)


@bot.message_handler(func=lambda message: message.text == 'prekol')
def penis_handler(message):
    gif_url = 'https://s9.gifyu.com/images/SVIDm.gif'
    bot.send_document(message.chat.id, document=gif_url)


@bot.message_handler(func=lambda message: message.text == 'Назад')
def back_handler(message):
    send_commands_list(message)


@bot.message_handler(commands=['exit'])
def exit_command(message):
    bot.send_message(message.chat.id, 'Сессия работы с ботом завершена.', reply_markup=types.ReplyKeyboardRemove())


bot.polling(none_stop=True)
