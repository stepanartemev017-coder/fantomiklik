import telebot
import google.generativeai as genai

# ТВОИ ДАННЫЕ
TOKEN = '8749709641:AAH8AgA6cj6QPbl14jhjnncn9KVFSDuGOlw' # Тот, который сейчас работает
GOOGLE_AI_KEY = 'AIzaSyBfVeE2mbx6-P8ohLvpWM75AIOXA1X01DE'

# Настройка Gemini
genai.configure(api_key=GOOGLE_AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Теперь я работаю на бесплатной нейронке от Google. Спрашивай!")

@bot.message_handler(func=lambda message: True)
def chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "Я немного устал, попробуй через минуту.")

bot.infinity_polling()
