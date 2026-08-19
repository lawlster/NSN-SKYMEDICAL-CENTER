from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler
)

from config import SUPER_ADMINS
from database import (
    get_all_users,
    assign_commander
)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in SUPER_ADMINS:
        await update.message.reply_text("❌ Access Denied.")
        return

    keyboard = [
        [InlineKeyboardButton("👤 Commander Management", callback_data="manage_commanders")],
        [InlineKeyboardButton("📋 View Reports", callback_data="reports")],
        [InlineKeyboardButton("📊 Attendance", callback_data="attendance")],
        [InlineKeyboardButton("👥 Registered Users", callback_data="users")]
    ]

    await update.message.reply_text(
        "⚙ Company Administration",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def commander_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🏢 HQ", callback_data="platoon_HQ")],
        [InlineKeyboardButton("1️⃣ Platoon 1", callback_data="platoon_1")],
        [InlineKeyboardButton("2️⃣ Platoon 2", callback_data="platoon_2")],
        [InlineKeyboardButton("3️⃣ Platoon 3", callback_data="platoon_3")]
    ]

    await query.edit_message_text(
        "Select a platoon:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def choose_commander(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    platoon = query.data.replace("platoon_", "")

    context.user_data["selected_platoon"] = platoon

    users = get_all_users()

    keyboard = []

    for telegram_id, rank, full_name in users:

        keyboard.append([
            InlineKeyboardButton(
                f"{rank} {full_name}",
                callback_data=f"user_{telegram_id}"
            )
        ])

    await query.edit_message_text(
        f"Assign commander for Platoon {platoon}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def save_commander(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    telegram_id = int(query.data.replace("user_", ""))

    platoon = context.user_data["selected_platoon"]

    assign_commander(platoon, telegram_id)

    await query.edit_message_text(

        f"✅ Commander Assigned\n\n"
        f"Platoon: {platoon}"

    )