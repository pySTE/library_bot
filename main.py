import telebot
import sqlite3

token = '7980971983:AAFaDP5jxPLm58Wdsj9wJFHlsj-2nZaeXFw'
bot = telebot.TeleBot(token)

def db():
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        year INTEGER,
        status TEXT
    );""")
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f'Привет {message.from_user.first_name}')
    db()

@bot.message_handler(commands=['add_book'])
def add_book(message):
    bot.reply_to(message, 'введите название книги')
    bot.register_next_step_handler(message, с_title)

def с_title(message):
    title = message.text.lower()
    bot.reply_to(message, 'введите автора книги')
    bot.register_next_step_handler(message, сauthor, title)

def сauthor(message, title):
    author = message.text
    bot.reply_to(message, 'введите год написания книги')
    bot.register_next_step_handler(message, с_year, title, author)

def с_year(message, title, author):
    try:
        year = int(message.text)
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (title, author, year, status) VALUES (?, ?, ?, ?)", 
                    (title, author, year, 'в наличие'))
        conn.commit()
        conn.close()
        bot.reply_to(message, 'Книга добавлена.')
    except ValueError:
        bot.reply_to(message, 'Ошибка: введите корректный год.')

@bot.message_handler(commands=['delete_book'])
def delete(message):
    bot.reply_to(message, 'введите id для удаления')
    bot.register_next_step_handler(message, cdelete)

def cdelete(message):
    try:
        id_for_del = int(message.text)
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (id_for_del,))
        if cur.rowcount > 0:
            bot.reply_to(message, 'Книга удалена.')
        else:
            bot.reply_to(message, 'Книга с таким id не найдена.')
        conn.commit()
        conn.close()
    except ValueError:
        bot.reply_to(message, 'Ошибка: введите корректный id.')

@bot.message_handler(commands=['search_with_title'])
def search_with_title(message):
    bot.reply_to(message, 'введите название книги для поиска')
    bot.register_next_step_handler(message, searching_with_title)

def searching_with_title(message):
    title_gor_search = message.text.lower()
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE title = ?", (title_gor_search,))
    results = cur.fetchall()
    conn.close()
    
    if results:
        response = "\n".join([f"Название: {row[1]}, Автор: {row[2]}, Год написания: {row[3]}, Статус: {row[4]}" for row in results])
        bot.send_message(message.chat.id, response)
    else:
        bot.reply_to(message, 'Книги с таким названием не найдены.')


@bot.message_handler(commands=['search_with_author'])
def search_with_author(message):
    bot.reply_to(message, 'введите имя и фамилию автора для поиска')
    bot.register_next_step_handler(message, searching_with_title)

def searching_with_title(message):
    author_gor_search = message.text
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE author = ?", (author_gor_search,))
    results = cur.fetchall()
    conn.close()
    
    if results:
        response = "\n".join([f"Название: {row[1]}, Автор: {row[2]}, Год написания: {row[3]}, Статус: {row[4]}" for row in results])
        bot.send_message(message.chat.id, response)
    else:
        bot.reply_to(message, 'Книги с таким автором не найдены.')


@bot.message_handler(commands=['search_with_year'])
def search_with_author(message):
    bot.reply_to(message, 'введите имя и фамилию автора для поиска')
    bot.register_next_step_handler(message, searching_with_year)

def searching_with_year(message):
    year_gor_search = int(message.text)
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE year = ?", (year_gor_search,))
    results = cur.fetchall()
    conn.close()
    
    if results:
        response = "\n".join([f"Название: {row[1]}, Автор: {row[2]}, Год написания: {row[3]}, Статус: {row[4]}" for row in results])
        bot.send_message(message.chat.id, response)
    else:
        bot.reply_to(message, 'Книги с таким годом написания не найдены.')


@bot.message_handler(commands=['check_all'])
def check_all(message):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    result = cur.fetchall()
    conn.close()
    if result:
        response = "\n".join([f"Название: {row[1]}, Автор: {row[2]}, Год написания: {row[3]}, Статус: {row[4]}" for row in result])
        bot.send_message(message.chat.id, response)
    else:
        bot.reply_to(message, 'Нету книг в бд')


@bot.message_handler(commands=['edit_status'])
def edit_status(message):
    bot.reply_to(message, 'введите id книги статус который хотите изменить')
    bot.register_next_step_handler(message, editing_status)

def editing_status(message):
    try:
        id = int(message.text)
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        
        cur.execute("SELECT status FROM users WHERE id = ?", (id,))
        ststus_now = cur.fetchone()
        
        if ststus_now is None:
            bot.reply_to(message, 'книга с таким ID не найдена.')
            return
        
        if ststus_now[0] == 'выдана':
            new_status = 'в наличии'
        else:
            new_status = 'выдана'
        
        cur.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, id))
        conn.commit()  
        conn.close()
        
        bot.reply_to(message, f'cтатус обновлен')
    except ValueError:
        bot.reply_to(message, 'yе обновлен статус: произошла ошибка')

db()
bot.polling()
