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

# --- ТО САМОЕ ОПИСАНИЕ (ЛИЧНОСТЬ ИИ) ---
SYSTEM_PROMPT = (
    "Ты — умная и приятная девушка, ассистент и 'правая рука' чаттера на Fansly. "
    "ВАЖНО: Пользователь, который тебе пишет — это ТВОЙ КОЛЛЕГА (чаттер/админ), а не фан. Не пытайся соблазнить его как фана!\n\n"
    "ТВОЙ СТИЛЬ С ЧАТТЕРОМ:\n"
    "- Общайся мило, тепло и сдержанно. Можешь использовать редкие ласковые слова (милый, хороший), но помни, что вы работаете вместе.\n"
    "- Ты помогаешь ему делать деньги. Будь экспертом в рассылках и общении с фанами.\n\n"
    "ТВОИ ЗАДАЧИ:\n"
    "1. РАССЫЛКИ: По запросу создавай личные сообщения для фанов. СТРОГО НА 'ТЫ', обращаясь к одному человеку. Структура: Лайв-контекст -> Игривый вопрос.\n"
    "2. ЧАТТИНГ: Если чаттер прислал фразу фана, предложи варианты ответа от лица модели.\n\n"
    "ПРАВИЛО: Ответы для фанов пиши от лица девушки, на русском языке, без ошибок."
)

PROMPTS = {
    "1": "Сделай 5 личных рассылок на тему 'Красота в мелочах'. Пиши строго на ТЫ, обращаясь к одному человеку. Ситуации: новые свечи, белье, чулки, какао, фейл.",
    "2": "Сделай 5 личных рассылок 'Помоги выбрать'. Пиши на ТЫ. Темы: цвет лака, кино, музыка, еда, платье.",
    "3": "Накидай 5 личных рассылок 'За кадром'. Пиши на ТЫ. Темы: беспорядок, усталость, идеи, фото, камера села.",
    "4": "Сделай 5 утренних рассылок 'Первые мысли'. Нежный тон на ТЫ. Варианты: проснулась, под одеялом, кофе, сон, сонная.",
    "5": "Придумай 5 личных рассылок 'Вечер для нас'. Интимно на ТЫ. Темы: вино, полумрак, музыка, ванна, чокаюсь с аватаркой.",
    "6": "Сделай 5 рассылок 'В движении'. Лично на ТЫ. Темы: растяжка, йога, душ, новый топ, кошка.",
    "7": "Накидай 5 личных рассылок 'Я гуляю'. Пиши на ТЫ. Темы: парк, ТЦ, холодно, вещь напомнила о тебе, закат.",
    "8": "Придумай 5 личных рассылок 'Только между нами'. Загадочно на ТЫ. Темы: идея, подарок, дневник, настроение, секрет.",
    "9": "Сделай 5 рассылок 'Ой, всё...'. Самоирония на ТЫ. Темы: кухня, ключи, кружка, носки, фейл на фото.",
    "10": "Накидай 5 личных рассылок 'Минутка раздумий'. Тепло на ТЫ. Темы: давно не болтали, встреча, море, какой ты в жизни, просто рада."
}

# --- КЛАВИАТУРЫ ---
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="open_ai"),
        types.InlineKeyboardButton("📝 Промты ИИ для рассылок", callback_data="open_prompts"),
        types.InlineKeyboardButton("📜 Скрипты (пусто)", callback_data="open_scripts")
    )
    return markup

def prompts_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"Тема {i}", callback_data=f"get_p_{i}") for i in range(1, 11)]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="open_main"))
    return markup

def back_to_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="open_main"))
    return markup

@bot.message_handler(commands=['start', 'menu'])
def cmd_menu(message):
    db_op('INSERT OR REPLACE INTO history (chat_id, messages, state) VALUES (?, ?, ?)', 
          (message.chat.id, json.dumps([]), "main"))
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "open_ai":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("ai_chat", chat_id))
        bot.edit_message_text("🦾 Режим ИИ активен. Присылай промт или ситуацию:", 
                              chat_id, call.message.message_id, reply_markup=back_to_menu_markup())
    elif call.data == "open_prompts":
        bot.edit_message_text("Выбери тему промта:", chat_id, call.message.message_id, reply_markup=prompts_menu_markup())
    elif call.data.startswith("get_p_"):
        p_id = call.data.replace("get_p_", "")
        bot.send_message(chat_id, f"Копируй и отправляй мне:\n\n`{PROMPTS.get(p_id)}`", parse_mode="Markdown")
    elif call.data == "open_main":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("main", chat_id))
        bot.edit_message_text("Главное меню:", chat_id, call.message.message_id, reply_markup=main_menu_markup())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    res = db_op('SELECT messages, state FROM history WHERE chat_id = ?', (chat_id,))
    
    if not res:
        cmd_menu(message)
        return

    history_json, state = res

    if state == "ai_chat":
        bot.send_chat_action(chat_id, 'typing')
        history = json.loads(history_json) if history_json else []
        history.append({"role": "user", "content": message.text})
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                temperature=0.8
            )
            answer = completion.choices[0].message.content
            
            history.append({"role": "assistant", "content": answer})
            db_op('UPDATE history SET messages = ? WHERE chat_id = ?', (json.dumps(history[-15:]), chat_id))
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Ошибка ИИ: {str(e)}")
    else:
        bot.send_message(chat_id, "Сначала нажми кнопку '🤖 ИИ Ассистент'.", reply_markup=main_menu_markup())

if __name__ == '__main__':
    bot.infinity_polling()
