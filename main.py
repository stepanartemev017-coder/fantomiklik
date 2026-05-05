import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- КЛЮЧИ (ОБЯЗАТЕЛЬНО ПРОВЕРЬ ИХ) ---
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

# Инициализация БД
conn = sqlite3.connect('memory.db')
conn.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
conn.close()

# --- ОБНОВЛЕННЫЙ СИСТЕМНЫЙ ПРОМПТ ---
SYSTEM_PROMPT = (
    "Ты — ИИ-ассистент для профессионального чаттера на Fansly. Твоя роль — помогать чаттеру в работе. "
    "ВАЖНО: Пользователь, который тебе пишет — это ТВОЙ КОЛЛЕГА (чаттер), а не фан. Не флиртуй с ним!\n\n"
    "ТВОИ ЗАДАЧИ:\n"
    "1. РАССЫЛКИ: По запросу создавай личные, живые сообщения. Структура: Лайв-контекст -> Игривый вопрос.\n"
    "2. ОТВЕТЫ: Если чаттер прислал фразу фана, предложи 3 варианта ответа: Нежный, Дерзкий, Продающий (ведущий к покупке контента).\n"
    "3. СТРАТЕГИЯ: Помогай дожимать фанов на чаевые и покупку PPV.\n\n"
    "СТИЛЬ ОТВЕТОВ ДЛЯ ЧАТТЕРА:\n"
    "- Общайся с чаттером конструктивно, как профи-наставник.\n"
    "- Тексты, которые предназначены ДЛЯ ФАНОВ, выделяй отдельно (например, в кавычках или блоках)."
)

@bot.message_handler(commands=['start'])
def start(message):
    db_op('DELETE FROM history WHERE chat_id = ?', (message.chat.id,))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔥 Сделать рассылку"), types.KeyboardButton("💬 Как ответить фану?"))
    
    welcome_msg = (
        "Бот-ассистент Fansly запущен. 🚀\n\n"
        "Теперь я понимаю, что ты — мой оператор. "
        "Присылай запросы, и я буду генерировать варианты текстов для работы."
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    # Загружаем историю
    res = db_op('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    history = json.loads(res[0]) if res and res and res[0] else []
    
    # Добавляем контекст, что пишет именно чаттер (админ)
    prompt_with_context = f"Запрос от чаттера: {message.text}"
    history.append({"role": "user", "content": prompt_with_context})
    
    if len(history) > 20: history = history[-20:]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.8
        )
        
        answer = completion.choices[0].message.content
        
        # Сохраняем ответ в историю
        history.append({"role": "assistant", "content": answer})
        db_op('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
        
        bot.reply_to(message, answer)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == '__main__':
    print("Ассистент работает...")
    bot.infinity_polling()
