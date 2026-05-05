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

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('memory.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Здарова. Я в строю. Че надо?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    
    if message.text == "ИИ":
        bot.reply_to(message, "Здарова фраер, че хотел?")
        return
    if message.text == "Скрипты":
        bot.reply_to(message, "Тут пока пусто.")
        return

    bot.send_chat_action(chat_id, 'typing')
    
    cursor.execute('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    res = cursor.fetchone()
    history = json.loads(res[0]) if res else []
    
    history.append({"role": "user", "content": message.text})
    if len(history) > 40: history = history[-40:]

    try:
        # ВОТ ТУТ МЫ СОЗДАЕМ completion
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — умный ассистент. Ты понимаешь специфику работы на OnlyFans (рассылки, чаттинг), "
                    "и помогаешь с этим, если тебя попросят. В остальное время ты просто полезный собеседник. "
                    "Общайся на 'ты', будь сообразительным, иногда по-дружески подкалывай. Отвечай только на русском."
                )
            }] + history
        )
        
        answer = completion.choices[0].message.content
        
        history.append({"role": "assistant", "content": answer})
        cursor.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
        conn.commit()
        
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
