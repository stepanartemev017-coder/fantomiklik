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

# Создание таблицы (обновлено)
conn = sqlite3.connect('memory.db')
conn.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT, state TEXT)')
conn.close()

# --- ЛИЧНОСТЬ ИИ ---
SYSTEM_PROMPT = (
    "Ты — Ethera, профессиональный ИИ-ассистент чаттера на Fansly. "
    "Твой пользователь — чаттер (коллега), общайся с ним мило, тепло и по делу. "
    "ПРАВИЛА ГЕНЕРАЦИИ ДЛЯ ФАНОВ: Пиши СТРОГО НА 'ТЫ', обращаясь к одному человеку. "
    "Стиль: живой, игривый. Структура: Контекст + Вопрос."
)

# --- СПИСКИ ДАННЫХ ---
KNOWING_LIST = (
    "🤝 **СПИСОК ВОПРОСОВ ДЛЯ ЗНАКОМСТВА**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что на ужин было?` \n9. `Что сейчас слушаешь?` \n10. `Твой рост?` \n"
    "11. `Активный отдых или диван?` \n12. `Твое любимое хобби?` \n13. `Что тебя смешит?` \n14. `Что ценишь в людях?` \n15. `Куда позовешь на свидание?` \n"
    "16. `О чем мечтаешь в тишине?` \n17. `Что во мне зацепило?` \n18. `Веришь в химию через экран?` \n19. `Любишь, когда тебя дразнят?` \n20. `Какая часть моего тела манит?` \n"
    "21. `Умеешь делать массаж?` \n22. `Ты нежный или властный?` \n23. `Твой любимый запах?` \n24. `Любишь обниматься?` \n25. `Твоя смелая фантазия?` \n"
    "26. `Доминировать или подчиняться?` \n27. `Что заводит мгновенно?` \n28. `Как относишься к ролевым?` \n29. `Что хочешь со мной сейчас?` \n30. `Твое главное желание на ночь?` \n"
    "*(Нажми на вопрос, чтобы скопировать)*"
)

SEXTING_LIST = (
    "🔥 **10 СЦЕНАРИЕВ ПРОГРЕВА**\n\n"
    "1. **'СЛУЧАЙНЫЙ КАДР'**\n`Ой, нашла старое фото... я тут такая настоящая. Показать?` \n*Дальше:* Описывай свои чувства или наряд.\n\n"
    "2. **'ВЫБОР ОБРАЗА'**\n`Хочу сегодня вечером быть особенной... Поможешь выбрать белье?` \n*Дальше:* Описывай два варианта на выбор.\n\n"
    "3. **'ГОРЯЧИЙ СЕКРЕТ'**\n`Тссс... я сейчас в людном месте, но на мне нет белья...` \n*Дальше:* Расскажи, как тебе волнительно.\n\n"
    "4. **'ПОСЛЕ ДУША'**\n`Я только что из душа, и тут так прохладно... Хочется тепла.` \n*Дальше:* Описывай капли воды на коже.\n\n"
    "5. **'СОН'**\n`Мне приснился очень яркий сон... и ты там был не совсем в одежде. 😊` \n*Дальше:* Рассказывай детали сна.\n\n"
    "6. **'ПРИКОСНОВЕНИЯ'**\n`Мои руки сегодня такие нежные... С чего мне начать?` \n\n"
    "7. **'БЛИЗОСТЬ'**\n`В комнате так тихо, слышу только мысли о тебе...` \n\n"
    "8. **'ИГРА'**\n`Давай сыграем? Ты говоришь желание, а я — как я его исполню.` \n\n"
    "9. **'НАКАЗАНИЕ'**\n`Я сегодня была вредной девочкой... Нуждаюсь в наказании.` \n\n"
    "10. **'ШЕПОТ'**\n`Приблизься... Хочу прошептать тебе кое-что горячее.`"
)

PROMPTS_LIST = (
    "📝 **10 ПРОМТОВ ДЛЯ РАССЫЛОК**\n\n"
    "1. `Сделай 5 рассылок на тему 'Уютный вечер'. Пиши на ТЫ.`\n"
    "2. `Придумай 5 рассылок 'В магазине белья'. Игриво на ТЫ.`\n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'.`\n"
    "4. `Сделай рассылку-байтер: я начала что-то рассказывать и 'отвлеклась'.`\n"
    "5. `Придумай рассылку про выбор фильма на вечер.`\n"
    "6. `Сделай 3 варианта рассылки про готовку ужина в одной футболке.`\n"
    "7. `Напиши рассылку 'Скучаю': нашла вещь, напомнившую о нем.`\n"
    "8. `Сделай рассылку про плохую погоду и желание согреться.`\n"
    "9. `Напиши 3 дерзких рассылки для тех, кто долго не отвечал.`\n"
    "10. `Придумай рассылку 'Секрет': хочу поделиться личным.`"
)

# --- МЕНЮ (INLINE) ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="set_ai"),
        types.InlineKeyboardButton("🤝 Знакомство", callback_data="show_know"),
        types.InlineKeyboardButton("🔥 Секстинг", callback_data="show_sext"),
        types.InlineKeyboardButton("📝 Промты ИИ", callback_data="show_prompts")
    )
    return markup

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    db_op('INSERT OR REPLACE INTO history (chat_id, messages, state) VALUES (?, ?, ?)', 
          (message.chat.id, json.dumps([]), "main"))
    bot.send_message(message.chat.id, "Ethera на связи. Твой пульт управления:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def cb_handler(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    
    if call.data == "set_ai":
        db_op('UPDATE history SET state="ai" WHERE chat_id=?', (cid,))
        bot.answer_callback_query(call.id, "Режим ИИ включен!")
        bot.edit_message_text("🦾 Режим ИИ активен. Пиши свой запрос (рассылка или ответ):", cid, mid, reply_markup=main_menu())
    
    elif call.data == "show_know":
        bot.send_message(cid, KNOWING_LIST, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        
    elif call.data == "show_sext":
        bot.send_message(cid, SEXTING_LIST, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    elif call.data == "show_prompts":
        bot.send_message(cid, PROMPTS_LIST, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

# --- ГЛАВНЫЙ ОБРАБОТЧИК ТЕКСТА ---
@bot.message_handler(func=lambda m: True)
def handle_text(m):
    res = db_op('SELECT messages, state FROM history WHERE chat_id=?', (m.chat.id,))
    
    if not res:
        cmd_start(m)
        return

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
        except Exception as e:
            bot.reply_to(m, f"Ошибка ИИ: {str(e)}")
    else:
        bot.send_message(m.chat.id, "Сначала нажми кнопку '🤖 ИИ Ассистент', чтобы я начала отвечать.", reply_markup=main_menu())

if __name__ == '__main__':
    bot.infinity_polling()
