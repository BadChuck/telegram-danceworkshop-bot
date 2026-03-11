# ===============================================
# 🟢 Телеграм-бот для заполнения заявки на фестиваль
# Python 3.11+ и python-telegram-bot v20+
# Автор: Илья
# ===============================================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import logging

# -----------------------------
# ВАЖНО! Вставь сюда свой токен от BotFather
TOKEN = "8274020327:AAH_oDLQtAud6Sbwiz8fCBUwsHXr7_wNOUg"

# ВАЖНО! Вставь сюда chat_id группы, куда бот будет отправлять ответы
GROUP_CHAT_ID = -1003796915790

# Включаем логирование (чтобы видеть ошибки)
logging.basicConfig(level=logging.INFO)

# -----------------------------
# Здесь храним прогресс каждого пользователя (какой вопрос на каком шаге)
user_data = {}

# -----------------------------
# Список вопросов анкеты
questions = [
    "1️⃣ Муниципальное образование:",
    "2️⃣ Фамилия, имя, отчество:",
    "3️⃣ Возраст:",
    "4️⃣ Название коллектива:",
    "5️⃣ Название направляющей организации:",
    "6️⃣ Стаж работы:",
    "7️⃣ Контактный телефон:",
    "8️⃣ Откуда узнали о мероприятии:",
    "9️⃣ Согласие на обработку ПД (ответьте 'да'):\n"
    "Заполняя и отправляя настоящую форму, я даю согласие на обработку моих персональных данных и передачу их третьим лицам."
]

# -----------------------------
# Функция стартового сообщения
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Заполнить заявку", callback_data='start_form')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажми кнопку, чтобы заполнить заявку:", reply_markup=reply_markup)

# -----------------------------
# Функция обработки нажатия кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # обязательно отвечаем на нажатие кнопки
    user_id = query.from_user.id
    # создаем запись о пользователе и начинаем с первого вопроса
    user_data[user_id] = {"step": 0, "answers": []}
    await query.edit_message_text(text=questions[0])

# -----------------------------
# Функция обработки текста пользователя
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Если пользователь еще не нажал кнопку /start
    if user_id not in user_data:
        await update.message.reply_text("Сначала нажмите /start")
        return

    # Сохраняем ответ
    step = user_data[user_id]["step"]
    text = update.message.text
    user_data[user_id]["answers"].append(text)
    step += 1

    # Если вопросы еще остались
    if step < len(questions):
        user_data[user_id]["step"] = step
        await update.message.reply_text(questions[step])
    else:
        # Формируем красивое сообщение для группы
        answers = user_data[user_id]["answers"]
        message_text = "📄 Новая заявка на фестиваль:\n\n"
        for q, a in zip(questions, answers):
            message_text += f"{q} {a}\n"

        # Отправляем в группу
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_text)

        # Сообщаем пользователю
        await update.message.reply_text("Спасибо! Заявка принята ✅")

        # Удаляем пользователя из памяти
        del user_data[user_id]

# -----------------------------
# Главная функция запуска бота
def main():
    # Создаем приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчик команды /start
    app.add_handler(CommandHandler("start", start))
    # Обработчик кнопки "Заполнить заявку"
    app.add_handler(CallbackQueryHandler(button, pattern="start_form"))
    # Обработчик текстовых сообщений пользователя
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    app.run_polling()

# -----------------------------
# Запуск бота
if __name__ == "__main__":
    main()