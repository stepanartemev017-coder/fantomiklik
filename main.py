import telebot
from telebot import types
from groq import Groq

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8749709641:AAEzaq4hLh2S982vdEtwDksxgnBQFZVNPuc"
AI_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

user_storage = {}

# --- ПРОФЕССИОНАЛЬНЫЙ ПРОМПТ: ЭКСПЕРТ ПО FANSLY ---
SYSTEM_PROMPT = """
Ты — ведущий эксперт и консультант для чаттеров на платформе Fansly. 
Твоя цель: помогать пользователю (чаттеру) максимально эффективно вести диалоги и увеличивать продажи.

ТВОИ ЗНАНИЯ:
- Механики Fansly: PPV (платные сообщения), рассылки, кастомные запросы, уровни подписки, чаевые.
- Психология фанатов: как работать с "китами", как дожимать жадных пользователей, как переводить диалог в интимное русло.
- Скрипты: создание естественных, вовлекающих текстов, которые не выглядят как спам.

ПРАВИЛА ОТВЕТА:
1. Общайся профессионально, конкретно и по делу. 
2. Никакой лишней ролевой игры "подружки" — ты инструмент для заработка денег.
3. Если пользователь просит текст для рассылки, давай несколько вариантов (от мягкого до агрессивного).
4. Твои советы должны быть направлены на удержание фаната и максимизацию прибыли.
"""

# --- БАЗЫ ДАННЫХ (ДЛЯ БЫСТРОГО КОПИРОВАНИЯ) ---
KNOWING_LIST = [
    "Как тебя зовут, симпатяга?", "Откуда ты родом?", "Сколько тебе лет?", "Кем работаешь?", 
    "Как твой день прошел?", "Ты сейчас отдыхаешь или еще в делах?", "Что на ужин было вкусного?", 
    "Ты сова или жаворонок?", "Твой рост?", "Какую музыку слушаешь?", "Есть питомцы?", 
    "Твое любимое хобби?", "Ты активный или любишь полениться?", "Где мечтаешь побывать?"
]

SEXTING_LIST = [
    "Случайно вспомнила то наше сообщение... кажется, я покраснела...",
    "Лежу, выбираю белье на вечер и подумала: а какое бы понравилось тебе?",
    "Тссс... я сейчас в людном месте, но на мне нет белья. Это наш секрет...",
    "Только из душа, кожа такая горячая, а в комнате прохладно... хочется тепла...",
    "Мне приснился очень яркий сон... и ты там был главным героем..."
]

ALL_PROMPTS_LIST = [
    "Сделай 5 рассылок: покупка нового белья, нужно мнение фаната.",
    "Придумай 5 сообщений для 'дожима' тех, кто молчит после цены.",
    "Напиши сценарий для короткого секстинга: начало, развитие, финал.",
    "5 идей для постов в ленту, которые спровоцируют фанатов написать в ЛС."
]

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💎 Вопросы: Знакомство"),
        types.KeyboardButton("🔞 Опенеры: Секстинг"),
        types.KeyboardButton("📈 Промты для продаж"),
        types.KeyboardButton("🧹 Очистить историю")
    )
    return markup

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    user_storage[message.chat.id] = {'history': []}
    bot.send_message(
        message.chat.id, 
        "<b>Эксперт по Fansly запущен.</b>\nЯ готов генерировать скрипты, сценарии и стратегии для продаж. Что нужно сделать?", 
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    cid = message.chat.id
    text = message.text

    if cid not in user_storage:
        user_storage[cid] = {'history': []}

    # Быстрые списки
    if "Знакомство" in text:
        res = "<b>База вопросов (копируй тапом):</b>\n\n"
        for q in KNOWING_LIST: res += f"<code>{q}</code>\n"
        bot.send_message(cid, res, parse_mode="HTML")
        return
    elif "Секстинг" in text:
        res = "<b>База опенеров (копируй тапом):</b>\n\n"
        for q in SEXTING_LIST: res += f"<code>{q}</code>\n"
        bot.send_message(cid, res, parse_mode="HTML")
        return
    elif "Промты" in text:
        res = "<b>Идеи для задач ИИ (копируй тапом):</b>\n\n"
        for q in ALL_PROMPTS_LIST: res += f"<code>{q}</code>\n"
        bot.send_message(cid, res, parse_mode="HTML")
        return
    elif "Очистить" in text:
        user_storage[cid]['history'] = []
        bot.send_message(cid, "Контекст диалога очищен.")
        return

    # Логика AI (Groq)
    bot.send_chat_action(cid, 'typing')
    user_storage[cid]['history'].append({"role": "user", "content": text})
    
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_storage[cid]['history']
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7
        )

        answer = completion.choices[0].message.content
        user_storage[cid]['history'].append({"role": "assistant", "content": answer})
        
        # Обрезка истории (храним последние 10 сообщений)
        if len(user_storage[cid]['history']) > 10:
            user_storage[cid]['history'] = user_storage[cid]['history'][-10:]

        bot.reply_to(message, answer)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка API: {str(e)}\nПопробуй включить VPN на сервере.")

if __name__ == "__main__":
    print("Бот-эксперт запущен!")
    bot.infinity_polling()
