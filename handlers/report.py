from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler
)

from database import (
    get_user,
    add_report,
    get_commander
)


PLATOON = 1
REASON = 2
REMARKS = 3
CONFIRM = 4


async def report(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Clear any old report information
    context.user_data.pop("platoon", None)
    context.user_data.pop("reason", None)
    context.user_data.pop("remarks", None)

    keyboard = [
        [
            InlineKeyboardButton(
                "🏢 HQ",
                callback_data="platoon_HQ"
            )
        ],
        [
            InlineKeyboardButton(
                "1️⃣ Platoon 1",
                callback_data="platoon_1"
            )
        ],
        [
            InlineKeyboardButton(
                "2️⃣ Platoon 2",
                callback_data="platoon_2"
            )
        ],
        [
            InlineKeyboardButton(
                "3️⃣ Platoon 3",
                callback_data="platoon_3"
            )
        ]
    ]

    await update.message.reply_text(
        "📍 Which platoon are you from today?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return PLATOON


async def get_platoon(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    platoon = query.data.replace(
        "platoon_",
        ""
    )

    context.user_data["platoon"] = platoon

    await query.edit_message_text(
        f"✅ Platoon selected: {platoon}\n\n"
        "🤒 What is your reason for reporting sick?"
    )

    return REASON


async def get_reason(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["reason"] = update.message.text

    await update.message.reply_text(
        "📝 Please enter any additional remarks.\n\n"
        "If you have no additional remarks, type "
        "\"None\"."
    )

    return REMARKS


async def get_remarks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["remarks"] = update.message.text

    telegram_id = update.effective_user.id

    user = get_user(telegram_id)

    if user is None:

        await update.message.reply_text(
            "❌ You are not registered.\n\n"
            "Please register before reporting sick."
        )

        return ConversationHandler.END

    rank = user[0]
    name = user[1]

    platoon = context.user_data["platoon"]
    reason = context.user_data["reason"]
    remarks = context.user_data["remarks"]

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Submit",
                callback_data="submit_report"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel_report"
            )
        ]
    ]

    summary = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏥 REPORT SICK REQUEST\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 Rank\n"
        f"{rank}\n\n"

        f"👤 Name\n"
        f"{name}\n\n"

        f"📍 Platoon\n"
        f"{platoon}\n\n"

        f"🤒 Reason\n"
        f"{reason}\n\n"

        f"📝 Remarks\n"
        f"{remarks}\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Please confirm that the information above "
        "is correct."
    )

    await update.message.reply_text(
        summary,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CONFIRM


async def submit_report(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    telegram_id = query.from_user.id

    user = get_user(telegram_id)

    if user is None:

        await query.edit_message_text(
            "❌ You are not registered."
        )

        return ConversationHandler.END

    rank = user[0]
    name = user[1]

    platoon = context.user_data.get("platoon")
    reason = context.user_data.get("reason")
    remarks = context.user_data.get("remarks")

    if not platoon or not reason or not remarks:

        await query.edit_message_text(
            "❌ Your report information is incomplete.\n\n"
            "Please start the report again."
        )

        return ConversationHandler.END

    # Find the commander assigned to this platoon
    commander = get_commander(platoon)

    if commander is None or commander[0] is None:

        await query.edit_message_text(
            "⚠️ Your report could not be submitted.\n\n"
            f"No commander is currently assigned to "
            f"Platoon {platoon}.\n\n"
            "Please contact your administrator."
        )

        return ConversationHandler.END

    commander_id = commander[0]

    # Save report and get its unique ID
    report_id = add_report(
        telegram_id,
        platoon,
        reason,
        remarks
    )

    # Create commander buttons
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{report_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{report_id}"
            )
        ]
    ]

    # Send report to commander
    await context.bot.send_message(
        chat_id=commander_id,
        text=(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🚨 REPORT SICK REQUEST\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            f"📋 Report #{report_id}\n\n"

            f"👤 Rank\n"
            f"{rank}\n\n"

            f"👤 Name\n"
            f"{name}\n\n"

            f"📍 Platoon\n"
            f"{platoon}\n\n"

            f"🤒 Reason\n"
            f"{reason}\n\n"

            f"📝 Remarks\n"
            f"{remarks}\n\n"

            f"📅 Date\n"
            f"{get_current_date()}\n\n"

            f"🕒 Time\n"
            f"{get_current_time()}\n\n"

            "Status\n"
            "🟡 Pending\n\n"

            "Please select an action below."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Tell soldier it was successfully submitted
    await query.edit_message_text(
        (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ REPORT SUBMITTED\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            f"📋 Report #{report_id}\n\n"

            f"📍 Platoon: {platoon}\n"
            f"📅 Date: {get_current_date()}\n"
            f"🕒 Time: {get_current_time()}\n\n"

            "🟡 Status: Pending\n\n"

            "Your report has been sent to your "
            "platoon commander for approval."
        )
    )

    # Clear temporary report information
    context.user_data.pop("platoon", None)
    context.user_data.pop("reason", None)
    context.user_data.pop("remarks", None)

    return ConversationHandler.END


async def cancel_report(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    context.user_data.pop("platoon", None)
    context.user_data.pop("reason", None)
    context.user_data.pop("remarks", None)

    await query.edit_message_text(
        "❌ Report cancelled.\n\n"
        "You can start a new report anytime by "
        "pressing 🩺 Report Sick."
    )

    return ConversationHandler.END


def get_current_date():

    from datetime import datetime

    return datetime.now().strftime(
        "%d %b %Y"
    )


def get_current_time():

    from datetime import datetime

    return datetime.now().strftime(
        "%I:%M %p"
    )