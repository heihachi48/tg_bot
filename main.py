import telebot
from telebot import types
import psycopg2
import hashlib
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


bot = telebot.TeleBot('7115522268:AAFoTHMK--OYTBFi-l773-vFCRkaG5BVv38')


def send_commands_list(chat_id):
    commands_list = ""
    commands_list += "/help - Показать список команд\n"
    commands_list += "/view_information - Личные данные\n"
    commands_list += "/training - Информация об обучении\n"
    commands_list += "/grade - Успеваемость\n"
    commands_list += "/grade - Расписание\n"
    commands_list += "/user_info - Получить информацию о пользователе\n"
    commands_list += "/exit - Завершить сессию работы с ботом\n"
    bot.send_message(chat_id, commands_list, parse_mode='html')


def authenticate_user(username, password_hash, message):
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password_hash))
            user_exists = cursor.fetchone() is not None
            cursor.close()
            connection.close()
            if user_exists:
                send_commands_list(message.chat.id)
            else:
                bot.send_message(message.chat.id, "Неверный логин или пароль. Попробуйте снова.")
                check_username(message)
        except psycopg2.Error as error:
            print("Error while authenticating user in PostgreSQL", error)
            bot.send_message(message.chat.id, "Произошла ошибка при аутентификации. Пожалуйста, попробуйте позже.")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при подключении к базе данных. Пожалуйста, попробуйте позже.")


def check_username(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Введите ваш логин:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: check_password(msg.text, message))


def check_password(username, message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Введите ваш пароль:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: authenticate_user(username, hashlib.sha256(msg.text.encode()).hexdigest(), message))


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Для использования бота вам необходимо авторизоваться.")
    check_username(message)


@bot.message_handler(commands=['help'])
def help_command(message):
    send_commands_list(message.chat.id)


# @bot.message_handler(commands=['view_information'])
# def view_information_command(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
#     personal_date = types.KeyboardButton('Паспортные данные')
#     snils = types.KeyboardButton('Снилс')
#     education = types.KeyboardButton('Образование')
#     back_button = types.KeyboardButton('Назад')
#     penis_button = types.KeyboardButton('prekol')
#     markup.add(personal_date, snils, education, penis_button, back_button)
#     bot.send_message(message.chat.id, '⇓ ⇓ Выберите нужную кнопку ⇓ ⇓ :', reply_markup=markup)


@bot.message_handler(commands=['training'])
def training_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    number_book_study = types.KeyboardButton('Номер зачетной книжки')
    status = types.KeyboardButton('Статус')
    direction = types.KeyboardButton('Направление')
    institute = types.KeyboardButton('Институт')
    department = types.KeyboardButton('Кафедра')
    group = types.KeyboardButton('Группа')
    the_form_of_education = types.KeyboardButton('Форма обучения')
    back_button = types.KeyboardButton('Назад')
    markup.add(number_book_study, status, direction, institute, department, group, the_form_of_education, back_button)
    bot.send_message(message.chat.id, '⇓ ⇓ Выберите нужную кнопку ⇓ ⇓ :', reply_markup=markup)


@bot.message_handler(commands=['grade'])
def grade_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    test = types.KeyboardButton('Зачеты')
    exams = types.KeyboardButton('Экзамены')
    back_button = types.KeyboardButton('Назад')
    markup.add(test, exams, back_button)
    bot.send_message(message.chat.id, '⇓ ⇓ Выберите нужную кнопку ⇓ ⇓ :', reply_markup=markup)


# @bot.message_handler(commands=['timetable'])
# def timetable_command(message):
#     bot.send_message(message.chat.id, 'Расписание занятий:', reply_markup=markup)

# @bot.message_handler(func=lambda message: message.text == 'Изменить записи о студенте')
# def edit_student_handler(message):
#     bot.send_message(message.chat.id, 'Теперь база есть, но пока не настроил((')


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


@bot.message_handler(commands=['exit'])
def exit_command(message):
    bot.send_message(message.chat.id, 'Сессия работы с ботом завершена.', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda message: message.text == 'Назад')
def back_handler(message):
    send_commands_list(message.chat.id)


bot.polling(none_stop=True)
