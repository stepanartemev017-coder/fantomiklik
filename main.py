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
    "Пользователь — твой босс. Общайся с ним мило и по делу. "
    "ПРАВИЛО ДЛЯ ТЕКСТОВ ФАНАМ: Пиши СТРОГО НА 'ТЫ', обращаясь к одному человеку. "
    "Используй структуру: Лайв-контекст -> Игривый вопрос."
)

# --- БАЗА ЗНАКОМСТВА (150+ ВОПРОСОВ) ---
KNOWING_LIST = (
    "🤝 **БАЗА ЗНАКОМСТВА (150+ ВОПРОСОВ)**\n\n"
    "🔹 **БЛОК 1: БАЗА**\n"
    "`Как тебя зовут?` `Сколько лет?` `Откуда ты?` `Кем работаешь?` `Нравится работа?` `Как день прошел?` `Ты сейчас отдыхаешь?` `Что на ужин было?` `Ты соня или жаворонок?` `Что сейчас слушаешь?` `Есть питомцы?` `Твой любимый цвет?` `Что тебя улыбнуло?` `Кофе или чай?` `Какая погода?` `Часто тут бываешь?` `Чем занят, когда скучно?` `Любишь готовить?` `Твой рост?` `Ты спортивный?`\n\n"
    "🔹 **БЛОК 2: ИНТЕРЕСЫ**\n"
    "`Активный отдых или диван?` `Где мечтаешь побывать?` `Твой любимый фильм?` `Веришь в судьбу?` `Что тебя смешит?` `Риск или комфорт?` `Лучшее воспоминание?` `Что ценишь в людях?` `Куда позовешь на свидание?` `Ты романтик или реалист?` `Твоя любимая книга?` `Любишь экстрим?` `Любишь море или горы?` `Умеешь играть на чем-то?` `Веришь в интуицию?` `Твое хобби?`\n\n"
    "🔹 **БЛОК 3: ЛИЧНОЕ**\n"
    "`О чем мечтаешь в тишине?` `Что во мне зацепило?` `Легко доверяешь людям?` `Хотел бы приехать?` `Веришь в химию через экран?` `О чем стесняешься спросить?` `Ты ревнивый?` `Твой страх?` `Что для тебя уют?` `Ты когда-нибудь влюблялся в сети?` `Что для тебя верность?` `Умеешь признавать ошибки?` `Что делает тебя счастливым?`\n\n"
    "🔹 **БЛОК 4: ФЛИРТ**\n"
    "`Любишь, когда тебя дразнят?` `Какая часть моего тела манит?` `Умеешь делать массаж?` `Что сделаешь при встрече?` `Любишь поцелуи в шею?` `Ты нежный или властный?` `Твой любимый запах?` `Часто думаешь обо мне?` `Любишь обниматься?` `Что тебя во мне заводит?` `Любишь шепот на ушко?` `Твой пульс сейчас участился? 😉`\n\n"
    "🔹 **БЛОК 5: СЕКС**\n"
    "`Твоя смелая фантазия?` `Доминировать или подчиняться?` `Что заводит мгновенно?` `Как относишься к ролевым?` `Что хочешь со мной прямо сейчас?` `Любишь грязные мысли?` `Как относишься к игрушкам?` `Самое необычное место?` `Любишь прелюдию?` `Любимая поза?` `Свет включен или выключен?` `Твой рекорд по времени?` `Любишь кусаться?`"
)

# --- СЦЕНАРИИ СЕКСТИНГА ---
SEXTING_SCENARIOS = (
    "🔥 **СЕКСТИНГ И ПРОГРЕВ**\n\n"
    "1. `Нашла старое фото... я тут такая настоящая. Показать?` (Тизер: лицо/губы)\n"
    "2. `Выбираю белье... Поможешь решить, что надеть?` (Тизер: белье на кровати)\n"
    "3. `Я в людном месте, но на мне нет белья... это наш секрет.` (Тизер: селфи из кафе)\n"
    "4. `Только из душа, мне так не хватает твоих рук...` (Тизер: плечи в полотенце)\n"
    "5. `Мне приснился очень горячий сон про нас...` (Тизер: сонные глаза под одеялом)"
)

# --- ИНТЕРФЕЙС ---
def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="ai"),
        types.InlineKeyboardButton("🤝 Знакомство (150+ вопросов)", callback_data="know"),
        types.InlineKeyboardButton("🔥 Секстинг и Прогрев", callback_data="sext"),
        types.InlineKeyboardButton("⬅️ Главное меню", callback_data="menu")
    )
    return m

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    db_op('INSERT OR REPLACE INTO history VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    bot.send_message(message.chat.id, "Ethera на связи. Погнали?", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Выбери раздел:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    cid = c.message.chat.id
    if c.data == "ai":
        db_op('UPDATE history SET state="ai" WHERE chat_id=?', (cid,))
        bot.edit_message_text("🦾 Режим ИИ. Пиши свой запрос (рассылка/ответ):", cid, c.message.message_id, reply_markup=main_menu())
    elif c.data == "know":
        bot.send_message(cid, KNOWING_LIST, parse_mode="Markdown")
    elif c.data == "sext":
        bot.send_message(cid, SEXTING_SCENARIOS, parse_mode="Markdown")
    elif c.data == "menu":
        db_op('UPDATE history SET state="main" WHERE chat_id=?', (cid,))
        bot.edit_message_text("Главное меню:", cid, c.message.message_id, reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    res = db_op('SELECT messages, state FROM history WHERE chat_id=?', (m.chat.id,))
    if res and res[1] == "ai":
        bot.send_chat_action(m.chat.id, 'typing')
        hist = json.loads(res[0]); hist.append({"role": "user", "content": m.text})
        try:
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}] + hist)
            ans = comp.choices[0].message.content
            hist.append({"role": "assistant", "content": ans})
            db_op('UPDATE history SET messages=? WHERE chat_id=?', (json.dumps(hist[-15:]), m.chat.id))
            bot.reply_to(m, ans)
        except: bot.reply_to(m, "Ошибка ИИ.")
    else:
        bot.reply_to(m, "Сначала нажми '🤖 ИИ Ассистент'.", reply_markup=main_menu())

if __name__ == '__main__':
    bot.infinity_polling()
