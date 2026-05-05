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

# --- СПИСОК ПРОМТОВ (ЛИЧНОЕ ОБРАЩЕНИЕ НА ТЫ) ---
PROMPTS = {
    "1": "Сделай 5 личных рассылок на тему 'Красота в мелочах'. Ситуации: 1. Новые свечи. 2. Свежее белье. 3. Любимые чулки. 4. Какао у окна. 5. Лайв-фейл. ПРАВИЛО: Пиши строго на ТЫ, обращаясь к одному человеку лично.",
    "2": "Придумай 5 личных рассылок 'Помоги мне определиться'. Ситуации: 1. Цвет лака. 2. Кино на вечер. 3. Музыка. 4. Еда. 5. Выбор платья. ПРАВИЛО: Только личное обращение на ТЫ.",
    "3": "Накидай 5 личных рассылок 'За кадром'. Ситуации: 1. Беспорядок. 2. Усталость. 3. Идеи. 4. Старые фото. 5. Лайв: камера села. ПРАВИЛО: Пиши лично на ТЫ, как секрет другу.",
    "4": "Сделай 5 утренних рассылок 'Первые мысли'. Варианты: 1. Только проснулась. 2. Под одеялом. 3. Кофе. 4. Сон. 5. Лайв: сонная. ПРАВИЛО: Теплый, нежный тон на ТЫ.",
    "5": "Придумай 5 личных рассылок 'Вечер только для нас'. Ситуации: 1. Вино. 2. Полумрак. 3. Музыка. 4. Ванна. 5. Чокаюсь с аватаркой. ПРАВИЛО: Интимный вайб на ТЫ.",
    "6": "Сделай 5 рассылок 'В движении'. Ситуации: 1. Растяжка. 2. Йога. 3. Душ. 4. Топ. 5. Лайв: кошка. ПРАВИЛО: Энергично и лично на ТЫ.",
    "7": "Накидай 5 личных рассылок 'Я гуляю'. Ситуации: 1. Парк. 2. ТЦ. 3. Холодно. 4. Вещь напомнила о тебе. 5. Закат. ПРАВИЛО: Пиши на ТЫ, будто скучаешь.",
    "8": "Придумай 5 личных рассылок 'Только между нами'. Ситуации: 1. Безумная идея. 2. Подарок. 3. Дневник. 4. Настроение. 5. Секрет. ПРАВИЛО: Загадочный тон на ТЫ.",
    "9": "Сделай 5 рассылок 'Ой, всё...'. Ситуации: 1. Кухня. 2. Ключи. 3. Кружка. 4. Носки. 5. Фейл на фото. ПРАВИЛО: Самоирония и обращение на ТЫ.",
    "10": "Накидай 5 личных рассылок 'Минутка раздумий'. Варианты: 1. Давно не болтали. 2. Вспомнила встречу. 3. К морю. 4. Какой ты в жизни. 5. Просто рада тебе. ПРАВИЛО: Искренне и на ТЫ."
}

SYSTEM_PROMPT = (
    "Ты — ассистент чаттера на Fansly. ГЛАВНОЕ ПРАВИЛО: Пиши СТРОГО НА ТЫ, обращаясь к одному человеку. "
    "Стиль: милый, сдержанный, женственный. Лайв-контекст + Вопрос в конце."
)

# --- ИНТЕРФЕЙС (INLINE КНОПКИ ОСТАЮТСЯ) ---
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

# --- КОМАНДЫ ---
@bot.message_handler(commands=['start', 'menu'])
def cmd_menu(message):
    db_op('INSERT OR REPLACE INTO history (chat_id, messages, state) VALUES (?, ?, ?)', 
          (message.chat.id, json.dumps([]), "main"))
    # Эта строка убирает нижнюю панель кнопок, но оставляет кнопки в сообщении
    bot.send_message(message.chat.id, "Панель управления обновлена.", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu_markup())

@bot.message_handler(commands=['clear'])
def cmd_clear(message):
    db_op('UPDATE history SET messages = ? WHERE chat_id = ?', (json.dumps([]), message.chat.id))
    bot.send_message(message.chat.id, "🧼 История диалога очищена.")

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "open_ai":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("ai_chat", call.message.chat.id))
        bot.edit_message_text("🤖 Режим ИИ. Присылай промт или ситуацию:", 
                              call.message.chat.id, call.message.message_id, reply_markup=back_to_menu_markup())
    elif call.data == "open_prompts":
        bot.edit_message_text("Выбери тему промта (нажми, чтобы скопировать):", 
                              call.message.chat.id, call.message.message_id, reply_markup=prompts_menu_markup())
    elif call.data.startswith("get_p_"):
        p_id = call.data.replace("get_p_", "")
        text = PROMPTS.get(p_id)
        bot.send_message(call.message.chat.id, f"Копируй и отправляй мне:\n\n`{text}`", parse_mode="Markdown")
    elif call.data == "open_main":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("main", call.message.chat.id))
        bot.edit_message_text("Главное меню:", 
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
    if state != "ai_chat":
        bot.send_message(chat_id, "Сначала нажми кнопку '🤖 ИИ Ассистент', чтобы я начала отвечать.", 
                         reply_markup=main_menu_markup())
        return

    bot.send_chat_action(chat_id, 'typing')
    history = json.loads(history_json)
    history.append({"role": "user", "content": message.text})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.8
        )
        answer = completion.choices.message.content
        history.append({"role": "assistant", "content": answer})
        db_op('UPDATE history SET messages = ? WHERE chat_id = ?', (json.dumps(history[-15:]), chat_id))
        bot.reply_to(message, answer)
    except:
        bot.reply_to(message, "Ошибка связи с ИИ.")

if __name__ == '__main__':
    bot.infinity_polling()
