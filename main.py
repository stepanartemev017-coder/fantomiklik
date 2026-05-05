import telebot
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

# --- НАСТРОЙКИ ИИ (ПРОМПТ) ---
SYSTEM_PROMPT = (
    "Ты — Ethera, профессиональный AI-ассистент чаттера на Fansly. "
    "Твой пользователь — чаттер, общайся с ним мило и по делу. "
    "Твоя цель: помогать ему генерировать крутой контент для фанов.\n\n"
    "ПРАВИЛА ГЕНЕРАЦИИ ДЛЯ ФАНОВ:\n"
    "1. Пиши СТРОГО НА 'ТЫ', обращаясь к ОДНОМУ человеку лично.\n"
    "2. СТИЛЬ: Живой, женственный, кокетливый. Без рекламы.\n"
    "3. СТРУКТУРА: Текущий контекст модели + вовлекающий вопрос."
)

# --- БАЗЫ ДАННЫХ (ТЕКСТЫ) ---

KNOWING_LIST = (
    "🤝 **ВОПРОСЫ ДЛЯ ЗНАКОМСТВА (НУМЕРОВАННЫЕ)**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что на ужин было?` \n9. `Что сейчас слушаешь?` \n10. `Твой рост?` \n"
    "11. `Активный отдых или диван?` \n12. `Где мечтаешь побывать?` \n13. `Твой любимый фильм?` \n14. `Веришь в судьбу?` \n15. `Что тебя смешит?` \n"
    "16. `Риск или комфорт?` \n17. `Лучшее воспоминание?` \n18. `Что ценишь в людях?` \n19. `Куда позовешь на свидание?` \n20. `Ты романтик или реалист?` \n"
    "21. `Твоя любимая книга?` \n22. `Любишь экстрим?` \n23. `Любишь море или горы?` \n24. `Умеешь играть на чем-то?` \n25. `Веришь в интуицию?` \n"
    "26. `Твое хобби?` \n27. `О чем мечтаешь в тишине?` \n28. `Что во мне зацепило?` \n29. `Легко доверяешь людям?` \n30. `Хотел бы приехать?` \n"
    "*(Просто нажми на вопрос, чтобы скопировать)*"
)

SEXTING_LIST = (
    "🔥 **10 СЦЕНАРИЕВ СЕКСТИНГА**\n\n"
    "1. `Нашла старое фото... я тут такая настоящая. Показать?` \n*Дальше:* Описывай свои чувства и скуку.\n\n"
    "2. `Выбираю белье... Поможешь решить, что надеть?` \n*Дальше:* Описывай два варианта на его вкус.\n\n"
    "3. `Я в людном месте, но на мне нет белья... Наше маленькое преступление.` \n*Дальше:* Расскажи про волнение от взглядов.\n\n"
    "4. `Я только что из душа, и тут так прохладно... Хочется твоих рук.` \n*Дальше:* Описывай капли воды на коже.\n\n"
    "5. `Мне приснился очень яркий сон... и ты там был не совсем в одежде. 😊` \n*Дальше:* Раскрывай детали сна.\n\n"
    "6. `Мои руки сегодня такие нежные... С чего мне начать касаться тебя?` \n\n"
    "7. `В комнате так тихо, слышу только свое дыхание и мысли о тебе...` \n\n"
    "8. `Давай сыграем? Ты говоришь желание, а я — как я его исполню.` \n\n"
    "9. `Я сегодня была вредной девочкой... Кажется, мне нужно наказание.` \n\n"
    "10. `Приблизься к экрану... Хочу прошептать тебе кое-что горячее.`"
)

PROMPTS_LIST = (
    "📝 **10 ПРОМТОВ ДЛЯ ИИ**\n\n"
    "1. `Сделай 5 рассылок на тему 'Уютный вечер'. Пиши строго на ТЫ.`\n"
    "2. `Придумай 5 рассылок 'Я в магазине белья'. Игриво на ТЫ.`\n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'.`\n"
    "4. `Сделай рассылку-байтер: я начала рассказывать и 'отвлеклась'.`\n"
    "5. `Придумай рассылку про выбор фильма на вечер.`\n"
    "6. `Сделай 3 варианта рассылки про готовку ужина в одной футболке.`\n"
    "7. `Напиши рассылку 'Скучаю': нашла вещь, напомнившую о нем.`\n"
    "8. `Сделай рассылку про плохую погоду и желание согреться.`\n"
    "9. `Напиши 3 дерзких рассылки для тех, кто долго не отвечал.`\n"
    "10. `Придумай рассылку 'Секрет': хочу поделиться личным.`"
)

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    db_op('INSERT OR REPLACE INTO history VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    help_msg = (
        "🦾 **Ethera готова к работе!**\n\n"
        "Команды управления:\n"
        "/ai — Включить режим ИИ (я начну отвечать)\n"
        "/know — Список вопросов для знакомства\n"
        "/sexting — Сценарии секстинга и прогрева\n"
        "/prompts — 10 промтов для создания рассылок\n"
        "/clear — Очистить память ИИ (начать с чистого листа)\n"
        "/menu — Список всех команд"
    )
    bot.send_message(message.chat.id, help_msg, parse_mode="Markdown")

@bot.message_handler(commands=['ai'])
def cmd_ai(message):
    db_op('UPDATE history SET state="ai" WHERE chat_id=?', (message.chat.id,))
    bot.send_message(message.chat.id, "🦾 **Режим ИИ активирован.**\nТеперь просто пиши свои ситуации или вопросы, и я помогу!")

@bot.message_handler(commands=['know'])
def cmd_know(message):
    bot.send_message(message.chat.id, KNOWING_LIST, parse_mode="Markdown")

@bot.message_handler(commands=['sexting'])
def cmd_sexting(message):
    bot.send_message(message.chat.id, SEXTING_LIST, parse_mode="Markdown")

@bot.message_handler(commands=['prompts'])
def cmd_prompts(message):
    bot.send_message(message.chat.id, PROMPTS_LIST, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def cmd_clear(message):
    db_op('UPDATE history SET messages="[]" WHERE chat_id=?', (message.chat.id,))
    bot.send_message(message.chat.id, "🧼 **Память очищена.** Я всё забыла и готова к новому диалогу.")

# --- ОБРАБОТЧИК ТЕКСТА ---

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    res = db_op('SELECT messages, state FROM history WHERE chat_id=?', (chat_id,))
    
    if not res:
        cmd_start(message)
        return

    history_json, state = res

    if state == "ai":
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
            db_op('UPDATE history SET messages=? WHERE chat_id=?', (json.dumps(history[-15:]), chat_id))
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Ошибка нейронки: {str(e)}")
    else:
        bot.send_message(chat_id, "Чтобы я начала помогать, введи команду /ai 🦾")

if __name__ == '__main__':
    print("Ethera запущена на командах...")
    bot.infinity_polling()
