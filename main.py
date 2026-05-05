import telebot
from telebot import types
from groq import Groq

# ВСТАВЬ СВОИ КЛЮЧИ ТУТ (строго в кавычках!)
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo' 
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Выбирай вкладку, фраер:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Скрипты")
def scripts(message):
    bot.reply_to(message, "Тут пока пусто.")

@bot.message_handler(func=lambda message: message.text == "ИИ")
def ai_hi(message):
    bot.reply_to(message, "Здарова фраер, че хотел?")

@bot.message_handler(func=lambda message: True)
def chat(message):
    if message.text not in ["ИИ", "Скрипты"]:
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Ты дерзкий помощник. Отвечай на 'ты', с юмором. На русском."},
                    {"role": "user", "content": message.text}
                ]
            )
            # ВОТ ТУТ БЫЛА ОШИБКА, ТЕПЕРЬ ИСПРАВЛЕНО:
            answer = completion.choices[0].message.content
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Ошибка нейронки: {e}")

if __name__ == '__main__':
    bot.infinity_polling()
