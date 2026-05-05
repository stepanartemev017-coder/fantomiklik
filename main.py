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
    "ПРАВИЛО ДЛЯ ТЕКСТОВ ФАНАМ: Пиши СТРОГО НА 'ТЫ', обращаясь к одному конкретному человеку. "
    "Используй структуру: Лайв-контекст -> Игривый вопрос."
)

# --- БАЗА ЗНАКОМСТВА (НУМЕРОВАННЫЙ СПИСОК) ---
KNOWING_LIST = (
    "🤝 **СПИСОК ВОПРОСОВ ДЛЯ ЗНАКОМСТВА**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что на ужин было?` \n9. `Что сейчас слушаешь?` \n10. `Твой рост?` \n"
    "11. `Активный отдых или диван?` \n12. `Где мечтаешь побывать?` \n13. `Твой любимый фильм?` \n14. `Веришь в судьбу?` \n15. `Что тебя смешит?` \n"
    "16. `Лучшее воспоминание?` \n17. `Что ценишь в людях?` \n18. `Ты романтик или реалист?` \n19. `О чем мечтаешь в тишине?` \n20. `Что во мне зацепило?` \n"
    "21. `Веришь в химию через экран?` \n22. `О чем стесняешься спросить?` \n23. `Любишь, когда тебя дразнят?` \n24. `Какая часть моего тела манит?` \n25. `Умеешь делать массаж?` \n"
    "26. `Твоя смелая фантазия?` \n27. `Доминировать или подчиняться?` \n28. `Что заводит мгновенно?` \n29. `Как относишься к ролевым?` \n30. `Что хочешь со мной прямо сейчас?`"
)

# --- СЦЕНАРИИ СЕКСТИНГА (ПОЛНЫЕ) ---
SEXTING_LIST = (
    "🔥 **СЦЕНАРИИ ПРОГРЕВА И СЕКСТИНГА**\n\n"
    "1. **СЦЕНАРИЙ: 'СЛУЧАЙНЫЙ КАДР'**\n"
    "— `Ой, пересматривала сейчас галерею и нашла одно фото... я тут такая настоящая. Показать?` \n"
    "— **Тизер:** Лицо/губы. **Добивка:** `Кажется, ты дар речи потерял... 😉` \n\n"
    "2. **СЦЕНАРИЙ: 'ВЫБОР ОБРАЗА'**\n"
    "— `Хочу сегодня вечером быть особенной для тебя... Поможешь выбрать белье под это платье?` \n"
    "— **Тизер:** Белье на кровати. **Добивка:** `Черный — это страсть, а кружево — нежность... Что выберешь?` \n\n"
    "3. **СЦЕНАРИЙ: 'ГОРЯЧИЙ СЕКРЕТ'**\n"
    "— `Тссс... я сейчас в людном месте, но на мне нет белья. Это наше маленькое преступление.` \n"
    "— **Тизер:** Селфи из кафе. **Добивка:** `Только представь, что я чувствую, зная, что этот секрет только твой...` \n\n"
    "4. **СЦЕНАРИЙ: 'ПОСЛЕ ДУША'**\n"
    "— `Я только что из душа, и тут так прохладно... Хочется, чтобы кто-то теплый был рядом.` \n"
    "— **Тизер:** Плечи в полотенце. **Добивка:** `Хочу почувствовать твои руки на своей коже...` \n\n"
    "5. **СЦЕНАРИЙ: 'СОН'**\n"
    "— `Мне приснился очень яркий сон... и ты там был не совсем в одежде. 😊` \n"
    "— **Тизер:** Сонные глаза под одеялом. **Добивка:** `Если я расскажу детали, ты не сможешь работать... Рискнем?`"
)

# --- ПРОМТЫ ДЛЯ ИИ ---
PROMPTS_LIST = (
    "📝 **ПРОМТЫ ДЛЯ РАССЫЛОК (Копируй и шли ИИ)**\n\n"
    "1. `Сделай 5 личных рассылок на тему 'Уютный вечер'. Пиши строго на ТЫ. Структура: контекст + вопрос.` \n\n"
    "2. `Придумай 5 рассылок 'Я в магазине белья'. Пиши игриво на ТЫ, создай интригу.` \n\n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'. Тон нежный, обращение на ТЫ.` \n\n"
    "4. `Сделай рассылку-байкер: я начала что-то рассказывать и 'отвлеклась'. Создай любопытство.`"
)

# --- ИНТЕРФЕЙС ---
def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="ai"),
        types.InlineKeyboardButton("🤝 Знакомство", callback_data="know"),
        types.InlineKeyboardButton("🔥 Секстинг", callback_data="sext"),
        types.InlineKeyboardButton("📝 Промты ИИ", callback_data="prompts"),
        types.InlineKeyboardButton("⬅️ Главное меню", callback_data="menu")
    )
    return m

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    db_op('INSERT OR REPLACE INTO history VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    bot.send_message(message.chat.id, "Ethera на связи. Все инструменты восстановлены.", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Выбери раздел:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    cid = c.message.chat.id
    if c.data == "ai":
        db_op('UPDATE history SET state="ai" WHERE chat_id=?', (cid,))
        bot.edit_message_text("🦾 Режим ИИ активен. Жду твой запрос:", cid, c.message.message_id, reply_markup=main_menu())
    elif c.data == "know":
        bot.send_message(cid, KNOWING_LIST, parse_mode="Markdown")
    elif c.data == "sext":
        bot.send_message(cid, SEXTING_LIST, parse_mode="Markdown")
    elif c.data == "prompts":
        bot.send_message(cid, PROMPTS_LIST, parse_mode="Markdown")
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
        bot.reply_to(m, "Нажми '🤖 ИИ Ассистент', чтобы начать общение.", reply_markup=main_menu())

if __name__ == '__main__':
    bot.infinity_polling()
