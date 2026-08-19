from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database import add_user, user_exists

RANK = 1
NAME = 2


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    if user_exists(telegram_id):
        await update.message.reply_text(
            "✅ You have already registered."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Please enter your rank.\n\nExample: PTE, CPL, 3SG"
    )

    return RANK


async def get_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["rank"] = update.message.text.strip().upper()

    await update.message.reply_text(
        "Please enter your FULL NAME."
    )

    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    rank = context.user_data["rank"]

    full_name = update.message.text.strip()

    add_user(
        telegram_id,
        rank,
        full_name
    )

    await update.message.reply_text(
        f"✅ Registration Complete!\n\n"
        f"Rank: {rank}\n"
        f"Name: {full_name}"
    )

    return ConversationHandler.END