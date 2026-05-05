import telebot
import g4f
from g4f.client import Client

# ВАЖНО: Токен ОБЯЗАТЕЛЬНО должен быть в кавычках
TOKEN = '8749709641:AAEyi0vr4SNNBeGo8uyrdp7lq1GOq56Pfn8'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бесплатная нейросеть. Напиши свой вопрос, и я отвечу!")

@bot.message_handler(func=lambda message: True)
def chat(message):
    # Показываем статус "печатает"
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
        )
        answer = response.choices.message.content
        bot.reply_to(message, answer)
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "Извини, бесплатный сервер сейчас перегружен. Попробуй еще раз через минуту.")

if __name__ == '__main__':
    print("Бот успешно запущен!")
    bot.infinity_polling()
