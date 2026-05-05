import telebot
from g4f.client import Client

bot = telebot.TeleBot('8749709641:AAEyio0vr4SNNBeGo8uyrdp7lqlG0q56Pfn8')
client = Client()

@bot.message_handler(func=lambda message: True)
def chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, "Ошибка: бесплатный доступ временно недоступен.")

bot.infinity_polling()
