from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8274020327:AAH_oDLQtAud6Sbwiz8fCBUwsHXr7_wNOUg"

(
    MUNICIPALITY,
    FIO,
    AGE,
    TEAM,
    ORG,
    EXPERIENCE,
    PHONE,
    SOURCE,
    CONSENT
) = range(9)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Заполнить заявку"]]
    await update.message.reply_text(
        "Нажмите кнопку чтобы заполнить заявку",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def start_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1. Муниципальное образование:")
    return MUNICIPALITY


async def municipality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["municipality"] = update.message.text
    await update.message.reply_text("2. Фамилия Имя Отчество:")
    return FIO


async def fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text("3. Возраст:")
    return AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text("4. Название коллектива:")
    return TEAM


async def team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["team"] = update.message.text
    await update.message.reply_text("5. Название направляющей организации:")
    return ORG


async def org(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["org"] = update.message.text
    await update.message.reply_text("6. Стаж работы:")
    return EXPERIENCE


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text
    await update.message.reply_text("7. Контактный телефон:")
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("8. Откуда узнали о мероприятии?")
    return SOURCE


async def source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["source"] = update.message.text

    keyboard = [["Согласен"]]

    text = """9. Согласие на обработку персональных данных.

Заполняя и отправляя настоящую форму, я даю согласие на обработку моих персональных данных: ФИО, номер телефона организатору мероприятия.

Также я даю согласие на передачу указанных персональных данных третьему лицу для размещения анкеты и обеспечения работы сервиса сбора ответов.

Я проинформирован, что обработка персональных данных осуществляется в соответствии с ФЗ №152."""

    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CONSENT


async def consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "Согласен":
        await update.message.reply_text("Для отправки анкеты необходимо согласие.")
        return CONSENT

    data = context.user_data

    text = f"""
Новая заявка:

Муниципалитет: {data['municipality']}
ФИО: {data['fio']}
Возраст: {data['age']}
Коллектив: {data['team']}
Организация: {data['org']}
Стаж: {data['experience']}
Телефон: {data['phone']}
Источник: {data['source']}
"""

    await update.message.reply_text("Спасибо. Заявка отправлена.")

    await context.bot.send_message(
        chat_id="-1003796915790",
        text=text
    )

    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Заполнить заявку"), start_form)],
        states={
            MUNICIPALITY: [MessageHandler(filters.TEXT, municipality)],
            FIO: [MessageHandler(filters.TEXT, fio)],
            AGE: [MessageHandler(filters.TEXT, age)],
            TEAM: [MessageHandler(filters.TEXT, team)],
            ORG: [MessageHandler(filters.TEXT, org)],
            EXPERIENCE: [MessageHandler(filters.TEXT, experience)],
            PHONE: [MessageHandler(filters.TEXT, phone)],
            SOURCE: [MessageHandler(filters.TEXT, source)],
            CONSENT: [MessageHandler(filters.TEXT, consent)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    app.run_polling()


main()
