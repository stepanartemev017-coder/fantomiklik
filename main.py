import telebot
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

# --- НАСТРОЙКИ ИИ ---
SYSTEM_PROMPT = (
    "Ты — Ethera, профессиональный AI-ассистент чаттера на Fansly. "
    "Твой босс — чаттер, общайся с ним мило и по делу. "
    "ПРАВИЛО ДЛЯ ФАНОВ: Пиши СТРОГО НА 'ТЫ', обращаясь к одному человеку. "
    "Структура: Контекст + Игривый вопрос."
)

# --- ТЕКСТОВЫЕ БАЗЫ ---
KNOWING_LIST = (
    "🤝 **ЗНАКОМСТВО (Нажми на вопрос, чтобы скопировать)**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Как твой день прошел?` \n"
    "6. `Ты сейчас отдыхаешь?` \n7. `Что сейчас слушаешь?` \n8. `Твой рост?` \n9. `Веришь в судьбу?` \n10. `Что во мне зацепило?` \n"
    "11. `Веришь в химию через экран?` \n12. `О чем стесняешься спросить?` \n13. `Любишь, когда тебя дразнят?` \n14. `Какая часть моего тела манит?` \n15. `Умеешь делать массаж?` \n"
    "16. `Твоя смелая фантазия?` \n17. `Доминировать или подчиняться?` \n18. `Что заводит мгновенно?` \n19. `Как относишься к ролевым?` \n20. `Твое главное желание на ночь?`"
)

SEXTING_LIST = (
    "🔥 **10 СЦЕНАРИЕВ СЕКСТИНГА**\n\n"
    "1. `Нашла старое фото... я тут такая настоящая. Показать?` (Описывай наряд)\n"
    "2. `Выбираю белье... Поможешь решить, что надеть?` (Описывай варианты)\n"
    "3. `Тссс... я сейчас в людном месте, но на мне нет белья.` (Описывай волнение)\n"
    "4. `Я только что из душа, тут так прохладно... Хочется тепла.` (Описывай капли воды)\n"
    "5. `Мне приснился очень яркий сон... и ты там был не совсем в одежде. 😊` (Раскрывай детали)\n"
    "6. `Мои руки сегодня такие нежные... С чего мне начать касаться тебя?` \n"
    "7. `В комнате так тихо, слышу только мысли о тебе...` \n"
    "8. `Давай сыграем? Ты говоришь желание, а я — как я его исполню.` \n"
    "9. `Я сегодня была вредной девочкой... Нуждаюсь в наказании.` \n"
    "10. `Приблизься... Хочу прошептать тебе кое-что горячее.`"
)

PROMPTS_LIST = (
    "📝 **10 ПРОМТОВ ДЛЯ ИИ**\n\n"
    "1. `Сделай 5 рассылок на тему 'Уютный вечер'. Пиши на ТЫ.`\n"
    "2. `Придумай 5 рассылок 'В магазине белья'. Игриво на ТЫ.`\n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'.`\n"
    "4. `Сделай рассылку-байтер: я начала что-то рассказывать и 'отвлеклась'.`\n"
    "5. `Придумай рассылку про выбор фильма на вечер.`\n"
    "6. `Сделай 3 варианта рассылки про готовку ужина в одной футболке.`\n"
    "7. `Напиши рассылку 'Скучаю': нашла вещь, напомнившую о нем.`\n"
    "8. `Сделай рассылку про плохую погоду и желание согреться.`\n"
    "9. `Напиши 3 дерзких рассылки для тех, кто давно не отвечал.`\n"
    "10. `Придумай рассылку 'Секрет': хочу поделиться личным.`"
)

# --- ОБРАБОТЧИКИ КОМАНД ---
@bot.message_handler(commands=['start'])
def cmd_start(message):
    db_op('INSERT OR REPLACE INTO history VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    help_text = (
        "Ethera на связи. 🦾\n\n"
        "Команды управления:\n"
        "/ai — включить режим нейронки\n"
        "/know — вопросы для знакомства\n"
        "/sexting — сценарии секстинга\n"
        "/prompts — промты для рассылок\n"
        "/clear — очистить память ИИ\n"
        "/menu — список команд"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['ai'])
def cmd_ai(message):
    db_op('UPDATE history SET state="ai" WHERE chat_id=?', (message.chat.id,))
    bot.send_message(message.chat.id, "🦾 Режим ИИ включен. Теперь я отвечаю на твои сообщения как ассистент.")

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
    bot.send_message(message.chat.id, "🧼 Память очищена. Я всё забыла.")

@bot.message_handler(commands=['menu'])
def cmd_menu(message):
    cmd_start(message)

# --- ГЛАВНЫЙ ОБРАБОТЧИК ТЕКСТА ---
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
        history = json.loads(history_json)
        history.append({"role": "user", "content": message.text})
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                temperature=0.8
            )
            # Фикс: берем контент из первого варианта ответа
            answer = completion.choices[0].message.content
            
            history.append({"role": "assistant", "content": answer})
            # Сохраняем последние 15 сообщений для контекста
            db_op('UPDATE history SET messages=? WHERE chat_id=?', (json.dumps(history[-15:]), chat_id))
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Ошибка нейронки: {str(e)}")
    else:
        bot.send_message(chat_id, "Сейчас режим ИИ выключен. Введи /ai, чтобы начать общаться.")

if __name__ == '__main__':
    print("Бот запущен на командах...")
    bot.infinity_polling()

