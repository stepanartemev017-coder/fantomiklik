import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- ТВОИ КЛЮЧИ ---
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('memory.db')
    conn.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Бот запущен. Я готов помогать с Fansly. Какая задача стоит сейчас?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    
    # Обработка кнопок меню
    if message.text == "ИИ":
        bot.reply_to(message, "На связи. Нужны идеи для рассылок или помощь в ответах фанам?")
        return
    if message.text == "Скрипты":
        bot.reply_to(message, "Раздел со скриптами пока пуст.")
        return

    bot.send_chat_action(chat_id, 'typing')
    
    # Читаем историю из БД
    conn = sqlite3.connect('memory.db')
    res = conn.execute('SELECT messages FROM history WHERE chat_id = ?', (chat_id,)).fetchone()
    history = json.loads(res) if res else []
    conn.close()

    history.append({"role": "user", "content": message.text})
    if len(history) > 30: history = history[-30:]

    try:
        # ЗАПРОС К НЕЙРОНКЕ
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — профессиональный ассистент чаттера на Fansly. Твоя единственная задача: помогать юзеру продавать контент. "
                    "Ты эксперт в рассылках, байтах и дожиме фанов на покупку PPV. "
                    "Общайся на 'ты', будь максимально конструктивным, коротким и четким. "
                    "Если просят текст для фана — пиши его сразу без лишних вступлений. "
                    "Ты отлично понимаешь функционал Fansly (тиры, платные сообщения, подписки). "
                    "Отвечай только на русском языке."
                )
            }] + history
        )
        
        answer = completion.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        
        # Сохраняем историю обратно в БД
        conn = sqlite3.connect('memory.db')
        conn.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, answer)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
