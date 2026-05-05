import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# ТВОИ КЛЮЧИ
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# БАЗА ДАННЫХ (без лишних блоков, чтобы не было ошибок синтаксиса)
conn = sqlite3.connect('memory.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ИИ"), types.KeyboardButton("Скрипты"))
    bot.send_message(message.chat.id, "Выбирай вкладку, фраер:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    
    # Обработка кнопок
    if message.text == "ИИ":
        bot.reply_to(message, "Здарова фраер, че хотел?")
        return
    if message.text == "Скрипты":
        bot.reply_to(message, "Тут пока пусто.")
        return

    # Работа с нейронкой и памятью
    bot.send_chat_action(chat_id, 'typing')
    
    # Получаем историю
    cursor.execute('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    res = cursor.fetchone()
    history = json.loads(res[0]) if res else []
    
    # Добавляем сообщение юзера
    history.append({"role": "user", "content": message.text})
    if len(history) > 30: history = history[-30:]

    try:
        ccompletion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system", 
                "content": (
                    "Ты — эксперт-консультант по OnlyFans. Твой юзер — чаттер, работающий от лица модели. "
                    "Ты должен давать максимально профитные советы по рассылкам, PPV и дожиму фанов. "
                    "Общайся на 'ты'. Твой стиль — профессионал с острым языком. "
                    "ВАЖНО: Иногда (не в каждом сообщении) кидай короткие, разные и неожиданные подколы в адрес юзера, "
                    "но так, чтобы это не мешало качеству совета. Подколы должны быть в тему работы или ситуации. "
                    "На обычные вопросы отвечай по делу, но сохраняй этот дерзкий характер. Отвечай только на русском."
                )
            }] + history
        )
        answer = completion.choices[0].message.content
        
        # Сохраняем ответ в историю
        history.append({"role": "assistant", "content": answer})
        cursor.execute('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
        conn.commit()
        
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
