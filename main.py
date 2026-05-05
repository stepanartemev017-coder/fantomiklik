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
    "ПРАВИЛО ДЛЯ ТЕКСТОВ ФАНАМ: Пиши СТРОГО НА 'ТЫ', обращаясь к одному конкретному человеку. "
    "Используй структуру: Лайв-контекст -> Игривый вопрос."
)

# --- СПИСОК ВОПРОСОВ (НУМЕРОВАННЫЙ) ---
KNOWING_LIST = (
    "🤝 **СПИСОК ВОПРОСОВ ДЛЯ ЗНАКОМСТВА**\n\n"
    "1. `Как тебя зовут?` \n2. `Сколько тебе лет?` \n3. `Из какого ты города?` \n4. `Кем ты работаешь?` \n5. `Нравится твоя работа?` \n"
    "6. `Как твой день прошел?` \n7. `Ты сейчас отдыхаешь?` \n8. `Что на ужин было?` \n9. `Ты соня или жаворонок?` \n10. `Что сейчас слушаешь?` \n"
    "11. `Есть питомцы?` \n12. `Твой любимый цвет?` \n13. `Что тебя сегодня улыбнуло?` \n14. `Кофе или чай?` \n15. `Какая сейчас погода?` \n"
    "16. `Часто тут бываешь?` \n17. `Чем занят, когда скучно?` \n18. `Любишь готовить?` \n19. `Твой рост?` \n20. `Ты спортивный парень?` \n"
    "21. `Активный отдых или диван?` \n22. `Где мечтаешь побывать?` \n23. `Твой любимый фильм?` \n24. `Веришь в судьбу?` \n25. `Что тебя смешит?` \n"
    "26. `Риск или комфорт?` \n27. `Лучшее воспоминание?` \n28. `Что ценишь в людях?` \n29. `Куда позовешь на свидание?` \n30. `Ты романтик или реалист?` \n"
    "31. `Твоя любимая книга?` \n32. `Любишь экстрим?` \n33. `Любишь море или горы?` \n34. `Умеешь играть на чем-то?` \n35. `Веришь в интуицию?` \n"
    "36. `Твое хобби?` \n37. `О чем мечтаешь в тишине?` \n38. `Что во мне зацепило?` \n39. `Легко доверяешь людям?` \n40. `Хотел бы приехать?` \n"
    "41. `Веришь в химию через экран?` \n42. `О чем стесняешься спросить?` \n43. `Ты ревнивый?` \n44. `Твой главный страх?` \n45. `Что для тебя уют?` \n"
    "46. `Ты когда-нибудь влюблялся в сети?` \n47. `Что для тебя верность?` \n48. `Умеешь признавать ошибки?` \n49. `Что делает тебя счастливым?` \n50. `Любишь, когда тебя дразнят?` \n"
    "51. `Какая часть моего тела манит?` \n52. `Умеешь делать массаж?` \n53. `Что сделаешь при встрече?` \n54. `Любишь поцелуи в шею?` \n55. `Ты нежный или властный?` \n"
    "56. `Твой любимый запах?` \n57. `Часто думаешь обо мне?` \n58. `Любишь обниматься?` \n59. `Что тебя во мне заводит?` \n60. `Любишь шепот на ушко?` \n"
    "61. `Твой пульс сейчас участился? 😉` \n62. `Твоя смелая фантазия?` \n63. `Доминировать или подчиняться?` \n64. `Что заводит мгновенно?` \n65. `Как относишься к ролевым?` \n"
    "66. `Что хочешь со мной прямо сейчас?` \n67. `Любишь грязные мысли?` \n68. `Как относишься к игрушкам?` \n69. `Самое необычное место?` \n70. `Любишь прелюдию?` \n"
    "71. `Любимая поза?` \n72. `Свет включен или выключен?` \n73. `Твой рекорд по времени?` \n74. `Любишь кусаться?` \n75. `Готов довериться мне полностью?`"
)

# --- ИНТЕРФЕЙС ---
def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🤖 ИИ Ассистент", callback_data="ai"),
        types.InlineKeyboardButton("🤝 Знакомство", callback_data="know"),
        types.InlineKeyboardButton("🔥 Секстинг", callback_data="sext"),
        types.InlineKeyboardButton("⬅️ Главное меню", callback_data="menu")
    )
    return m

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    db_op('INSERT OR REPLACE INTO history VALUES (?, ?, ?)', (message.chat.id, '[]', 'main'))
    bot.send_message(message.chat.id, "Ethera готова к работе. Выбери инструмент:", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Разделы:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    cid = c.message.chat.id
    if c.data == "ai":
        db_op('UPDATE history SET state="ai" WHERE chat_id=?', (cid,))
        bot.edit_message_text("🦾 Режим ИИ активен. Пиши ситуацию для ответа или рассылки:", cid, c.message.message_id, reply_markup=main_menu())
    elif c.data == "know":
        bot.send_message(cid, KNOWING_LIST, parse_mode="Markdown")
    elif c.data == "sext":
        bot.send_message(cid, "🔥 **СЦЕНАРИИ СЕКСТИНГА**\n\n1. `Я из душа, мне так холодно...` \n2. `Примеряю белье, помочь выбрать?` \n3. `Мне приснился сон про нас...` \n4. `Тссс, я сейчас без белья...`", parse_mode="Markdown")
    elif c.data == "menu":
        db_op('UPDATE history SET state="main" WHERE chat_id=?', (cid,))
        bot.edit_message_text("Главное меню. Выбери раздел:", cid, c.message.message_id, reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    res = db_op('SELECT messages, state FROM history WHERE chat_id=?', (m.chat.id,))
    if res and res[1] == "ai":
        bot.send_chat_action(m.chat.id, 'typing')
        hist = json.loads(res[0]); hist.append({"role": "user", "content": m.text})
        try:
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}] + hist)
            ans = comp.choices[0].message.content
            hist.append({"role": "assistant", "content": ans})
            db_op('UPDATE history SET messages=? WHERE chat_id=?', (json.dumps(hist[-15:]), m.chat.id))
            bot.reply_to(m, ans)
        except: bot.reply_to(m, "Ошибка ИИ.")
    else:
        bot.reply_to(m, "Чтобы я начала отвечать, нажми кнопку '🤖 ИИ Ассистент'.", reply_markup=main_menu())

if __name__ == '__main__':
    bot.infinity_polling()
