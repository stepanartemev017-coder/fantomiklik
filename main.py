import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- ДАННЫЕ ---
TOKEN = '8749709641:AAEyio0vr4SNNBeGo8uyrdp7lqlG0q56Pfn8'
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

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Здарова, Степан. Я готов. Нужен прогрев или просто поболтать? Пиши.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    
    if message.text == "ИИ":
        bot.reply_to(message, "Я на связи. Накидать скриптов или обсудим дела?")
        return
    if message.text == "Скрипты":
        bot.reply_to(message, "Тут пока пусто.")
        return

    bot.send_chat_action(chat_id, 'typing')
    
    # Загружаем историю
    history = get_history(chat_id)
    history.append({"role": "user", "content": message.text})

    try:
   completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — универсальный ИИ-ассистент для профессиональных чаттеров на OnlyFans. "
                    "Твоя роль: быть надежным напарником для любого пользователя, который к тебе обратился. "
                    "ТЫ ДОЛЖЕН: \n"
                    "1. Помогать с креативом: писать рассылки (игривые, романтичные, дерзкие, байтовые). \n"
                    "2. Быть экспертом в продажах: советовать, как дожать фана на покупку PPV или чаевые. \n"
                    "3. Быть гибким: уметь подстроиться под стиль общения любой модели. \n"
                    "4. Быть живым собеседником: общаться на 'ты', с юмором, иногда по-дружески подкалывать, но не мешать работе. \n"
                    "Ты — просто мощный ИИ-помощник, который понимает специфику индустрии и всегда на стороне чаттера. Отвечай только на русском."
                )
            }] + history
        )
        
        answer = completion.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        
        # Сохраняем обновленную историю
        save_history(chat_id, history)
        
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
