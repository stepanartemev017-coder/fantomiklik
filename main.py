import telebot
from groq import Groq
import json

# --- ТВОИ НОВЫЕ КЛЮЧИ ---
TOKEN = '8749709641:AAEzaq4hLh2S982vdEtwDksxgnBQFZVNPuc'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# Хранилище в памяти (работает на любом хостинге)
user_storage = {}

# --- ЖЕСТКИЕ НАСТРОЙКИ ИИ ---
SYSTEM_PROMPT = (
    "Ты — Ethera, профессиональный AI-ассистент чаттера на Fansly. "
    "ВАЖНО: Твой собеседник — это ЧАТТЕР (Админ), твой босс. "
    "ЗАПРЕЩЕНО флиртовать с пользователем или называть его 'милый'. Общайся с ним как профи-коллега. "
    "ТВОЯ ЗАДАЧА: помогать ему делать деньги, создавая лучший контент для фанов.\n\n"
    "ПРАВИЛА ДЛЯ ТЕКСТОВ ФАНАМ:\n"
    "1. Пиши СТРОГО НА 'ТЫ', обращаясь к одному мужчине лично.\n"
    "2. СТИЛЬ: Живой, женственный, кокетливый.\n"
    "3. СТРУКТУРА: Лайв-контекст + вовлекающий вопрос."
)

# --- БАЗА ЗНАКОМСТВА (100+ ВОПРОСОВ) ---
KNOWING_LIST = (
    "🤝 **СПИСОК ВОПРОСОВ ДЛЯ ЗНАКОМСТВА (Копируй нажатием)**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что на ужин было?` \n9. `Что сейчас слушаешь?` \n10. `Твой рост?` \n"
    "11. `Активный отдых или диван?` \n12. `Где мечтаешь побывать?` \n13. `Твой любимый фильм?` \n14. `Веришь в судьбу?` \n15. `Что тебя смешит?` \n"
    "16. `Риск или комфорт?` \n17. `Лучшее воспоминание?` \n18. `Что ценишь в людях?` \n19. `Куда позовешь на свидание?` \n20. `Ты романтик или реалист?` \n"
    "21. `Твоя любимая книга?` \n22. `Любишь экстрим?` \n23. `Любишь море или горы?` \n24. `Умеешь играть на чем-то?` \n25. `Веришь в интуицию?` \n"
    "26. `Твое хобби?` \n27. `О чем мечтаешь в тишине?` \n28. `Что во мне зацепило?` \n29. `Легко доверяешь людям?` \n30. `Хотел бы приехать?` \n"
    "31. `Веришь в химию через экран?` \n32. `О чем стесняешься спросить?` \n33. `Ты ревнивый?` \n34. `Твой главный страх?` \n35. `Что для тебя уют?` \n"
    "36. `Ты когда-нибудь влюблялся в сети?` \n37. `Что для тебя верность?` \n38. `Умеешь признавать ошибки?` \n39. `Что делает тебя счастливым?` \n40. `Любишь, когда тебя дразнят?` \n"
    "*(Нажми на вопрос, чтобы скопировать)*"
)

# --- 10 СЦЕНАРИЕВ СЕКСТИНГА ---
SEXTING_LIST = (
    "🔥 **10 СЦЕНАРИЕВ СЕКСТИНГА (ПРОГРЕВ)**\n\n"
    "1. **'СЛУЧАЙНЫЙ КАДР'**\n`Ой, пересматривала сейчас галерею и нашла одно фото... я тут такая настоящая. Показать?` \n*Дальше:* Жди 'да' и описывай свои чувства или наряд.\n\n"
    "2. **'ВЫБОР ОБРАЗА'**\n`Хочу сегодня вечером быть особенной для тебя... Поможешь выбрать белье под платье?` \n*Дальше:* Описывай два варианта и спрашивай, какой его заводит.\n\n"
    "3. **'ГОРЯЧИЙ СЕКРЕТ'**\n`Тссс... я сейчас в людном месте, но на мне нет белья. Это наше маленькое преступление.` \n*Дальше:* Расскажи, как тебе волнительно.\n\n"
    "4. **'ПОСЛЕ ДУША'**\n`Я только что из душа, и тут так прохладно... Хочется, чтобы кто-то теплый был рядом.` \n*Дальше:* Описывай капли воды на коже.\n\n"
    "5. **'СОН'**\n`Мне приснился очень яркий сон... и ты там был не совсем в одежде. 😊` \n*Дальше:* Рассказывай детали своего сна.\n\n"
    "6. **'ПРИКОСНОВЕНИЯ'**\n`Мои руки сегодня такие нежные... С чего мне начать касаться тебя?` \n\n"
    "7. **'БЛИЗОСТЬ'**\n`В комнате так тихо, я слышу только свое дыхание и мысли о тебе...` \n\n"
    "8. **'ИГРА'**\n`Давай сыграем? Ты говоришь свое желание, а я — как я его исполню.` \n\n"
    "9. **'НАКАЗАНИЕ'**\n`Я сегодня была вредной девочкой... Кажется, мне нужно наказание. Справишься?` \n\n"
    "10. **'ШЕПОТ'**\n`Приблизься к экрану... Я хочу прошептать тебе кое-что, от чего у тебя пойдут мурашки.`"
)

