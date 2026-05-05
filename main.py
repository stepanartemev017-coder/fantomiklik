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

SYSTEM_PROMPT = (
    "Ты — профи-ассистент чаттера на Fansly. Твой юзер — чаттер (админ), а не фан. "
    "Помогай ему с рассылками и ответами фанам. Тексты для фанов пиши от лица девушки."
)

# --- КЛАВИАТУРЫ ---
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="open_ai"),
        types.InlineKeyboardButton("📜 Скрипты", callback_data="open_scripts")
    )
    return markup

def back_to_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ В главное меню", callback_data="open_main"))
    return markup

# --- КОМАНДЫ ---
@bot.message_handler(commands=['start', 'menu'])
def cmd_menu(message):
    db_op('INSERT OR REPLACE INTO history (chat_id, messages, state) VALUES (?, ?, ?)', 
          (message.chat.id, json.dumps([]), "main"))
    bot.send_message(message.chat.id, "Главное меню. Выбери раздел:", reply_markup=main_menu_markup())

@bot.message_handler(commands=['clear'])
def cmd_clear(message):
    db_op('UPDATE history SET messages = ? WHERE chat_id = ?', (json.dumps([]), message.chat.id))
    bot.send_message(message.chat.id, "🧼 Контекст ИИ очищен. Можно начинать заново.")

# --- ОБРАБОТКА КНОПОК (CALLBACK) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "open_ai":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("ai_chat", call.message.chat.id))
        bot.edit_message_text("Переключено на **ИИ Ассистент**. \nПрисылай запрос (рассылка, ответ фану или стратегия):", 
                              call.message.chat.id, call.message.message_id, reply_markup=back_to_menu_markup())
    
    elif call.data == "open_scripts":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("scripts", call.message.chat.id))
        bot.edit_message_text("Раздел **Скрипты** пока пуст. \nСкоро здесь появятся твои лучшие шаблоны.", 
                              call.message.chat.id, call.message.message_id, reply_markup=back_to_menu_markup())
    
    elif call.data == "open_main":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("main", call.message.chat.id))
        bot.edit_message_text("Главное меню. Выбери раздел:", 
                              call.message.chat.id, call.message.message_id, reply_markup=main_menu_markup())

# --- ОБРАБОТКА ТЕКСТА ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    res = db_op('SELECT messages, state FROM history WHERE chat_id = ?', (chat_id,))
    
    if not res:
        cmd_menu(message)
        return

    history_json, state = res
    
    # Если юзер в главном меню или в скриптах и просто пишет текст
    if state != "ai_chat":
        bot.reply_to(message, "Чтобы общаться с нейронкой, перейди в раздел **ИИ Ассистент**.", reply_markup=main_menu_markup())
        return

    # Если мы в режиме ИИ
    bot.send_chat_action(chat_id, 'typing')
    history = json.loads(history_json)
    
    user_input = f"[Запрос от чаттера]: {message.text}"
    history.append({"role": "user", "content": user_input})
    if len(history) > 20: history = history[-20:]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.8
        )
        answer = completion.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        
        db_op('UPDATE history SET messages = ? WHERE chat_id = ?', (json.dumps(history), chat_id))
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка ИИ: {str(e)}")

if __name__ == '__main__':
    print("Бот запущен с вкладками...")
    bot.infinity_polling()
