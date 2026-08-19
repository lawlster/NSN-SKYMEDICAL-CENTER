from telegram import (
    Update,
    ReplyKeyboardMarkup
)
from telegram.ext import ContextTypes

from database import get_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    user = get_user(telegram_id)

    # User is already registered
    if user:

        rank = user[0]
        name = user[1]

        keyboard = [
            ["🩺 Report Sick"],
            ["ℹ Help"]
        ]

        message = (
            f"🏥 Nee Soon Nodepy Report Sick System\n\n"
            f"Welcome {rank} {name}!\n\n"
            "Please choose an option."
        )

    # User has never registered
    else:

        keyboard = [
            ["📝 Register"]
        ]

        message = (
            "🏥 Company Report Sick System\n\n"
            "You are not registered.\n\n"
            "Please register before using the system."
        )

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )

    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )