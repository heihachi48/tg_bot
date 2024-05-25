import telebot
from telebot import types
import psycopg2
import hashlib
import secrets
from datetime import datetime

reminder_sent = False

user_nexus = {}


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


def execute_query(query, params=None):
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()  # Фиксация изменений (если есть)
            cursor.close()
            connection.close()
            return result
        except psycopg2.Error as error:
            print("Error executing query:", error)
            return None
    else:
        print("No database connection")
        return None


bot = telebot.TeleBot('7115522268:AAFoTHMK--OYTBFi-l773-vFCRkaG5BVv38')


def send_commands_list(chat_id):
    commands_list = ""
    commands_list += "/help - Показать список команд\n"
    commands_list += "/training - Информация об обучении\n"
    commands_list += "/grade - Успеваемость\n"
    commands_list += "/распиание - Расписание\n"
    commands_list += "/user_info - Получить информацию о пользователе\n"
    commands_list += "/prekol - хохма\n"
    commands_list += "/exit - Завершить сессию работы с ботом\n"
    bot.send_message(chat_id, commands_list, parse_mode='html')


def update_passwords_with_salt():
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()

            cursor.execute("SELECT user_id, username, password_hash FROM users")
            users = cursor.fetchall()

            for user in users:
                user_id, username, password_hash = user

                salt = secrets.token_hex(16)

                new_password_hash = hashlib.sha256((password_hash + salt).encode()).hexdigest()

                # Обновляем пароль и соль в базе данных
                cursor.execute("UPDATE users SET password_hash = %s, salt = %s WHERE id = %s", (new_password_hash, salt, user_id))

            connection.commit()
            cursor.close()
            connection.close()
            print("Passwords updated successfully")
        except psycopg2.Error as error:
            print("Error while updating passwords in PostgreSQL", error)
    else:
        print("No database connection")


update_passwords_with_salt()


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
                user_nexus[message.chat.id] = username
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


@bot.message_handler(commands=['training'])
def number_book_study_handler(message):
    username = message.from_user.username
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT u.full_name, t.number_zb, t.course, t.direction, t.institute, t.department, t.group_s
                FROM users u
                JOIN training t ON u.user_id = t.user_id
                WHERE u.username = %s;
            """, (user_nexus[message.chat.id],))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            if result:
                user_info = f"Имя пользователя: {result[0]}\n"
                user_info += f"Номер зачетной книжки: {result[1]}\n"
                user_info += f"Курс: {result[2]}\n"
                user_info += f"Направление: {result[3]}\n"
                user_info += f"Институт: {result[4]}\n"
                user_info += f"Кафедра: {result[5]}\n"
                user_info += f"Группа: {result[6]}\n"
                bot.send_message(message.chat.id, '⇓ ⇓ Ваша информация ⇓ ⇓ \n' + user_info)
            else:
                bot.send_message(message.chat.id, "Информация об обучении не найдена для данного пользователя")
        except psycopg2.Error as error:
            print("Error while executing SQL query:", error)
            bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса к базе данных.")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при подключении к базе данных. Пожалуйста, попробуйте позже.")


@bot.message_handler(commands=['grade'])
def grade_command(message):
    username = user_nexus[message.chat.id]
    user_course = get_user_course(username)

    if user_course is None:
        bot.reply_to(message, "К сожалению, не удалось определить ваш курс.")
        return

    available_semesters = determine_available_semesters(user_course)

    if not available_semesters:
        bot.reply_to(message, "Кажется, что у вас нет доступных семестров.")
        return

    row_width = 4
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    row_buttons = []

    for semester in available_semesters:
        button = types.KeyboardButton(f'{semester}-ый семестр')
        row_buttons.append(button)
        if len(row_buttons) == row_width:
            markup.row(*row_buttons)
            row_buttons = []

    if row_buttons:
        markup.row(*row_buttons)

    back_button = types.KeyboardButton('Назад')
    markup.add(back_button)

    bot.send_message(message.chat.id, '⇓ ⇓ Выберите семестр ⇓ ⇓ :', reply_markup=markup)

    for semester in available_semesters:
        bot.register_message_handler(lambda msg, s=semester: get_grades_handler(msg, username, s))


def get_grades_handler(message, username, semester):
    grades = get_grades_for_semester(username, semester)
    if grades:
        formatted_grades = "\n".join([f"{subject}: {grade}" for subject, grade in grades])
        bot.reply_to(message, f'Оценки за {semester}-ый семестр:\n{formatted_grades}')
    else:
        bot.reply_to(message, f'Кажется, что у вас нет оценок за {semester}-ый семестр.')


def determine_available_semesters(course):
    if course == 1:
        return ['1-ый семестр', '2-ой семестр']
    elif course == 2:
        return ['1-ый семестр', '2-ой семестр', '3-ий семестр', '4-ый семестр']
    elif course == 3:
        return ['1-ый семестр', '2-ой семестр', '3-ий семестр', '4-ый семестр', '5-ый семестр', '6-ой семестр']
    elif course == 4:
        return ['1-ый семестр', '2-ой семестр', '3-ий семестр', '4-ый семестр', '5-ый семестр', '6-ой семестр', '7-ой семестр', '8-ой семестр']
    elif course == 5:
        return ['1-ый семестр', '2-ой семестр', '3-ий семестр', '4-ый семестр', '5-ый семестр', '6-ой семестр', '7-ой семестр', '8-ой семестр', '9-ый семестр', '10-ый семестр']
    else:
        return []


def get_user_course(username):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"""
            SELECT course FROM training t
            JOIN users u ON t.user_id = u.user_id
            WHERE username = '{username}';
            """)
            user_course = cursor.fetchone()
            cursor.close()
            connection.close()
            if user_course:
                return user_course[0]
            else:
                print("User course not found")
                return None
        else:
            print("No database connection")
            return None
    except Exception as e:
        print("Error getting user course:", e)
        return None


def get_grades_for_semester(username, semester):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT ghr.full_name, ghr.subject_name, ghr.term_name, ghr.grade_name 
                FROM (
                    SELECT 
                        us.full_name as full_name, 
                        sb.subject_name as subject_name, 
                        gr.name as grade_name, 
                        tr.name as term_name, 
                        row_number() over(partition by gh.user_user_id, gh.subject_subject_id, gh.term_term_id order by gh.number_history DESC) as rn
                    FROM grade_histories gh
                    JOIN grades gr ON gr.grade_id = gh.grade_grade_id
                    JOIN termes tr ON tr.term_id = gh.term_term_id
                    JOIN users us ON us.user_id = gh.user_user_id
                    JOIN subjects sb ON sb.subject_id = gh.subject_subject_id
                    WHERE gh.user_user_id = %s AND gh.term_term_id = %s
                ) as ghr
                WHERE ghr.rn = 1;
            """, (username, semester))
            grades = cursor.fetchall()
            cursor.close()
            connection.close()
            return grades
        else:
            print("No database connection")
            return None
    except Exception as e:
        print("Error getting grades for semester:", e)
        return None


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


@bot.message_handler(commands=['prekol'])
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
