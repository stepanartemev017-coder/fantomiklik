import telebot
from telebot import types
from groq import Groq

# ВСТАВЬ СВОИ КЛЮЧИ ТУТ (строго в кавычках!)
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo' 
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# --- РАБОТА С ПАМЯТЬЮ (SQLite) ---
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
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else []

def save_history(chat_id, messages):
    if len(messages) > 40: messages = messages[-40:] # Помним последние 40 сообщений
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(messages)))
    conn.commit()
    conn.close()

init_db()

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Выбирай вкладку, фраер:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Скрипты")
def scripts(message):
    bot.reply_to(message, "Тут пока пусто.")

@bot.message_handler(func=lambda message: message.text == "ИИ")
def ai_hi(message):
    bot.reply_to(message, "Здарова фраер, че хотел?")

@bot.message_handler(func=lambda message: True)
def chat(message):
    if message.text in ["ИИ", "Скрипты"]: return

    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    # Загружаем память
    history = get_history(chat_id)
    history.append({"role": "user", "content": message.text})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты умный и дерзкий помощник. Отвечай на 'ты', с юмором. На русском."}] + history
        )
        answer = completion.choices.message.content
        
        # Сохраняем ответ бота в память
        history.append({"role": "assistant", "content": answer})
        save_history(chat_id, history)
        
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка нейронки: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
