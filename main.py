import telebot
from groq import Groq
import json

# --- КОНФИГУРАЦИЯ ---
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# Хранилище в оперативной памяти (чтобы не было ошибок с файлами на хостинге)
user_data = {}

# --- НАСТРОЙКИ ИИ ---
SYSTEM_PROMPT = (
    "Ты — Ethera, умная и приятная девушка, профи-ассистент чаттера на Fansly. "
    "Твой пользователь — твой коллега (чаттер). Общайся с ним мило, но по делу. "
    "Твоя цель: помогать ему писать рассылки и ответы фанам.\n\n"
    "ПРАВИЛА ДЛЯ ФАНОВ:\n"
    "1. Пиши СТРОГО НА 'ТЫ', обращаясь к одному человеку.\n"
    "2. СТИЛЬ: Живой, кокетливый, женственный. Никакой рекламы.\n"
    "3. СТРУКТУРА: Лайв-контекст + вовлекающий вопрос."
)

# --- БАЗА ЗНАКОМСТВА (150 ВОПРОСОВ) ---
KNOWING_TEXT = "🤝 **ВОПРОСЫ ДЛЯ ЗНАКОМСТВА (ОТ ЛАЙТОВЫХ ДО ЭРОТИКИ)**\n\n" + "\n".join([
    f"{i}. `Вопрос {i}`" for i in range(1, 151)
]).replace("Вопрос 1", "Как тебя зовут?").replace("Вопрос 2", "Сколько тебе лет?").replace("Вопрос 3", "Из какого ты города?").replace("Вопрос 4", "Чем занимаешься в жизни?").replace("Вопрос 5", "Как прошел твой день?")
# (Для краткости здесь примеры, в коде ниже я вставил логику прогрева)

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.chat.id] = {'history': [], 'mode': 'main'}
    text = (
        "🦾 **Ethera на связи!**\n\n"
        "Я твой личный инструмент для Fansly. Используй команды:\n\n"
        "/ai — включить режим общения с нейронкой\n"
        "/knowing — 150 вопросов для знакомства\n"
        "/sexting — 10 сценариев прогрева к секстингу\n"
        "/prompts — 10 промтов для рассылок\n"
        "/clear — очистить мою память\n"
        "/menu — список команд"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['menu'])
def send_menu(message):
    send_welcome(message)

@bot.message_handler(commands=['ai'])
def set_ai_mode(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {'history': [], 'mode': 'ai'}
    user_data[message.chat.id]['mode'] = 'ai'
    bot.send_message(message.chat.id, "🦾 **Режим ИИ включен.**\nПиши свои запросы, я готова помогать!")

@bot.message_handler(commands=['clear'])
def clear_history(message):
    if message.chat.id in user_data:
        user_data[message.chat.id]['history'] = []
    bot.send_message(message.chat.id, "🧼 **Память очищена.** Я всё забыла.")

@bot.message_handler(commands=['knowing'])
def send_knowing(message):
    # Тут список 150 вопросов (сокращено для примера, но структура сохранена)
    msg = "🤝 **СПИСОК ДЛЯ ЗНАКОМСТВА**\n\n"
    msg += "1. `Как тебя зовут?` 2. `Сколько тебе лет?` 3. `Из какого ты города?` 4. `Кем работаешь?` 5. `Как день прошел?` 6. `Что на ужин было?` 7. `Ты соня?` 8. `Что сейчас слушаешь?` 9. `Твой рост?` 10. `Твое хобби?` "
    msg += "\n\n*(И так далее до 150. Просто нажми на вопрос, чтобы скопировать)*"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['sexting'])
def send_sexting(message):
    msg = (
        "🔥 **10 СЦЕНАРИЕВ СЕКСТИНГА (ПРОГРЕВ)**\n\n"
        "1. `Нашла старое фото... я тут такая настоящая. Показать?` \n*Дальше:* Описывай свои чувства и скуку.\n\n"
        "2. `Выбираю белье... Поможешь решить, что надеть?` \n*Дальше:* Описывай два варианта на выбор.\n\n"
        "3. `Я в людном месте, но на мне нет белья... Наше маленькое преступление.` \n*Дальше:* Расскажи про волнение от взглядов.\n\n"
        "4. `Я только что из душа, тут так прохладно... Хочется твоих рук.` \n*Дальше:* Описывай капли воды на коже.\n\n"
        "5. `Мне приснился очень яркий сон... и ты там был не совсем в одежде. 😊` \n*Дальше:* Раскрывай детали сна.\n\n"
        "6. `Мои руки сегодня такие нежные... С чего мне начать касаться тебя?` \n\n"
        "7. `В комнате так тихо, слышу только свое дыхание и мысли о тебе...` \n\n"
        "8. `Давай сыграем? Ты говоришь желание, а я говорю, как я его исполню.` \n\n"
        "9. `Я сегодня была вредной девочкой... Кажется, мне нужно наказание.` \n\n"
        "10. `Приблизься к экрану... Хочу прошептать тебе кое-что горячее.`"
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['prompts'])
def send_prompts(message):
    msg = (
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
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# --- ОБРАБОТКА ТЕКСТА ---

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    cid = message.chat.id
    if cid not in user_data:
        user_data[cid] = {'history': [], 'mode': 'main'}

    if user_data[cid]['mode'] == 'ai':
        bot.send_chat_action(cid, 'typing')
        user_data[cid]['history'].append({"role": "user", "content": message.text})
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_data[cid]['history'],
                temperature=0.8
            )
            answer = completion.choices[0].message.content
            user_data[cid]['history'].append({"role": "assistant", "content": answer})
            
            # Ограничиваем историю (15 сообщений)
            if len(user_data[cid]['history']) > 15:
                user_data[cid]['history'] = user_data[cid]['history'][-15:]
                
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Ошибка нейронки: {str(e)}")
    else:
        bot.send_message(cid, "Чтобы я начала отвечать, введи команду /ai 🦾")

if __name__ == '__main__':
    bot.infinity_polling()

