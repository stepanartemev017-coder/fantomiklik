import telebot
import os

# Берем токен из настроек хостинга или вставляем вручную
TOKEN = '8749709641:AAEyi0vr4SNNBeGo8uyrdp7lq1GOq56Pfn8'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я работаю через GitHub на хостинге!")

print("Бот запущен...")
bot.infinity_polling()
