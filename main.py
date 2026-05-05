import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# КЛЮЧИ
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
    bot.send_message(message.chat.id, "Я в строю. Могу накидать рассылок, помочь с дожимом фана или просто обсудить ситуацию на аккаунте. Че делаем?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    if message.text in ["ИИ", "Скрипты"]:
        bot.reply_to(message, "На связи. Описывай ситуацию, я включусь.")
        return

    bot.send_chat_action(chat_id, 'typing')
    
    res = db_op('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    history = json.loads(res) if res else []
    history.append({"role": "user", "content": message.text})
    history = history[-30:] # Помним 30 сообщений для нормального контекста

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Вернул мощную модель для умных ответов
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — универсальный ИИ-ассистент для чаттера на Fansly. Твоя задача — помогать во всём. \n"
                    "1. ОТВЕТЫ: Помогай отвечать фанам так, чтобы они влюблялись или покупали. \n"
                    "2. ДОЖИМ: Подсказывай, как технично закрыть сделку на PPV или кастом. \n"
                    "3. КРЕАТИВ: Делай рассылки (милые, игривые, горячие). \n"
                    "4. ОБЩЕНИЕ: Можешь просто обсудить работу или подсказать по фишкам площадки. \n"
                    "Стиль: живой, человечный, без официоза, на 'ты'. Только на русском."
                )
            }] + history
        )
        answer = completion.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        db_op('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

if __name__ == '__main__':
    bot.infinity_polling()
