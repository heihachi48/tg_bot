import telebot
from telebot import types
import psycopg2
from datetime import datetime

reminder_sent = False


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


def check_user_access(tg_id):
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM tg_id_student WHERE tg_id = %s", (tg_id,))
            user_exists = cursor.fetchone() is not None
            cursor.close()
            connection.close()
            return user_exists
        except psycopg2.Error as error:
            print("Error while fetching data from PostgreSQL", error)
            return False
    else:
        return False


bot = telebot.TeleBot('7115522268:AAFoTHMK--OYTBFi-l773-vFCRkaG5BVv38')


def send_commands_list(chat_id):
    commands_list = ""
    # commands_list += "/start - Начать использование бота\n"
    commands_list += "/help - Показать список команд\n"
    commands_list += "/add - Добавить данные\n"
    commands_list += "/delete - Удалить данные\n"
    commands_list += "/edit - Изменить данные\n"
    commands_list += "/user_info - Получить информацию о пользователе\n"
    commands_list += "/exit - Завершить сессию работы с ботом\n"
    bot.send_message(chat_id, commands_list, parse_mode='html')


@bot.message_handler(commands=['start'])
def start(message):
    tg_id = message.from_user.id
    if check_user_access(tg_id):
        send_commands_list(message.chat.id)
    else:
        bot.reply_to(message, "Извините, у вас нет доступа к использованию этого бота.")


@bot.message_handler(commands=['help'])
def help_command(message):
    send_commands_list(message.chat.id)


@bot.message_handler(commands=['add'])
def add_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_student_button = types.KeyboardButton('Добавить записи о студенте')
    back_button = types.KeyboardButton('Назад')
    markup.add(add_student_button, back_button)
    bot.send_message(message.chat.id, 'Какие данные вы хотите добавить?', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Добавить записи о студенте')
def add_student_handler(message):
    bot.send_message(message.chat.id, 'База есть, просто настроить надо')


@bot.message_handler(commands=['delete'])
def delete_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
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
    bot.send_message(message.chat.id, 'Теперь база есть, но пока не настроил((')


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
