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

# --- СИСТЕМНЫЕ НАСТРОЙКИ ИИ ---
SYSTEM_PROMPT = (
    "Ты — Ethera, профессиональный AI-ассистент чаттера на Fansly. "
    "Твой пользователь — это чаттер (коллега), общайся с ним тепло и по делу. "
    "Твоя цель: помогать увеличивать доход через крутые тексты.\n\n"
    "ПРАВИЛА ГЕНЕРАЦИИ ДЛЯ ФАНОВ:\n"
    "1. Пиши СТРОГО НА 'ТЫ', обращаясь к ОДНОМУ человеку лично.\n"
    "2. СТИЛЬ: Женственный, игривый, живой. Никакой рекламы.\n"
    "3. СТРУКТУРА: Лайв-контекст + вовлекающий вопрос.\n"
    "4. Если нужно продать PPV — делай это через флирт и создание ценности."
)

# --- 1. СПИСОК ВОПРОСОВ (Знакомство) ---
KNOWING_LIST = (
    "🤝 **СПИСОК ВОПРОСОВ ДЛЯ ЗНАКОМСТВА**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что сейчас слушаешь?` \n9. `Твой рост?` \n10. `Веришь в судьбу?` \n"
    "11. `Что во мне зацепило?` \n12. `Веришь в химию через экран?` \n13. `Какая часть моего тела манит?` \n14. `Умеешь делать массаж?` \n15. `Твоя смелая фантазия?` \n"
    "*(Нажми на вопрос, чтобы скопировать)*"
)

# --- 2. 10 СЦЕНАРИЕВ СЕКСТИНГА ---
SEXTING_LIST = (
    "🔥 **10 СЦЕНАРИЕВ ПРОГРЕВА**\n\n"
    "1. **'СЛУЧАЙНЫЙ КАДР'**\n`Ой, нашла старое фото... я тут такая настоящая. Показать?` \n*Дальше:* Описывай свои чувства или наряд.\n\n"
    "2. **'ВЫБОР ОБРАЗА'**\n`Хочу сегодня вечером быть особенной... Поможешь выбрать белье?` \n*Дальше:* Описывай два варианта на выбор.\n\n"
    "3. **'ГОРЯЧИЙ СЕКРЕТ'**\n`Тссс... я сейчас в людном месте, но на мне нет белья...` \n*Дальше:* Расскажи, как тебе волнительно.\n\n"
    "4. **'ПОСЛЕ ДУША'**\n`Я только что из душа, тут так прохладно... Хочется тепла.` \n*Дальше:* Описывай капли воды на коже.\n\n"
    "5. **'СОН'**\n`Мне приснился очень яркий сон... и ты там был не совсем в одежде. 😊` \n*Дальше:* Рассказывай детали сна.\n\n"
    "6. **'ПРИКОСНОВЕНИЯ'**\n`Мои руки сегодня такие нежные... С чего мне начать?` \n\n"
    "7. **'БЛИЗОСТЬ'**\n`В комнате так тихо, слышу только мысли о тебе...` \n\n"
    "8. **'ИГРА'**\n`Давай сыграем? Ты говоришь желание, а я — как я его исполню.` \n\n"
    "9. **'НАКАЗАНИЕ'**\n`Я сегодня была вредной девочкой... Нуждаюсь в наказании.` \n\n"
    "10. **'ШЕПОТ'**\n`Приблизься... Хочу прошептать тебе кое-что горячее.`"
)

# --- 3. 10 ПРОМТОВ ДЛЯ ИИ ---
PROMPTS_LIST = (
    "📝 **10 ПРОМТОВ ДЛЯ РАССЫЛОК**\n\n"
    "1. `Сделай 5 рассылок на тему 'Уютный вечер'. Пиши на ТЫ.`\n"
    "2. `Придумай 5 рассылок 'В магазине белья'. Игриво на ТЫ.`\n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'.`\n"
    "4. `Сделай рассылку-байтер: я начала рассказывать и 'отвлеклась'.`\n"
    "5. `Придумай рассылку про выбор фильма на вечер.`\n"
    "6. `Сделай 3 варианта рассылки про готовку ужина в одной футболке.`\n"
    "7. `Напиши рассылку 'Скучаю': нашла вещь, напомнившую о нем.`\n"
    "8. `Сделай рассылку про плохую погоду и желание согреться.`\n"
    "9. `Напиши 3 дерзких рассылки для тех, кто долго не отвечал.`\n"
    "10. `Придумай рассылку 'Секрет': хочу поделиться личным.`"
)

# --- КЛАВИАТУРА ---
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🤖 ИИ Ассистент"),
        types.KeyboardButton("🤝 Знакомство"),
        types.KeyboardButton("🔥 Секстинг"),
        types.KeyboardButton("📝 Промты ИИ")
    )
    return markup

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    # Очищаем состояние при старте
    db_op('INSERT OR REPLACE INTO history VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    bot.send_message(message.chat.id, "Ethera запущена. Твои инструменты внизу:", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    text = message.text

    # Маршрутизация кнопок
    if text == "🤖 ИИ Ассистент":
        db_op('UPDATE history SET state="ai" WHERE chat_id=?', (chat_id,))
        bot.send_message(chat_id, "🦾 Режим ИИ активен. Отправь ситуацию или промт:")
        return
    elif text == "🤝 Знакомство":
        bot.send_message(chat_id, KNOWING_LIST, parse_mode="Markdown")
        return
    elif text == "🔥 Секстинг":
        bot.send_message(chat_id, SEXTING_LIST, parse_mode="Markdown")
        return
    elif text == "📝 Промты ИИ":
        bot.send_message(chat_id, PROMPTS_LIST, parse_mode="Markdown")
        return

    # Логика ИИ
    res = db_op('SELECT messages, state FROM history WHERE chat_id=?', (chat_id,))
    if res and res[1] == "ai":
        bot.send_chat_action(chat_id, 'typing')
        history = json.loads(res[0])
        history.append({"role": "user", "content": text})
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                temperature=0.8
            )
            answer = completion.choices[0].message.content
            history.append({"role": "assistant", "content": answer})
            db_op('UPDATE history SET messages=? WHERE chat_id=?', (json.dumps(history[-15:]), chat_id))
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Ошибка ИИ: {str(e)}")
    else:
        bot.send_message(chat_id, "Выбери раздел в меню клавиатуры.", reply_markup=main_keyboard())

if __name__ == '__main__':
    bot.infinity_polling()
