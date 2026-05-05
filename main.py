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

# --- НАСТРОЙКИ ИИ ---
SYSTEM_PROMPT = (
    "Ты — Ethera, профессиональный AI-ассистент чаттера на Fansly. "
    "Пользователь — твой босс и коллега. Общайся с ним мило, тепло и сдержанно. "
    "Твоя задача: помогать ему писать рассылки и ответы фанам. "
    "ПРАВИЛО: Пиши СТРОГО НА 'ТЫ', обращаясь к одному человеку. "
    "Структура: Лайв-контекст -> Игривый вопрос."
)

# --- СПИСКИ ДАННЫХ ---
KNOWING_LIST = (
    "🤝 **ВОПРОСЫ ДЛЯ ЗНАКОМСТВА**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что на ужин было?` \n9. `Что сейчас слушаешь?` \n10. `Твой рост?` \n"
    "11. `Активный отдых или диван?` \n12. `Твое хобби?` \n13. `Что тебя смешит?` \n14. `Что ценишь в людях?` \n15. `Куда позовешь на свидание?` \n"
    "*(Нажми на вопрос, чтобы скопировать)*"
)

SEXTING_LIST = (
    "🔥 **10 СЦЕНАРИЕВ СЕКСТИНГА**\n\n"
    "1. `Нашла старое фото... я тут такая настоящая. Показать?` \n"
    "2. `Выбираю белье... Поможешь решить, что надеть?` \n"
    "3. `Тссс... я сейчас в людном месте, но на мне нет белья.` \n"
    "4. `Я только что из душа, и тут так прохладно...` \n"
    "5. `Мне приснился очень горячий сон про нас...` \n"
    "6. `Мои руки сегодня такие нежные... С чего мне начать?` \n"
    "7. `В комнате так тихо, я слышу только свои мысли о тебе...` \n"
    "8. `Давай сыграем? Ты говоришь желание, а я — как я его исполню.` \n"
    "9. `Я сегодня была очень вредной... Нуждаюсь в наказании.` \n"
    "10. `Приблизься к экрану... Хочу прошептать тебе кое-что.`"
)

PROMPTS_LIST = (
    "📝 **10 ПРОМТОВ ДЛЯ ИИ**\n\n"
    "1. `Сделай 5 рассылок на тему 'Уютный вечер'. Пиши на ТЫ.` \n"
    "2. `Придумай 5 рассылок 'В магазине белья'. Игриво на ТЫ.` \n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'.` \n"
    "4. `Сделай рассылку-байтер: я начала рассказывать и 'отвлеклась'.` \n"
    "5. `Придумай рассылку про выбор фильма на вечер.` \n"
    "6. `Сделай 3 варианта рассылки про готовку ужина в одной футболке.` \n"
    "7. `Напиши рассылку 'Скучаю': нашла вещь, напомнившую о нем.` \n"
    "8. `Сделай рассылку про плохую погоду и желание согреться.` \n"
    "9. `Напиши 3 дерзких рассылки для тех, кто давно не отвечал.` \n"
    "10. `Придумай рассылку 'Секрет': хочу поделиться личным.`"
)

# --- МЕНЮ (INLINE) ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="ai"),
        types.InlineKeyboardButton("🤝 Знакомство", callback_data="know"),
        types.InlineKeyboardButton("🔥 Секстинг", callback_data="sext"),
        types.InlineKeyboardButton("📝 Промты ИИ", callback_data="prompts"),
        types.InlineKeyboardButton("⬅️ Главное меню", callback_data="menu")
    )
    return markup

# --- ОБРАБОТЧИКИ КОМАНД ---
@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    db_op('INSERT OR REPLACE INTO history (chat_id, messages, state) VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    bot.send_message(message.chat.id, "Ethera на связи. Твой пульт управления:", reply_markup=main_menu())

# --- ОБРАБОТКА НАЖАТИЙ (С ЗАЩИТОЙ ОТ ОШИБОК) ---
@bot.callback_query_handler(func=lambda call: True)
def cb_handler(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    
    try:
        if call.data == "ai":
            db_op('UPDATE history SET state="ai" WHERE chat_id=?', (cid,))
            bot.edit_message_text("🦾 Режим ИИ активен. Жду твой запрос (рассылка или ответ):", cid, mid, reply_markup=main_menu())
        
        elif call.data == "know":
            bot.send_message(cid, KNOWING_LIST, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            
        elif call.data == "sext":
            bot.send_message(cid, SEXTING_LIST, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

        elif call.data == "prompts":
            bot.send_message(cid, PROMPTS_LIST, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

        elif call.data == "menu":
            db_op('UPDATE history SET state="main" WHERE chat_id=?', (cid,))
            bot.edit_message_text("Ethera на связи. Твой пульт управления:", cid, mid, reply_markup=main_menu())
            
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" not in e.description:
            raise e

# --- ОБРАБОТКА ТЕКСТА ---
@bot.message_handler(func=lambda m: True)
def handle_text(m):
    res = db_op('SELECT messages, state FROM history WHERE chat_id=?', (m.chat.id,))
    if not res: return

    history_json, state = res
    if state == "ai":
        bot.send_chat_action(m.chat.id, 'typing')
        history = json.loads(history_json) if history_json else []
        history.append({"role": "user", "content": m.text})
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                temperature=0.8
            )
            answer = completion.choices[0].message.content
            history.append({"role": "assistant", "content": answer})
            db_op('UPDATE history SET messages=? WHERE chat_id=?', (json.dumps(history[-15:]), m.chat.id))
            bot.reply_to(m, answer)
        except:
            bot.reply_to(m, "Ошибка связи с ИИ. Попробуй позже.")
    else:
        bot.send_message(m.chat.id, "Сначала нажми кнопку '🤖 ИИ Ассистент'.", reply_markup=main_menu())

if __name__ == '__main__':
    bot.infinity_polling()
