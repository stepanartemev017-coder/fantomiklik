import telebot
import requests

# --- ТВОИ ДАННЫЕ ---
TOKEN = '8749709641:AAEyio0vr4SNNBeGo8uyrdp7lqlG0q56Pfn8'
AI_KEY = 'sk-f84ab856270742b8865066c608453d5e' 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я работаю на стабильном API DeepSeek. Спрашивай!")

@bot.message_handler(func=lambda message: True)
def chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты дружелюбный ассистент."},
            {"role": "user", "content": message.text}
        ],
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_KEY}"
    }

    try:
        response = requests.post("https://deepseek.com", json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            bot_text = response.json()['choices']['message']['content']
            bot.reply_to(message, bot_text)
        else:
            bot.reply_to(message, f"Ошибка API: {response.status_code}. Проверь баланс в личном кабинете DeepSeek.")
    except Exception as e:
        bot.reply_to(message, "Ошибка связи с сервером нейросети.")

bot.infinity_polling()
