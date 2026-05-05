import telebot
from telebot import types
from groq import Groq

# ВСТАВЬ СВОИ КЛЮЧИ ТУТ (строго в кавычках!)
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo' 
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# ГЛАВНОЕ МЕНЮ
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Выбирай вкладку, фраер:", reply_markup=markup)

# ВКЛАДКА СКРИПТЫ
@bot.message_handler(func=lambda message: message.text == "Скрипты")
def scripts(message):
    bot.reply_to(message, "Тут пока пусто.")

# ПРИВЕТСТВИЕ ПРИ НАЖАТИИ НА ИИ
@bot.message_handler(func=lambda message: message.text == "ИИ")
def ai_hi(message):
    bot.reply_to(message, "Здарова фраер, че хотел?")

# ОСНОВНОЙ ЧАТ
@bot.message_handler(func=lambda message: True)
def chat(message):
    # Пропускаем, если нажаты кнопки меню
    if message.text in ["ИИ", "Скрипты"]:
        return

    bot.send_chat_action(message.chat.id, 'typing')
    try:
        # ЗАПРОС К НЕЙРОНКЕ
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты умный и дерзкий помощник. Отвечай на 'ты', с юмором. На русском языке."},
                {"role": "user", "content": message.text}
            ]
        )
        # ИСПРАВЛЕННЫЙ СПОСОБ ПОЛУЧЕНИЯ ОТВЕТА:
        answer = completion.choices[0].message.content
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка нейронки: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
