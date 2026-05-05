import telebot
from telebot import types
from groq import Groq

# ВСТАВЬ СВОИ КЛЮЧИ ТУТ (строго в кавычках!)
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo' 
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# 1. ГЛАВНОЕ МЕНЮ (кнопки ИИ и Скрипты)
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_ai = types.KeyboardButton("ИИ")
    btn_scripts = types.KeyboardButton("Скрипты")
    markup.add(btn_ai, btn_scripts)
    bot.send_message(message.chat.id, "Выбирай вкладку, фраер:", reply_markup=markup)

# 2. ВКЛАДКА "СКРИПТЫ" (пустая)
@bot.message_handler(func=lambda message: message.text == "Скрипты")
def scripts_tab(message):
    bot.reply_to(message, "Тут пока пусто, заходи позже.")

# 3. ВКЛАДКА "ИИ" (приветствие)
@bot.message_handler(func=lambda message: message.text == "ИИ")
def ai_welcome(message):
    bot.reply_to(message, "Здарова фраер, че хотел?")

# 4. ОБЩЕНИЕ С НЕЙРОНКОЙ
@bot.message_handler(func=lambda message: True)
def chat(message):
    # Если пользователь просто пишет текст (не нажимая на кнопки)
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты умный и дерзкий помощник. Отвечай на 'ты', с юмором. На русском."},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, completion.choices.message.content)
    except Exception as e:
        bot.reply_to(message, f"Ошибка нейронки: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
