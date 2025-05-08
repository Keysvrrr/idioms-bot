# код
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

import difflib
import logging
import sqlite3
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler


user_languages = {}


def get_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("❓ Помощь", callback_data="help")],
        [InlineKeyboardButton("🫂 Разработчики", callback_data="developers")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bonjour! 🇨🇵\n\n"
        "📚 Отправьте мне фразеологизм — я переведу его с французского на русский или с русского на французский.\n\n"
        "📌 Выберите одну из кнопок ниже, если нужна помощь или информация о разработчиках:",
        reply_markup=get_menu_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Это бот для перевода фразеологизмов.\n"
        "Просто отправьте мне фразеологизм на русском или французском языке, "
        "и я предоставлю вам перевод.\n\n"
        'Если в базе данных бота нет нужного фразеологизма, вы получите данное сообщение - "Извините, я не знаю этот фразеологизм. 💔" \n\n'
        "Команды бота:\n"
        "/start - Запустить бота и показать меню\n"
        "/help - Показать это сообщение помощи\n"
        "/developers - Информация о разработчиках\n\n"
        "Версия бота: 1.0"
    )
    if update.message:
        await update.message.reply_text(help_text)
    elif update.callback_query:
        await update.callback_query.message.reply_text(help_text)


async def developers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    developers_text = (
        '💡 Разработчики бота:\n'
        'Студенты КФУ ИМО ВШИЯиП (группа 04.3-305):\n'
        '- Воронова Ксения\n'
        '- Шинкаренко Екатерина\n'
        '- Евстифеева Надежда\n'
        '- Худайназаров Назар\n\n'
        '🚀 Проект создан в рамках Цифровых Кафедр КФУ — '
        'образовательной программы, объединяющей IT и лингвистику.'
    )
    if update.message:
        await update.message.reply_text(developers_text)
    elif update.callback_query:
        await update.callback_query.message.reply_text(developers_text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    await query.answer()

    if data == 'help':
        await help_command(update, context)

    elif data == 'developers':
        await developers_command(update, context)


# Функция для получения перевода из базы данных
def get_translation(phrase: str) -> str:
    connection = sqlite3.connect('idioms.db')
    cursor = connection.cursor()

    
    cursor.execute("SELECT russian, french FROM idioms")
    idioms = cursor.fetchall()

    best_match_russian = None
    best_match_french = None
    best_similarity_russian = 0
    best_similarity_french = 0

    # Проверка схожести фразы с каждой фразой в бд
    for russian, french in idioms:
        # Вычисление схожести для русского
        similarity_russian = difflib.SequenceMatcher(None, phrase, russian).ratio()
        if similarity_russian > best_similarity_russian:
            best_similarity_russian = similarity_russian
            best_match_russian = russian

        # Вычисление схожести для французского
        similarity_french = difflib.SequenceMatcher(None, phrase, french).ratio()
        if similarity_french > best_similarity_french:
            best_similarity_french = similarity_french
            best_match_french = french

    # Если схожесть хотя бы с одной фразой более 50%, возвращаем перевод
    if best_similarity_russian >= 0.5:
        cursor.execute("SELECT french FROM idioms WHERE russian = ?", (best_match_russian,))
        result = cursor.fetchone()
        connection.close()
        return result[0] if result else None  

    elif best_similarity_french >= 0.5:
        cursor.execute("SELECT russian FROM idioms WHERE french = ?", (best_match_french,))
        result = cursor.fetchone()
        connection.close()
        return result[0] if result else None  

# Если совпадение меньше 50%
    connection.close()
    return None 


# Функция обработки текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.strip()

    translation = get_translation(user_message)

    if translation:
        await update.message.reply_text(translation)
    else:
        await update.message.reply_text("Извините, я не знаю этот фразеологизм. 💔")


# Основная функция для запуска бота
def main():
    if not TOKEN:
        raise ValueError

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("developers", developers_command))
    app.add_handler(CallbackQueryHandler(button_handler))  
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Вывод на терминал сообщение о запуске бота
    print("Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()

