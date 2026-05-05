import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- ТВОИ ДАННЫЕ ---
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# --- ФУНКЦИИ БАЗЫ ДАННЫХ (БЕЗОПАСНЫЕ) ---
def init_db():
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
    conn.commit()
    conn.close()

def get_history(chat_id):
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    res = cursor.fetchone()
    conn.close()
    return json.loads(res[0]) if res else []

def save_history(chat_id, history):
    if len(history) > 40: history = history[-40:]
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
    conn.commit()
    conn.close()

# Инициализируем БД один раз при запуске
init_db()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Здарова! Я на связи. Нужен прогрев для фанов или просто поболтать? Пиши.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    
    # Обработка кнопок
    if message.text == "ИИ":
        bot.reply_to(message, "Я в деле. Накидать идей для рассылок или обсудим стратегию?")
        return
    if message.text == "Скрипты":
        bot.reply_to(message, "Тут пока пусто, скрипты на базе будут позже.")
        return

    bot.send_chat_action(chat_id, 'typing')
    
    # ЧИТАЕМ ИСТОРИЮ (безопасно)
    history = get_history(chat_id)
    history.append({"role": "user", "content": message.text})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — универсальный ИИ-ассистент для профессиональных чаттеров на OnlyFans. "
                    "Твоя роль: быть надежным напарником для любого пользователя. "
                    "Помогай с креативом, рассылками, советами по продажам и дожиму фанов. "
                    "Общайся на 'ты', с юмором, иногда дерзко подкалывай, но не мешай работе. "
                    "Ты понимаешь специфику индустрии и всегда на стороне чаттера. Отвечай только на русском."
                )
            }] + history
        )
        
        answer = completion.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        
        # СОХРАНЯЕМ ИСТОРИЮ (безопасно)
        save_history(chat_id, history)
        
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
