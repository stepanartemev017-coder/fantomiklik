import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- КЛЮЧИ ---
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

# --- СПИСОК ПРОМТОВ ---
PROMPTS = {
    "1": "Сделай 5 рассылок на тему 'Красота в мелочах'. Варианты: 1. Новые свечи. 2. Свежее белье. 3. Любимые чулки. 4. Какао у окна. 5. Лайв-фейл. Стиль: уютный, мягкий, с легким флиртом.",
    "2": "Придумай 5 рассылок на тему 'Помоги мне определиться'. Ситуации: 1. Цвет лака. 2. Кино на вечер. 3. Выбор музыки. 4. Суши или пицца. 5. Лайв: выбор платья. Задача: заставить фана дать совет.",
    "3": "Накидай 5 рассылок на тему 'За кадром'. Варианты: 1. Беспорядок при сборах. 2. Усталость после съемок. 3. Поиск идей. 4. Старые фото. 5. Лайв: разрядилась камера. Тон: активный, вовлекающий.",
    "4": "Сделай 5 утренних рассылок 'Первые мысли'. Варианты: 1. Только открыла глаза. 2. Под одеялом. 3. Первый кофе. 4. Странный сон. 5. Лайв: сонная и лохматая. Стиль: сонный, милый, нежный.",
    "5": "Придумай 5 рассылок на тему 'Вечер только для нас'. Ситуации: 1. Бокал вина. 2. Благовония и полумрак. 3. Виниловая пластинка. 4. Ванна с пеной. 5. Лайв: чокаюсь с аватаркой. Стиль: расслабленный, интимный.",
    "6": "Сделай 5 рассылок на тему 'В движении'. Варианты: 1. Растяжка. 2. Йога. 3. Душ после зала. 4. Новый спортивный топ. 5. Лайв: кошка мешает планке. Стиль: бодрый, с намеком на формы.",
    "7": "Накидай 5 рассылок на тему 'Я сегодня гуляю'. Варианты: 1. Парк и птицы. 2. ТЦ и соблазны. 3. Замерзла на ветру. 4. Вещь напомнила о тебе. 5. Лайв: красивый закат. Тон: живой, естественный.",
    "8": "Придумай 5 рассылок на тему 'Только между нами'. Ситуации: 1. Безумная идея. 2. Секретный подарок. 3. Старый дневник. 4. Игривое настроение. 5. Лайв: делаю то, что нельзя. Стиль: интригующий.",
    "9": "Сделай 5 рассылок на тему 'Ой, всё...'. Варианты: 1. Провал на кухне. 2. Потеряла ключи. 3. Разбила кружку. 4. Разные носки. 5. Лайв: чихнула при съемке. Стиль: самоироничный, милый.",
    "10": "Накидай 5 рассылок на тему 'Минутка раздумий'. Варианты: 1. Давно не болтали. 2. Вспомнила первую встречу. 3. Хочу к морю. 4. Гадаю, какой ты в жизни. 5. Лайв: просто рада тебе. Стиль: теплый."
}

# --- МЕНЮ ---
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="open_ai"),
        types.InlineKeyboardButton("📝 Промты ИИ для рассылок", callback_data="open_prompts"),
        types.InlineKeyboardButton("📜 Скрипты (пусто)", callback_data="open_scripts")
    )
    return markup

def prompts_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"Тема {i}", callback_data=f"get_p_{i}") for i in range(1, 11)]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="open_main"))
    return markup

def back_to_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="open_main"))
    return markup

# --- ОБРАБОТКА КОМАНД ---
@bot.message_handler(commands=['start', 'menu'])
def cmd_menu(message):
    db_op('INSERT OR REPLACE INTO history (chat_id, messages, state) VALUES (?, ?, ?)', 
          (message.chat.id, json.dumps([]), "main"))
    bot.send_message(message.chat.id, "Главное меню. Выберите раздел:", reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "open_ai":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("ai_chat", call.message.chat.id))
        bot.edit_message_text("Режим ИИ. Присылай описание ситуации, а я сделаю варианты рассылок:", 
                              call.message.chat.id, call.message.message_id, reply_markup=back_to_menu_markup())
    
    elif call.data == "open_prompts":
        bot.edit_message_text("Выберите тему промта. При нажатии текст будет отправлен в чат для копирования:", 
                              call.message.chat.id, call.message.message_id, reply_markup=prompts_menu_markup())
    
    elif call.data.startswith("get_p_"):
        p_id = call.data.replace("get_p_", "")
        text = PROMPTS.get(p_id)
        # Отправляем сообщение с моноширинным шрифтом для копирования в один клик
        bot.send_message(call.message.chat.id, f"Копируй и отправляй ИИ:\n\n`{text}`", parse_mode="Markdown")

    elif call.data == "open_main":
        db_op('UPDATE history SET state = ? WHERE chat_id = ?', ("main", call.message.chat.id))
        bot.edit_message_text("Главное меню. Выберите раздел:", 
                              call.message.chat.id, call.message.message_id, reply_markup=main_menu_markup())

# --- ЛОГИКА ИИ ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    res = db_op('SELECT messages, state FROM history WHERE chat_id = ?', (chat_id,))
    if not res or res[1] != "ai_chat":
        bot.reply_to(message, "Чтобы общаться с ИИ, перейдите в раздел '🤖 ИИ Ассистент'.", reply_markup=main_menu_markup())
        return

    bot.send_chat_action(chat_id, 'typing')
    history = json.loads(res[0])
    history.append({"role": "user", "content": message.text})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты — приятная девушка-ассистент чаттера. Помогай с рассылками мило и профессионально."}] + history,
            temperature=0.8
        )
        answer = completion.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        db_op('UPDATE history SET messages = ? WHERE chat_id = ?', (json.dumps(history[-15:]), chat_id))
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка, попробуй позже.")

if __name__ == '__main__':
    bot.infinity_polling()
