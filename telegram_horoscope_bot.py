import os
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.background import BackgroundScheduler
import openai
import random
from datetime import datetime

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Zodiac signs
ZODIAC_SIGNS = [
    "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
    "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
]

# Initialize bot
bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Generate horoscope using OpenAI
def generate_horoscope(sign):
    prompt = f"Создай ироничный и вдохновляющий гороскоп для знака зодиака {sign}."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Morning post with all zodiac signs
def morning_post():
    message = "☀️ Доброе утро! Ваши гороскопы на сегодня:\n\n"
    keyboard = []
    for sign in ZODIAC_SIGNS:
        text = generate_horoscope(sign)
        message += f"♈ {sign}: {text}\n\n"
        keyboard.append([InlineKeyboardButton(sign, callback_data=f"reaction:{sign}")])
    bot.send_message(
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Random predictions throughout the day
def random_prediction():
    sign = random.choice(ZODIAC_SIGNS)
    prediction = generate_horoscope(sign)
    keyboard = [
        [
            InlineKeyboardButton("Сбылось", callback_data="reaction:success"),
            InlineKeyboardButton("Ждём", callback_data="reaction:waiting"),
            InlineKeyboardButton("Не моё", callback_data="reaction:notmine")
        ]
    ]
    bot.send_message(
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        text=f"✨ {sign}: {prediction}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Reaction handler
def button_handler(update, context):
    query = update.callback_query
    query.answer()
    data = query.data.split(":")
    if data[0] == "reaction":
        reaction = data[1]
        query.edit_message_text(text=f"Спасибо за ваш ответ: {reaction}")

# Scheduler for posting
scheduler = BackgroundScheduler()
scheduler.add_job(morning_post, 'cron', hour=8, minute=0)
scheduler.add_job(random_prediction, 'interval', hours=4)  # Every 4 hours
scheduler.start()

# Command start
def start(update, context):
    update.message.reply_text("Привет! Я ваш гороскоп-бот. Ждите вдохновляющих предсказаний!")

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_handler))

# Start the bot
if __name__ == "__main__":
    updater.start_polling()
    updater.idle()