import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- КЛЮЧИ ---
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

def init_db():
    conn = sqlite3.connect('memory.db')
    conn.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Работаем. Нужна мягкая рассылка или игривый ответ? Пиши вайб.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    if message.text == "ИИ":
        bot.reply_to(message, "Я тут. Давай накидаем что-нибудь уютное или игривое для Fansly.")
        return
    if message.text == "Скрипты":
        bot.reply_to(message, "Тут пока пусто.")
        return

    bot.send_chat_action(chat_id, 'typing')
    
    conn = sqlite3.connect('memory.db')
    res = conn.execute('SELECT messages FROM history WHERE chat_id = ?', (chat_id,)).fetchone()
    history = json.loads(res) if res else []
    conn.close()

    history.append({"role": "user", "content": message.text})
    if len(history) > 30: history = history[-30:]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — профи-ассистент чаттера на Fansly. Ты пишешь тексты от лица модели. "
                    "ТВОЯ ЗАДАЧА: Создавать рассылки, которые выглядят как ЛИЧНЫЕ сообщения. "
                    "СТИЛЬ: Никакой грязи в лоб. Используй игривый вайб, полунамеки, уют. "
                    "Пиши коротко, просто, как живой человек. Без рекламных оборотов. "
                    "Общайся с юзером на 'ты'. Отвечай на русском."
                )
            }] + history
        )
        
        # ИСПРАВЛЕННАЯ СТРОКА:
        answer = completion.choices[0].message.content
        
        history.append({"role": "assistant", "content": answer})
        
        conn = sqlite3.connect('memory.db')
        conn.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
