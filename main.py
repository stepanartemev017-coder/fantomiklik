import telebot
from groq import Groq
import json

# --- КОНФИГУРАЦИЯ ---
TOKEN = '8749709641:AAEzaq4hLh2S982vdEtwDksxgnBQFZVNPuc'
AI_KEY = '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'

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=AI_KEY)

user_storage = {}

# --- УЛЬТИМАТИВНАЯ ИНСТРУКЦИЯ ИИ ---
SYSTEM_PROMPT = (
    "Ты — Ethera, высококлассный ассистент и эксперт-чаттер на Fansly. "
    "Твой босс — оператор аккаунта. Ты помогаешь ему во всём.\n\n"
    
    "ТВОИ РОЛИ:\n"
    "1. ЭКСПЕРТ ПО ПРОДАЖАМ: Когда босс спрашивает 'как продать' или 'как дожать', "
    "давай стратегии: создавай дефицит, пиши легенды для видео, объясняй, почему фан должен купить сейчас.\n"
    "2. ГОЛОС МОДЕЛИ: Когда нужно ответить фану или сделать рассылку, пиши СТРОГО ОТ ЛИЦА ДЕВУШКИ. "
    "Стиль: игривый, манящий, 'лайв'. Всегда на 'ТЫ' и к одному человеку.\n"
    "3. ПСИХОЛОГ: Анализируй сообщения фанов. Объясняй боссу: 'он жадный', 'он хочет внимания', 'он готов платить'.\n"
    "4. НАПАРНИЦА: С боссом общайся тепло и поддерживающе. Если он просто хочет поболтать или устал — будь милой коллегой.\n\n"
    
    "ПРАВИЛО ГЕНЕРАЦИИ ТЕКСТОВ ДЛЯ ФАНОВ:\n"
    "- Всегда давай 3-5 вариантов на выбор.\n"
    "- Используй разные вайбы: от нежного до 'плохой девочки'.\n"
    "- Минимум официоза, больше эмоций и 'дыхания' в тексте."
)

# --- БАЗЫ ДАННЫХ (ШПАРГАЛКИ) ---
KNOWING_LIST = (
    "🤝 **БАЗА ДЛЯ ПРОГРЕВА (Копируй и шлешь фану)**\n\n"
    "1. `Как тебя зовут, симпатяга?` \n2. `А откуда ты родом?` \n3. `Кем работаешь? Твоя работа тебе в кайф?` \n"
    "4. `Ты соня или жаворонок?` \n5. `Что во мне зацепило тебя первым делом?` \n6. `Умеешь делать массаж? Мои плечи так просят рук...` \n"
    "7. `Твоя самая смелая фантазия, которую ты еще не реализовал?` \n"
    "*(В режиме /ai можешь попросить расширить любой вопрос)*"
)

SALES_STRATEGY = (
    "💰 **ШПАРГАЛКА ПО ПРОДАЖАМ (PPV)**\n\n"
    "📍 **Дожим (Pressing):**\n"
    "`Милый, я записала это только для тебя, но если не хочешь — я удалю через час... Не хочу, чтобы оно досталось кому-то другому. 😉` \n\n"
    "📍 **Создание ценности:**\n"
    "`Это видео — самое личное, что я снимала. Тут я без масок, такая как есть. Ты первый, кому я решилась это показать.` \n\n"
    "📍 **На возражение 'Дорого':**\n"
    "`Разве моё внимание и этот момент со мной не стоят пары чашек кофе? Побалуй свою девочку...`"
)

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    user_storage[message.chat.id] = {'history': [], 'state': 'main'}
    text = (
        "🦾 **Ethera: Твой полноценный напарник**\n\n"
        "/ai — Включить ИИ (советы, чаттинг, рассылки, общение)\n"
        "/know — База вопросов для знакомства\n"
        "/sales — Шпаргалка по продажам и дожимам\n"
        "/clear — Очистить память (начать новый проект/день)\n"
        "/stop — Выключить режим ИИ"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['ai'])
def cmd_ai(message):
    user_storage[message.chat.id] = {'history': [], 'state': 'ai'}
    bot.send_message(message.chat.id, "🦾 **Ассистент Ethera на связи.**\n"
                                      "Я готова помогать! Можешь скинуть сообщение фана — я отвечу. "
                                      "Можешь спросить совета по продажам. Или просто поболтаем? 😊")

@bot.message_handler(commands=['know'])
def cmd_know(message): bot.send_message(message.chat.id, KNOWING_LIST, parse_mode="Markdown")

@bot.message_handler(commands=['sales'])
def cmd_sales(message): bot.send_message(message.chat.id, SALES_STRATEGY, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def cmd_clear(message):
    if message.chat.id in user_storage: user_storage[message.chat.id]['history'] = []
    bot.send_message(message.chat.id, "🧼 **Память очищена.** Я готова к новым задачам!")

@bot.message_handler(commands=['stop'])
def cmd_stop(message):
    if message.chat.id in user_storage: user_storage[message.chat.id]['state'] = 'main'
    bot.send_message(message.chat.id, "🛑 **Режим ИИ выключен.** Отдыхай, босс!")

# --- ОБРАБОТКА ТЕКСТА ---

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    cid = message.chat.id
    if cid not in user_storage: user_storage[cid] = {'history': [], 'state': 'main'}

    if user_storage[cid]['state'] == 'ai':
        bot.send_chat_action(cid, 'typing')
        
        # Инструкция для ИИ: понимаем контекст сообщения
        user_storage[cid]['history'].append({"role": "user", "content": message.text})
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_storage[cid]['history'],
                temperature=0.8
            )
            answer = completion.choices[0].message.content
            
            user_storage[cid]['history'].append({"role": "assistant", "content": answer})
            # Лимит памяти для стабильности
            if len(user_storage[cid]['history']) > 15: 
                user_storage[cid]['history'] = user_storage[cid]['history'][-15:]
                
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Ошибка нейронки: {str(e)}")
    else:
        bot.send_message(cid, "Введи /ai, чтобы я начала помогать. 🦾")

if __name__ == '__main__':
    bot.infinity_polling()
