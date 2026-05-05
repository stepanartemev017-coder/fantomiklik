import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- КОНФИГУРАЦИЯ ---
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# --- БАЗА ДАННЫХ ---
def db_op(query, params=()):
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    res = cursor.fetchone()
    conn.commit()
    conn.close()
    return res

conn = sqlite3.connect('memory.db')
conn.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT, state TEXT)')
conn.close()

# --- ЛИЧНОСТЬ ИИ ---
SYSTEM_PROMPT = (
    "Ты — Ethera, профессиональный ассистент чаттера на Fansly. "
    "Пользователь — твой босс. Общайся с ним мило и по делу. "
    "ПРАВИЛО ДЛЯ ТЕКСТОВ ФАНАМ: Пиши СТРОГО НА 'ТЫ', обращаясь к одному человеку лично. "
    "Используй структуру: Лайв-контекст -> Игривый вопрос."
)

# --- ДАННЫЕ РАЗДЕЛОВ ---
KNOWING_LIST = (
    "🤝 **СПИСОК ВОПРОСОВ ДЛЯ ЗНАКОМСТВА**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что сейчас слушаешь?` \n9. `Твой рост?` \n10. `Веришь в судьбу?` \n"
    "11. `Что во мне зацепило?` \n12. `Веришь в химию через экран?` \n13. `Какая часть моего тела манит?` \n14. `Умеешь делать массаж?` \n15. `Твоя смелая фантазия?` \n"
    "*(Для копирования просто нажми на вопрос)*"
)

SEXTING_LIST = (
    "🔥 **СЦЕНАРИИ СЕКСТИНГА**\n\n"
    "1. `Нашла старое фото... я тут такая настоящая. Показать?` \n"
    "2. `Выбираю белье... Поможешь решить, что надеть?` \n"
    "3. `Тссс... я сейчас в людном месте, но на мне нет белья.` \n"
    "4. `Я только что из душа, и тут так прохладно...` \n"
    "5. `Мне приснился очень яркий сон... и ты там был голышом. 😊`"
)

PROMPTS_LIST = (
    "📝 **ПРОМТЫ ДЛЯ ИИ**\n\n"
    "1. `Сделай 5 рассылок на тему 'Уютный вечер'. Пиши на ТЫ.`\n"
    "2. `Придумай 5 рассылок 'Я в магазине белья'. Игриво на ТЫ.`\n"
    "3. `Накидай 5 утренних рассылок 'Только проснулась'.`"
)

# --- КЛАВИАТУРА МЕНЮ ---
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🤖 ИИ Ассистент"),
        types.KeyboardButton("🤝 Знакомство"),
        types.KeyboardButton("🔥 Секстинг"),
        types.KeyboardButton("📝 Промты ИИ")
    )
    return markup

# --- ОБРАБОТЧИКИ КОМАНД ---
@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    db_op('INSERT OR REPLACE INTO history VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    bot.send_message(message.chat.id, "Ethera на связи. Инструменты в клавиатуре ниже:", reply_markup=main_keyboard())

# --- ГЛАВНЫЙ ОБРАБОТЧИК ТЕКСТА ---
@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    text = message.text

    # Обработка нажатий кнопок клавиатуры
    if text == "🤖 ИИ Ассистент":
        db_op('UPDATE history SET state="ai" WHERE chat_id=?', (chat_id,))
        bot.send_message(chat_id, "🦾 Режим ИИ активен. Отправь ситуацию или промт, и я помогу с текстом.")
        return

    elif text == "🤝 Знакомство":
        bot.send_message(chat_id, KNOWING_LIST, parse_mode="Markdown")
        return

    elif text == "🔥 Секстинг":
        bot.send_message(chat_id, SEXTING_LIST, parse_mode="Markdown")
        return

    elif text == "📝 Промты ИИ":
        bot.send_message(chat_id, PROMPTS_LIST, parse_mode="Markdown")
        return

    # Логика работы с ИИ
    res = db_op('SELECT messages, state FROM history WHERE chat_id=?', (chat_id,))
    if res and res[1] == "ai":
        bot.send_chat_action(chat_id, 'typing')
        history = json.loads(res[0])
        history.append({"role": "user", "content": text})
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                temperature=0.8
            )
            answer = completion.choices[0].message.content
            history.append({"role": "assistant", "content": answer})
            db_op('UPDATE history SET messages=? WHERE chat_id=?', (json.dumps(history[-15:]), chat_id))
            bot.reply_to(message, answer)
        except:
            bot.reply_to(message, "Ошибка связи с ИИ. Попробуй позже.")
    else:
        bot.reply_to(message, "Выбери нужный раздел в меню клавиатуры.", reply_markup=main_keyboard())

if __name__ == '__main__':
    bot.infinity_polling()
