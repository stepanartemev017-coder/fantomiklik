import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- ТВОИ НОВЫЕ КЛЮЧИ ---
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

# Создаем таблицу
db_op('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Работаем на новых ключах! Я в курсе, что мы на Fansly. Что по рассылкам или дожиму?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    
    if message.text in ["ИИ", "Скрипты"]:
        bot.reply_to(message, "На связи. Описывай ситуацию или проси что нужно.")
        return

    bot.send_chat_action(chat_id, 'typing')
    
    # ИСПРАВЛЕНО: Теперь берем первый элемент кортежа [0]
    res = db_op('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    history = json.loads(res[0]) if res else []
    
    history.append({"role": "user", "content": message.text})
    if len(history) > 30: history = history[-30:]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — универсальный ИИ-ассистент для чаттера на Fansly. Твоя задача — помогать во всём. \n"
                    "1. ОТВЕТЫ: Помогай отвечать фанам так, чтобы они влюблялись или покупали. \n"
                    "2. ДОЖИМ: Подсказывай, как закрыть сделку на PPV или кастом. \n"
                    "3. КРЕАТИВ: Делай рассылки (милые, игривые, завлекающие). \n"
                    "4. ОБЩЕНИЕ: Можешь просто обсудить работу. Стиль: живой, на 'ты'. Только на русском."
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
