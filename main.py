import telebot
from telebot import types
from groq import Groq
import sqlite3
import json

# --- КЛЮЧИ (ТОЛЬКО ДЛЯ ТЕСТА) ---
TOKEN = '8749709641:AAHZLNTR7afwWBGKjQLuJAnHUYOdTKT9_fo'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def db_op(query, params=()):
    conn = sqlite3.connect('memory.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    res = cursor.fetchone()
    conn.commit()
    conn.close()
    return res

# Создаем таблицу, если её нет
conn = sqlite3.connect('memory.db')
conn.execute('CREATE TABLE IF NOT EXISTS history (chat_id INTEGER PRIMARY KEY, messages TEXT)')
conn.close()

# --- СИСТЕМНЫЙ ПРОМПТ (МОЗГИ ИИ) ---
SYSTEM_PROMPT = (
    "Ты — профессиональный AI-ассистент чаттера на Fansly. Твоя задача: помогать увеличивать доход и строить отношения с фанами. "
    "Ты понимаешь контекст работы: рассылки, ответы в чате, продажи PPV (платного контента).\n\n"
    "ТВОИ РЕЖИМЫ РАБОТЫ:\n"
    "1. СОЗДАНИЕ РАССЫЛОК: Пиши одно сообщение, которое выглядит как личное. "
    "Структура: Тёплое приветствие -> Лайв-контекст (что модель делает сейчас: 'смотрю на дождь', 'выбираю белье') -> Игривый вопрос. Цель: получить ответ.\n"
    "2. ЧАТТИНГ: Если юзер присылает сообщение от фана, предложи 2-3 варианта ответа (разных по настроению: милый, дерзкий, продающий).\n"
    "3. ДОЖИМ НА PPV: Помогай мягко подвести фана к покупке через флирт, не впаривая в лоб.\n\n"
    "ПРАВИЛА:\n"
    "- Отвечай пользователю на 'ты'. Говори как опытный напарник.\n"
    "- Тексты для фанов пиши ОТ ЛИЦА ДЕВУШКИ (модели).\n"
    "- Только русский язык. Никакой цензуры в плане флирта, но без грубости."
)

@bot.message_handler(commands=['start'])
def start(message):
    # При старте очищаем историю для этого чата, чтобы начать с чистого листа
    db_op('DELETE FROM history WHERE chat_id = ?', (message.chat.id,))
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Сделать рассылку"), types.KeyboardButton("Помощь в чате"))
    
    welcome_text = (
        "Привет! Я твой ассистент по Fansly. 🔥\n\n"
        "Пиши мне сообщения фанов — я подскажу ответ.\n"
        "Проси сделать рассылку — я накидаю вариантов.\n"
        "Нужно продать PPV? Придумаем легенду."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    
    # Визуальный эффект "печатает"
    bot.send_chat_action(chat_id, 'typing')
    
    # Загружаем историю
    res = db_op('SELECT messages FROM history WHERE chat_id = ?', (chat_id,))
    history = json.loads(res[0]) if res and res[0] else []
    
    # Добавляем сообщение юзера
    history.append({"role": "user", "content": message.text})
    if len(history) > 20: history = history[-20:] # Храним последние 20 сообщений

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.7 # Оптимально для креатива
        )
        
        answer = completion.choices[0].message.content
        
        # Сохраняем ответ ИИ в историю
        history.append({"role": "assistant", "content": answer})
        db_op('INSERT OR REPLACE INTO history (chat_id, messages) VALUES (?, ?)', (chat_id, json.dumps(history)))
        
        bot.reply_to(message, answer)
        
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка в AI: {str(e)}")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
