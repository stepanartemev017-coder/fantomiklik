import telebot
from telebot import types # Нужна для создания кнопок
from groq import Groq

# ДАННЫЕ
TOKEN = '8749709641:AHH8AgA6cj6QPb114jhjnncn9KVFSduGO1w'
GROQ_KEY = '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'

client = Groq(api_key=GROQ_KEY)
bot = telebot.TeleBot(TOKEN)

import telebot
from telebot import types
from groq import Groq

# ДАННЫЕ
TOKEN = '8749709641:AHH8AgA6cj6QPb114jhjnncn9KVFSduGO1w'
GROQ_KEY = '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'

client = Groq(api_key=GROQ_KEY)
bot = telebot.TeleBot(TOKEN)

# 1. Приветствие и кнопка
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("ИИ")
    markup.add(btn)
    bot.send_message(message.chat.id, "Кнопка внизу, нажимай и погнали.", reply_markup=markup)

# 2. Обработка кнопки "ИИ"
@bot.message_handler(func=lambda message: message.text == "ИИ")
def ai_welcome(message):
    bot.reply_to(message, "Здарова фраер, че хотел?")

# 3. Чат с умной, но шутливой нейронкой
@bot.message_handler(func=lambda message: True)
def chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Ты — высокоинтеллектуальный помощник с отличным чувством юмора. "
                        "Твоя задача: отвечать на вопросы ВСЕГДА ТОЧНО, ПРАВИЛЬНО и ПО ДЕЛУ. "
                        "Но при этом общайся на 'ты', веди себя как старый знакомый и иногда вкидывай острые шутки или подколы. "
                        "Не будь занудой, но и не превращай ответ в бессмыслицу. Отвечай только на русском."
                    )
                },
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, completion.choices.message.content)
    except Exception as e:
        bot.reply_to(message, f"Блин, мозг залагал. Ошибка: {str(e)}")

bot.infinity_polling()
