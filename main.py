import telebot
from groq import Groq

# ДАННЫЕ
TOKEN = '8749709641:AAH8AgA6cj6QPbl14jhjnncn9KVFSDuGOlw'
GROQ_KEY = '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'

client = Groq(api_key=GROQ_KEY)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile" ,
            messages=[{"role": "user", "content": message.text}]
        )
        bot.reply_to(message, completion.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

bot.infinity_polling()
