import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- КОНФИГУРАЦИЯ ---
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
    "Ты — Ethera, умная девушка и профессиональный ассистент чаттера на Fansly. "
    "Пользователь — твой коллега и босс. Общайся с ним мило, тепло и сдержанно. "
    "Ты помогаешь ему делать рассылки и отвечать фанам. "
    "ПРАВИЛО ДЛЯ ТЕКСТОВ ФАНАМ: Пиши СТРОГО НА 'ТЫ', обращаясь к одному человеку. "
    "Структура: Лайв-контекст -> Игривый вопрос. Никакого множественного числа!"
)

# --- БАЗА ЗНАКОМСТВА (150 ВОПРОСОВ) ---
KNOWING_STAGES = {
    "1": "✨ **ЭТАП 1: ПЕРВОЕ КАСАНИЕ**\n\n`Как прошел твой день?`\n`Чем сейчас занимаешься?`\n`Ты часто заходишь сюда ко мне?`\n`Какое у тебя сегодня настроение?`\n`Любишь кофе или чай по утрам?`\n`Что тебя сегодня порадовало?`\n`Ты больше любишь утро или вечер?`\n`Какая у тебя сейчас погода?`\n`Ты сегодня уже улыбался?`\n`Какое твое любимое время года?`",
    "2": "🌟 **ЭТАП 2: УЗНАЕМ ДРУГ ДРУГА**\n\n`Какой твой любимый фильм?`\n`Где бы ты хотел оказаться прямо сейчас?`\n`Какая твоя самая большая страсть в жизни?`\n`Ты любишь животных? У тебя есть кто-то?`\n`Что тебя больше всего вдохновляет?`\n`Какой самый необычный подарок тебе дарили?`\n`Ты скорее реалист или мечтатель?`\n`Что тебя может по-настоящему удивить?`",
    "3": "🔥 **ЭТАП 3: ФЛИРТ**\n\n`Что в моем профиле зацепило тебя больше всего?`\n`Какое самое романтичное свидание у тебя было?`\n`Что ты подумал, когда впервые увидел мое фото?`\n`Какая часть моего тела тебе кажется самой привлекательной?`\n`Что бы ты сделал, если бы я сейчас была рядом?`\n`Ты любишь, когда тебя слегка дразнят?`",
    "4": "💎 **ЭТАП 4: ДОВЕРИЕ**\n\n`О чем ты мечтаешь, когда остаешься один?`\n`Ты умеешь хранить секреты?`\n`Что для тебя значит настоящее доверие?`\n`Ты веришь в родственные души?`\n`О чем бы ты хотел меня спросить, но стесняешься?`",
    "5": "🔞 **ЭТАП 5: БЛИЗОСТЬ**\n\n`Какая твоя самая смелая фантазия?`\n`Что ты чувствуешь, когда смотришь на мои губы?`\n`Ты любишь доминировать или подчиняться?`\n`Ты готов к экспериментам со мной?`\n`Какое твое финальное желание на сегодня?`"
}

# --- СЦЕНАРИИ СЕКСТИНГА (ПРОГРЕВ) ---
SEXTING_SCENARIOS = (
    "🔥 **ПРОГРЕВ И СЕКСТИНГ (ИНСТРУКЦИИ)**\n\n"
    "1. **СЦЕНАРИЙ: 'СЛУЧАЙНЫЙ КАДР'**\n"
    "— `Ой, пересматривала сейчас галерею и нашла одно фото... я тут такая настоящая. Показать?`\n"
    "— **Тизер:** Фото лица с прикушенной губой.\n"
    "— **Добивка:** `Кажется, ты дар речи потерял... или мне не стоило быть такой откровенной?`\n\n"
    "2. **СЦЕНАРИЙ: 'ВЫБОР ОБРАЗА'**\n"
    "— `Хочу сегодня вечером быть особенной для тебя... Поможешь выбрать белье под это платье?`\n"
    "— **Тизер:** Фото двух комплектов на кровати.\n"
    "— **Добивка:** `Черный — это страсть, а кружево — нежность... Что на мне ты хочешь увидеть первым?`\n\n"
    "3. **СЦЕНАРИЙ: 'ГОРЯЧИЙ СЕКРЕТ'**\n"
    "— `Тссс... я сейчас в людном месте, но на мне нет белья. Это наше преступление на двоих.`\n"
    "— **Тизер:** Селфи с хитрой улыбкой из кафе.\n"
    "— **Добивка:** `Только представь, что я чувствую, зная, что этот секрет только твой...`"
)

