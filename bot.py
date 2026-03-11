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
# ⚠️ ВАЖНО! НЕ вставляем токен напрямую
# На Replit будем использовать Secrets
# -----------------------------
import os
TOKEN = 8274020327:AAH_oDLQtAud6Sbwiz8fCBUwsHXr7_wNOUg  # токен хранится в Replit Secrets

# ⚠️ Вставь сюда chat_id группы
GROUP_CHAT_ID = -1003796915790

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# -----------------------------
# Прогресс каждого пользователя
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
    "9️⃣ Согласие на обработку ПД (напиши *СОГЛАСЕН*):\n"
    "Заполняя и отправляя форму, я даю согласие на обработку моих персональных данных и передачу их третьим лицам."
]

# -----------------------------
# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Заполнить заявку", callback_data='start_form')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажми кнопку, чтобы заполнить заявку:", reply_markup=reply_markup)

# -----------------------------
# Кнопка начала анкеты
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"step": 0, "answers": []}
    await query.edit_message_text(text=questions[0])

# -----------------------------
# Обработка текстовых ответов
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_data:
        await update.message.reply_text("Сначала нажмите /start")
        return

    step = user_data[user_id]["step"]
    text = update.message.text

    # -----------------------------
    # Проверка последнего вопроса (согласие)
    if step == len(questions) - 1:
        if text.strip().upper() != "СОГЛАСЕН":
            await update.message.reply_text(
                "❌ Вы должны написать *СОГЛАСЕН*, чтобы отправить форму. Попробуйте ещё раз."
            )
            return

    # Сохраняем ответ
    user_data[user_id]["answers"].append(text)
    step += 1

    # Если ещё вопросы есть
    if step < len(questions):
        user_data[user_id]["step"] = step
        await update.message.reply_text(questions[step])
    else:
        # Формируем сообщение для группы
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
# Проверка, что бот жив
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я жив и работаю на Replit! ✅")

# -----------------------------
# Запуск бота
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))  # проверка
    app.add_handler(CallbackQueryHandler(button, pattern="start_form"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()