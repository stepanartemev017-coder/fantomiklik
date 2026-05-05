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
    "Структура: Лайв-контекст -> Игривый вопрос."
)

# --- 1. СПИСОК ВОПРОСОВ (Знакомство) ---
KNOWING_LIST = (
    "🤝 **ВОПРОСЫ ДЛЯ ЗНАКОМСТВА**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что на ужин было?` \n9. `Что сейчас слушаешь?` \n10. `Твой рост?` \n"
    "11. `Активный отдых или диван?` \n12. `Где мечтаешь побывать?` \n13. `Твой любимый фильм?` \n14. `Веришь в судьбу?` \n15. `Что тебя смешит?` \n"
    "16. `Лучшее воспоминание?` \n17. `Что ценишь в людях?` \n18. `Ты романтик или реалист?` \n19. `О чем мечтаешь в тишине?` \n20. `Что во мне зацепило?` \n"
    "21. `Веришь в химию через экран?` \n22. `О чем стесняешься спросить?` \n23. `Любишь, когда тебя дразнят?` \n24. `Какая часть моего тела манит?` \n25. `Умеешь делать массаж?` \n"
    "*(Просто нажми на вопрос, чтобы скопировать)*"
)

# --- 2. 10 СЦЕНАРИЕВ СЕКСТИНГА ---
SEXTING_LIST = (
    "🔥 **10 СЦЕНАРИЕВ ПРОГРЕВА**\n\n"
    "1. **'СЛУЧАЙНЫЙ КАДР'**\n`Ой, пересматривала сейчас галерею и нашла одно фото... я тут такая настоящая. Показать?` \n*Дальше:* Описывай свои чувства или наряд.\n\n"
    "2. **'ВЫБОР ОБРАЗА'**\n`Хочу сегодня вечером быть особенной для тебя... Поможешь выбрать белье под это платье?` \n*Дальше:* Описывай два варианта на выбор.\n\n"
    "3. **'ГОРЯЧИЙ СЕКРЕТ'**\n`Тссс... я сейчас в людном месте, но на мне нет белья. Это наше маленькое преступление.` \n*Дальше:* Расскажи, как тебе волнительно.\n\n"
    "4. **'ПОСЛЕ ДУША'**\n`Я только что из душа, и тут так прохладно... Хочется, чтобы кто-то теплый был рядом.` \n*Дальше:* Описывай капли воды на коже.\n\n"
    "5. **'СОН'**\n`Мне приснился очень яркий сон... и ты там был не совсем в одежде. 😊` \n*Дальше:* Рассказывай детали сна.\n\n"
    "6. **'ПРИКОСНОВЕНИЯ'**\n`Мои руки сегодня такие нежные... Хочу прикоснуться к тебе, с какого места мне начать?` \n\n"
    "7. **'БЛИЗОСТЬ'**\n`В комнате так тихо, я слышу только свое дыхание и мысли о тебе...` \n\n"
    "8. **'ИГРА'**\n`Давай сыграем? Ты говоришь свое желание, а я — как я его исполню.` \n\n"
    "9. **'НАКАЗАНИЕ'**\n`Я сегодня была очень вредной девочкой... Кажется, мне нужно наказание. Справишься?` \n\n"
    "10. **'ШЕПОТ'**\n`Приблизься к экрану... Хочу прошептать тебе кое-что, от чего у тебя пойдут мурашки.`"
)

# --- 3. 10 ПРОМТОВ ДЛЯ ИИ ---
PROMPTS_LIST = (
    "📝 **10 ПРОМТЫ ДЛЯ РАССЫЛОК**\n\n"
    "1. `Сделай 5 рассылок на тему 'Уютный вечер'. Пиши строго на ТЫ. Лайв-контекст + вопрос.`\n"
    "2. `Придумай 5 рассылок 'Я в магазине белья'. Игриво на ТЫ, создай интригу.`\n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'. Тон нежный, на ТЫ.`\n"
    "4. `Сделай рассылку-байтер: я начала рассказывать и 'отвлеклась'.`\n"
    "5. `Придумай рассылку про выбор фильма на вечер.`\n"
    "6. `Сделай 3 варианта рассылки про готовку ужина в одной футболке.`\n"
    "7. `Напиши рассылку 'Скучаю': нашла вещь, которая напомнила мне о нем.`\n"
    "8. `Сделай рассылку про плохую погоду и желание согреться вдвоем.`\n"
    "9. `Напиши 3 дерзких рассылки для тех, кто долго не отвечал.`\n"
    "10. `Придумай рассылку 'Секрет': хочу поделиться тем, что знаю только я.`"
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
    db_op('INSERT OR REPLACE INTO history VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    bot.send_message(message.chat.id, "Ethera на связи. Погнали?", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    text = message.text

    if text == "🤖 ИИ Ассистент":
        db_op('UPDATE history SET state="ai" WHERE chat_id=?', (chat_id,))
        bot.send_message(chat_id, "🦾 Режим ИИ активен. Присылай ситуацию или промт:")
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

    # РАБОТА С ИИ
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
        except:
            bot.reply_to(message, "Ошибка связи с ИИ.")
    else:
        bot.send_message(chat_id, "Выбери раздел в меню ниже:", reply_markup=main_keyboard())

if __name__ == '__main__':
    bot.infinity_polling()
