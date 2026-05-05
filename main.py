import telebot
from telebot import types
from groq import Groq
import sqlite3
import json
import os # Позволяет читать переменные из настроек хостинга

# --- ТЕПЕРЬ ЭТИ СТРОКИ ВСЕГДА ОДИНАКОВЫЕ ---
# Код берет значения из тех полей, что ты заполнил на Bothost
TOKEN = os.getenv('API_TOKEN')
GROQ_KEY = os.getenv('GROQ_KEY')

client = Groq(api_key=GROQ_KEY)
bot = telebot.TeleBot(TOKEN)

# --- РАБОТА С БАЗОЙ ДАННЫХ (ВЕЧНАЯ ПАМЯТЬ) ---
def init_db():
    conn = sqlite3.connect('bot_memory.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
    conn.commit()
    conn.close()

def get_history(chat_id):
    conn = sqlite3.connect('bot_memory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result) if result else []

def save_history(chat_id, messages):
    if len(messages) > 60: messages = messages[-60:] # Помним 60 сообщений
    conn = sqlite3.connect('bot_memory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(messages)))
    conn.commit()
    conn.close()

init_db()

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"))
    save_history(message.chat.id, []) # Очистка памяти при /start
    bot.send_message(message.chat.id, "Здарова! Кнопка 'ИИ' внизу, жми и пиши че хотел.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "ИИ")
def ai_welcome(message):
    bot.reply_to(message, "Здарова фраер, че хотел?")

@bot.message_handler(func=lambda message: True)
def chat(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    # Загружаем историю из базы
    history = get_history(chat_id)
    history.append({"role": "user", "content": message.text})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты умный помощник. Отвечай точно, на 'ты', с юмором и подколами. Всегда на русском."}] + history
        )
        answer = completion.choices.message.content
        
        # Сохраняем ответ бота в память
        history.append({"role": "assistant", "content": answer})
        save_history(chat_id, history)
        
        bot.reply_to(message, answer)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка (проверь ключи в настройках): {str(e)}")

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
