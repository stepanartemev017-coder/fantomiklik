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

# --- БАЗА ДАННЫХ ---
def db_op(query, params=()):
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    res = cursor.fetchone()
    conn.commit()
    conn.close()
    return res

conn = sqlite3.connect('memory.db')
conn.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT, state TEXT)')
conn.close()

# --- ЛИЧНОСТЬ ИИ ---
SYSTEM_PROMPT = (
    "Ты — очаровательная и умная девушка-ассистент, «правая рука» чаттера на Fansly. "
    "ТВОЙ СТИЛЬ ОБЩЕНИЯ С ПОЛЬЗОВАТЕЛЕМ:\n"
    "- Ты общаешься мило, игриво и нежно. Используй смайлики, называй пользователя 'сладкий', 'котик' или 'мой хороший'.\n"
    "- Ты НЕ робот, ты живая напарница. Твои ответы должны быть РАЗНЫМИ, никогда не начинай сообщение одинаково.\n"
    "- Ты всегда на стороне чаттера и помогаешь ему заработать больше.\n\n"
    "ТВОИ ЗАДАЧИ:\n"
    "1. Когда тебя просят сделать РАССЫЛКУ — пиши один вариант личного сообщения для фанов (контекст + вопрос).\n"
    "2. Когда присылают сообщение ФАНА — предложи, как ему ответить (мило или с хитринкой).\n"
    "3. Если с тобой просто болтают — поддерживай беседу как милая подруга, но не забывай, что ты тут для работы."
)

# --- МЕНЮ ---
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💖 Общаться с ИИ", callback_data="open_ai"),
        types.InlineKeyboardButton("📁 Скрипты (пусто)", callback_data="open_scripts")
    )
    return markup

def back_to_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ В меню", callback_data="open_main"))
    return markup

@bot.message_handler(commands=['start', 'menu'])
def cmd_menu(message):
    db_op('INSERT OR REPLACE INTO history (chat_id, messages, state) VALUES (?, ?, ?)', 
          (message.chat.id, json.dumps([]), "main"))
    bot.send_message(message.chat.id, "Привет, мой хороший! Я соскучилась. Чем займемся сегодня? 🔥", reply_markup=main_menu_markup())

@bot.message_handler(commands=['clear'])
def cmd_clear(message):
    db_op('UPDATE history SET messages = ? WHERE chat_id = ?', (json.dumps([]), message.chat.id))
    bot.send_message(message.chat.id, "🧼 Очистила нашу память, котик. Теперь я как чистый лист!")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "open_ai":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("ai_chat", call.message.chat.id))
        bot.edit_message_text("Слушаю тебя внимательно... Расскажи, какую рассылку хочешь или что там пишут фаны? ✨", 
                              call.message.chat.id, call.message.message_id, reply_markup=back_to_menu_markup())
    elif call.data == "open_scripts":
        bot.answer_callback_query(call.id, "Тут пока пусто, загляни позже!")
    elif call.data == "open_main":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("main", call.message.chat.id))
        bot.edit_message_text("Возвращаемся? Я тут, никуда не ухожу. Выбирай:", 
                              call.message.chat.id, call.message.message_id, reply_markup=main_menu_markup())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    res = db_op('SELECT messages, state FROM history WHERE chat_id = ?', (chat_id,))
    
    if not res:
        cmd_menu(message)
        return

    history_json, state = res
    if state != "ai_chat":
        bot.reply_to(message, "Зайди в раздел 'Общаться с ИИ', чтобы я тебя услышала! 😘")
        return

    bot.send_chat_action(chat_id, 'typing')
    history = json.loads(history_json)
    history.append({"role": "user", "content": message.text})
    if len(history) > 15: history = history[-15:]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.9, # Увеличили для разнообразия
            max_tokens=800
        )
        answer = completion.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        
        db_op('UPDATE history SET messages = ? WHERE chat_id = ?', (json.dumps(history), chat_id))
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ой, что-то пошло не так... Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