# --- ПРОМТЫ РАССЫЛОК ---
PROMPTS = {
    "1": "Сделай 5 личных рассылок 'Красота в мелочах'. Пиши на ТЫ. Темы: свечи, белье, какао, фейл.",
    "2": "Сделай 5 личных рассылок 'Помоги выбрать'. Пиши на ТЫ. Темы: цвет лака, кино, еда, платье.",
    "3": "Накидай 5 личных рассылок 'За кадром'. Пиши на ТЫ. Темы: беспорядок, усталость, идеи, камера села."
}

# --- МЕНЮ ---
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="open_ai"),
        types.InlineKeyboardButton("🤝 Знакомство (150 вопросов)", callback_data="open_knowing"),
        types.InlineKeyboardButton("🔥 Секстинг и Прогрев", callback_data="open_sexting"),
        types.InlineKeyboardButton("📝 Промты для рассылок", callback_data="open_prompts")
    )
    return markup

def knowing_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("1. Легкий интерес", callback_data="get_k_1"),
        types.InlineKeyboardButton("2. Углубление", callback_data="get_k_2"),
        types.InlineKeyboardButton("3. Флирт", callback_data="get_k_3"),
        types.InlineKeyboardButton("4. Доверие", callback_data="get_k_4"),
        types.InlineKeyboardButton("5. Близость", callback_data="get_k_5"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="open_main")
    )
    return markup

def prompts_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"Тема {i}", callback_data=f"get_p_{i}") for i in range(1, 4)]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="open_main"))
    return markup

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start', 'menu'])
def cmd_menu(message):
    db_op('INSERT OR REPLACE INTO history (chat_id, messages, state) VALUES (?, ?, ?)', 
          (message.chat.id, json.dumps([]), "main"))
    bot.send_message(message.chat.id, "Ethera приветствует тебя. Выбери инструмент:", 
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Доступные разделы:", reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "open_ai":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("ai_chat", chat_id))
        bot.edit_message_text("🤖 Режим ИИ активен. Жду твой запрос (рассылка или ответ):", 
                              chat_id, call.message.message_id, reply_markup=main_menu_markup())
    
    elif call.data == "open_knowing":
        bot.edit_message_text("Выбери этап знакомства:", chat_id, call.message.message_id, reply_markup=knowing_menu_markup())
    
    elif call.data.startswith("get_k_"):
        bot.send_message(chat_id, KNOWING_STAGES.get(call.data.replace("get_k_", "")), parse_mode="Markdown")

    elif call.data == "open_sexting":
        bot.send_message(chat_id, SEXTING_SCENARIOS, parse_mode="Markdown")

    elif call.data == "open_prompts":
        bot.edit_message_text("Выбери тему промта для копирования:", chat_id, call.message.message_id, reply_markup=prompts_menu_markup())

    elif call.data.startswith("get_p_"):
        bot.send_message(chat_id, f"Копируй и отправляй ИИ:\n\n`{PROMPTS.get(call.data.replace('get_p_', ''))}`", parse_mode="Markdown")

    elif call.data == "open_main":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("main", chat_id))
        bot.edit_message_text("Главное меню:", chat_id, call.message.message_id, reply_markup=main_menu_markup())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    res = db_op('SELECT messages, state FROM history WHERE chat_id = ?', (chat_id,))
    if not res: return

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
        except:
            bot.reply_to(message, "Ошибка связи с ИИ.")
    else:
        bot.send_message(chat_id, "Для работы включи '🤖 ИИ Ассистент'.", reply_markup=main_menu_markup())

if __name__ == '__main__':
    bot.infinity_polling()
