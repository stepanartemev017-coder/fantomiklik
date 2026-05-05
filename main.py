import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# ТВОИ КЛЮЧИ
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# БАЗА ДАННЫХ
def init_db():
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Выбирай вкладку, фраер:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def chat(message):
    if message.text in ["ИИ", "Скрипты"]:
        if message.text == "ИИ": bot.reply_to(message, "Здарова фраер, че хотел?")
        else: bot.reply_to(message, "Тут пока пусто.")
        return

    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    # Читаем историю
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    res = cursor.fetchone()
    conn.close()
    
    history = json.loads(res) if res else []
    history.append({"role": "user", "content": message.text})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты дерзкий помощник. На 'ты', с юмором. На русском."}] + history
        )
        answer = completion.choices.message.content
        history.append({"role": "assistant", "content": answer})
        
        # Сохраняем (макс 30 сообщ)
        new_hist = history[-30:]
        conn = sqlite3.connect('memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(new_hist)))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
