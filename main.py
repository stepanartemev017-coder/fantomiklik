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

# БАЗА ДАННЫХ
def db_op(query, params=()):
    conn = sqlite3.connect('memory.db')
    res = conn.execute(query, params).fetchone()
    conn.commit()
    conn.close()
    return res

db_op('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Бот готов. Нужна рассылка в личку фанам или помощь с ответом? Пиши, сделаем красиво.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    
    if message.text in ["ИИ", "Скрипты"]:
        bot.reply_to(message, "Я на связи. Какую задачу решаем?")
        return

    bot.send_chat_action(chat_id, 'typing')
    
    res = db_op('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    history = json.loads(res[0]) if res and res[0] else []
    
    history.append({"role": "user", "content": message.text})
    if len(history) > 30: history = history[-30:]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — профи-ассистент чаттера на Fansly. ты помогаешь чаттеру в работе на анкетах. во многих вопросах таких как рассылки, помощь в диалоге с фаном, добив фана на покупку. \n"
                    "ПРАВИЛА ДЛЯ РАССЫЛОК: \n"
                    "1. Каждое сообщение должно выглядеть как ЛИЧНОЕ и живое (Mass Message). \n"
                    "2. СТРУКТУРА: Теплое приветствие -> Текущий контекст (например: только вышла из душа, лежу в постели, смотрю фильм, вернулась с прогулки) -> Игривый/теплый вопрос по теме. \n"
                    "3. СТИЛЬ: Никакой рекламы! Только естественная речь, мягкая интрига и теплота. \n"
                    "4. ЗАДАЧА: Сделать так, чтобы фан почувствовал близость и захотел ответить. \n"
                    "Общайся с юзером на 'ты', помогай с дожимом и PPV. Отвечай только на русском."
                )
            }] + history
        )
        
        answer = completion.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        
        db_op('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
