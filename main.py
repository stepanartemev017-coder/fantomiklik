import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- ДАННЫЕ ---
TOKEN = '8749709641:AHH8AgA6cj6QPb114jhjnncn9KVFSduGO1w'
GROQ_KEY = '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'

client = Groq(api_key=GROQ_KEY)
bot = telebot.TeleBot(TOKEN)

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('bot_memory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history 
        (chat_id INTEGER PRIMARY KEY, messages TEXT)
    ''')
    conn.commit()
    conn.close()

def get_history(chat_id):
    conn = sqlite3.connect('bot_memory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])
    return []

def save_history(chat_id, messages):
    # Ограничиваем историю (последние 60 сообщений), чтобы не перегружать нейронку
    if len(messages) > 60:
        messages = messages[-60:]
    conn = sqlite3.connect('bot_memory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', 
                   (chat_id, json.dumps(messages)))
    conn.commit()
    conn.close()

# Инициализируем БД при запуске
init_db()

# --- ОБРАБОТКА КОМАНД ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("ИИ")
    markup.add(btn)
    # При старте можно очистить историю, если хочешь начать заново
    save_history(message.chat.id, [])
    bot.send_message(message.chat.id, "Здарова! Кнопка внизу, нажимай и погнали.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "ИИ")
def ai_welcome(message):
    bot.reply_to(message, "Здарова фраер, че хотел?")

@bot.message_handler(func=lambda message: True)
def chat(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')

    # Загружаем историю из базы
    history = get_history(chat_id)

    # Добавляем сообщение пользователя
    history.append({"role": "user", "content": message.text})

    try:
        # Формируем запрос
        messages_to_ai = [
            {
                "role": "system", 
                "content": "Ты — умный помощник с чувством юмора. Отвечай точно, по делу, на 'ты' и с подколами. Отвечай только на русском."
            }
        ] + history

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_to_ai
        )

        answer = completion.choices[0].message.content
        
        # Добавляем ответ бота в историю и сохраняем в БД
        history.append({"role": "assistant", "content": answer})
        save_history(chat_id, history)
        
        bot.reply_to(message, answer)

    except Exception as e:
        bot.reply_to(message, f"Блин, мозг залагал. Ошибка: {str(e)}")

if __name__ == '__main__':
    print("Бот с вечной памятью запущен!")
    bot.infinity_polling()