# --- 10 ПРОМТОВ ДЛЯ ИИ ---
PROMPTS_LIST = (
    "📝 **10 ПРОМТОВ ДЛЯ РАССЫЛОК**\n\n"
    "1. `Сделай 5 рассылок на тему 'Уютный вечер'. Пиши строго на ТЫ. Лайв-контекст + вопрос.`\n"
    "2. `Придумай 5 рассылок 'Я в магазине белья'. Игриво на ТЫ, создай интригу.`\n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'. Тон нежный, на ТЫ.`\n"
    "4. `Сделай рассылку-байтер: я начала рассказывать и 'отвлеклась'.`\n"
    "5. `Придумай рассылку про выбор фильма на вечер.`\n"
    "6. `Сделай 3 варианта рассылки про готовку ужина в одной футболке.`\n"
    "7. `Напиши рассылку 'Скучаю': нашла вещь, напомнившую о нем.`\n"
    "8. `Сделай рассылку про плохую погоду и желание согреться вдвоем.`\n"
    "9. `Напиши 3 дерзких рассылки для тех, кто долго не отвечал.`\n"
    "10. `Придумай рассылку 'Секрет': хочу поделиться тем, что знаю только я.`"
)

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    user_storage[message.chat.id] = {'history': [], 'state': 'main'}
    text = (
        "🦾 **Ethera V3: Профессиональный инструмент**\n\n"
        "/ai — Включить режим нейронки\n"
        "/know — Список вопросов для знакомства\n"
        "/sexting — Сценарии секстинга\n"
        "/prompts — 10 промтов для рассылок\n"
        "/clear — Очистить память ИИ\n"
        "/stop — Выключить нейронку"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['ai'])
def cmd_ai(message):
    if message.chat.id not in user_storage:
        user_storage[message.chat.id] = {'history': [], 'state': 'ai'}
    user_storage[message.chat.id]['state'] = 'ai'
    bot.send_message(message.chat.id, "🦾 **Режим ИИ включен.**\nЯ больше не буду флиртовать с тобой. Жду запросы по работе!")

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
    if message.chat.id in user_storage:
        user_storage[message.chat.id]['history'] = []
    bot.send_message(message.chat.id, "🧼 **Память очищена.**")

@bot.message_handler(commands=['stop'])
def cmd_stop(message):
    if message.chat.id in user_storage:
        user_storage[message.chat.id]['state'] = 'main'
    bot.send_message(message.chat.id, "🛑 **Режим ИИ выключен.**")

# --- ОБРАБОТКА ТЕКСТА ---

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    cid = message.chat.id
    if cid not in user_storage:
        user_storage[cid] = {'history': [], 'state': 'main'}

    if user_storage[cid]['state'] == 'ai':
        bot.send_chat_action(cid, 'typing')
        # Добавляем в историю пометку, что пишет Администратор
        user_storage[cid]['history'].append({"role": "user", "content": f"[ADMIN REQUEST]: {message.text}"})
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_storage[cid]['history'],
                temperature=0.7
            )
            # Извлекаем текст ответа
            answer = completion.choices[0].message.content
            
            user_storage[cid]['history'].append({"role": "assistant", "content": answer})
            # Ограничиваем историю
            if len(user_storage[cid]['history']) > 12:
                user_storage[cid]['history'] = user_storage[cid]['history'][-12:]
                
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Ошибка: {str(e)}")
    else:
        bot.send_message(cid, "Введи /ai, чтобы я начала помогать. 🦾")

if __name__ == '__main__':
    print("Ethera запущена...")
    bot.infinity_polling()
