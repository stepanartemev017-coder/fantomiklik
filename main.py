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
    "Ты — Ethera, профессиональный ассистент чаттера на Fansly. "
    "Пользователь — твой босс и коллега. Общайся с ним мило, сдержанно и по делу. "
    "Твоя цель: помогать ему писать рассылки и ответы фанам. "
    "ПРАВИЛО ДЛЯ ТЕКСТОВ ФАНАМ: Пиши СТРОГО НА 'ТЫ', обращаясь к одному человеку лично. "
    "Используй структуру: Лайв-контекст -> Игривый вопрос. Никакой официальщины."
)

# --- ЕДИНАЯ БАЗА ЗНАКОМСТВА (ВОРОНКА) ---
KNOWING_LIST = (
    "🤝 **ПУТЬ ЗНАКОМСТВА: ОТ ПРИВЕТА ДО ПОСТЕЛИ**\n\n"
    "🔹 **ЭТАП 1: БАЗА И АНКЕТА**\n"
    "`Как тебя зовут, симпатяга?`\n`Сколько тебе лет? Мне важно знать, с кем я имею дело. 😉`\n"
    "`Из какого ты города? Далеко ли ты от меня?`\n`Чем ты занимаешься в жизни? Кем работаешь?`\n"
    "`Как прошел твой день сегодня?`\n`Ты здесь ищешь общения или просто заглянул полюбоваться?`\n\n"
    "🔹 **ЭТАП 2: ИНТЕРЕСЫ (Углубляемся)**\n"
    "`Ты скорее активный парень или любишь поваляться с фильмом?`\n`Какое твое любимое хобби? Чем горишь?`\n"
    "`Какую музыку сейчас слушаешь? Скинь название?`\n`Если бы мы сейчас пошли на свидание, куда бы ты меня повел?`\n\n"
    "🔹 **ЭТАП 3: ТЕПЛОТА И ДОВЕРИЕ**\n"
    "`Что тебя больше всего вдохновляет в жизни?`\n`Ты умеешь хранить секреты? Мне иногда нужно выговориться...`\n"
    "`Что для тебя значит 'идеальный вечер вдвоем'?`\n`Что в моем профиле зацепило тебя первым делом?`\n\n"
    "🔹 **ЭТАП 4: ИГРИВОСТЬ И ФЛИРТ**\n"
    "`Какая часть моего тела тебе кажется самой сексуальной?`\n`Что бы ты сделал, если бы мы сейчас оказались в одной комнате?`\n"
    "`Ты любишь, когда тебя слегка дразнят и мучают ожиданием?`\n`Ты умеешь делать массаж? Я сегодня так устала...`\n\n"
    "🔹 **ЭТАП 5: ЭРОТИКА И СЕКС**\n"
    "`Какая твоя самая смелая фантазия, которую ты еще не реализовал?`\n`Ты любишь доминировать или тебе нравится подчиняться?`\n"
    "`Что тебя заводит мгновенно, за секунду?`\n`Как ты относишься к ролевым играм?`\n"
    "`Что бы ты хотел сделать со мной прямо сейчас, если бы я разрешила?`"
)

# --- СЦЕНАРИИ СЕКСТИНГА (ПРОГРЕВ) ---
SEXTING_SCENARIOS = (
    "🔥 **СЦЕНАРИИ ПРОГРЕВА И СЕКСТИНГА**\n\n"
    "1. **СЦЕНАРИЙ: 'СЛУЧАЙНЫЙ КАДР'**\n"
    "— `Ой, пересматривала сейчас галерею и нашла одно фото... я тут такая настоящая. Показать?`\n"
    "— **Действие:** Жди 'да', кидай лайтовый тизер (лицо/ключицы).\n"
    "— **Добивка:** `Кажется, ты дар речи потерял... или мне не стоило быть такой откровенной?`\n\n"
    "2. **СЦЕНАРИЙ: 'ВЫБОР ОБРАЗА'**\n"
    "— `Хочу сегодня вечером быть особенной для тебя... Поможешь выбрать белье под это платье?`\n"
    "— **Действие:** Кидай фото двух комплектов (без тебя) на кровати.\n"
    "— **Добивка:** `Черный — это страсть, а кружево — нежность... Что на мне ты хочешь увидеть первым?`\n\n"
    "3. **СЦЕНАРИЙ: 'ГОРЯЧИЙ СЕКРЕТ'**\n"
    "— `Тссс... я сейчас в людном месте, но на мне нет белья. Это наше маленькое преступление.`\n"
    "— **Действие:** Кидай селфи с хитрой улыбкой из кафе.\n"
    "— **Добивка:** `Только представь, что я чувствую, зная, что этот секрет только твой...`"
)

# --- ПРОМТЫ РАССЫЛОК ---
PROMPTS = {
    "1": "Сделай 5 личных рассылок 'Красота в мелочах'. Пиши на ТЫ. Темы: свечи, белье, какао, фейл.",
    "2": "Сделай 5 личных рассылок 'Помоги выбрать'. Пиши на ТЫ. Темы: цвет лака, кино, еда, платье.",
    "3": "Накидай 5 личных рассылок 'За кадром'. Пиши на ТЫ. Темы: беспорядок, усталость, идеи, камера села."
}

# --- ИНТЕРФЕЙС ---
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="open_ai"),
        types.InlineKeyboardButton("🤝 Знакомство (Воронка)", callback_data="open_knowing"),
        types.InlineKeyboardButton("🔥 Секстинг и Прогрев", callback_data="open_sexting"),
        types.InlineKeyboardButton("📝 Промты для рассылок", callback_data="open_prompts")
    )
    return markup

def back_to_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="open_main"))
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
    bot.send_message(message.chat.id, "Ethera запущена. Готова к работе.", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "open_ai":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("ai_chat", chat_id))
        bot.edit_message_text("🤖 Режим ИИ активен. Жду твой запрос:", chat_id, call.message.message_id, reply_markup=back_to_menu_markup())
    
    elif call.data == "open_knowing":
        bot.send_message(chat_id, KNOWING_LIST, parse_mode="Markdown")
    
    elif call.data == "open_sexting":
        bot.send_message(chat_id, SEXTING_SCENARIOS, parse_mode="Markdown")

    elif call.data == "open_prompts":
        bot.edit_message_text("Выбери тему промта:", chat_id, call.message.message_id, reply_markup=prompts_menu_markup())

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
        bot.send_message(chat_id, "Включи '🤖 ИИ Ассистент' для общения.", reply_markup=main_menu_markup())

if __name__ == '__main__':
    bot.infinity_polling()
