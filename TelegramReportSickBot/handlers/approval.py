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
    get_report,
    approve_report,
    reject_report,
    get_user
)

REJECTION_REASON = 10


async def approve_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    # Example callback_data:
    # approve_25
    report_id = int(query.data.replace("approve_", ""))

    report = get_report(report_id)

    if report is None:
        await query.edit_message_text(
            "❌ This report could not be found."
        )
        return

    # Database structure:
    # 0 = id
    # 1 = telegram_id
    # 2 = platoon
    # 3 = reason
    # 4 = remarks
    # 5 = status
    # 6 = report_date
    # 7 = report_time
    # 8 = approved_by
    # 9 = approved_at

    if report[5] != "Pending":
        await query.answer(
            f"This report is already {report[5]}.",
            show_alert=True
        )
        return

    commander_id = query.from_user.id

    approve_report(
        report_id,
        commander_id
    )

    soldier_id = report[1]

    # Notify soldier
    await context.bot.send_message(
        chat_id=soldier_id,
        text=(
            "✅ REPORT SICK APPROVED\n\n"
            f"📋 Report #{report_id}\n\n"
            f"📍 Platoon: {report[2]}\n"
            f"📅 Date: {report[6]}\n"
            f"🕒 Time: {report[7]}\n\n"
            "Your report sick request has been "
            "approved by your commander."
        )
    )

    # Update commander's message
    await query.edit_message_text(
        (
            "✅ REPORT SICK APPROVED\n\n"
            f"📋 Report #{report_id}\n\n"
            f"📍 Platoon: {report[2]}\n"
            f"🤒 Reason: {report[3]}\n"
            f"📝 Remarks: {report[4]}\n\n"
            f"📅 Date: {report[6]}\n"
            f"🕒 Time: {report[7]}\n\n"
            "Status: 🟢 Approved"
        )
    )


async def reject_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    report_id = int(query.data.replace("reject_", ""))

    report = get_report(report_id)

    if report is None:
        await query.edit_message_text(
            "❌ This report could not be found."
        )
        return ConversationHandler.END

    if report[5] != "Pending":
        await query.answer(
            f"This report is already {report[5]}.",
            show_alert=True
        )
        return ConversationHandler.END

    context.user_data["rejection_report_id"] = report_id

    await query.message.reply_text(
        f"❌ Reject Report #{report_id}\n\n"
        "Please enter the reason for rejecting this report."
    )

    return REJECTION_REASON


async def get_rejection_reason(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    rejection_reason = update.message.text

    report_id = context.user_data.get(
        "rejection_report_id"
    )

    if not report_id:
        await update.message.reply_text(
            "❌ Report information could not be found."
        )
        return ConversationHandler.END

    report = get_report(report_id)

    if report is None:
        await update.message.reply_text(
            "❌ This report could not be found."
        )
        return ConversationHandler.END

    if report[5] != "Pending":
        await update.message.reply_text(
            f"❌ This report is already {report[5]}."
        )
        return ConversationHandler.END

    commander_id = update.effective_user.id

    reject_report(
    report_id,
    commander_id,
    rejection_reason
    )

    soldier_id = report[1]

    # Notify soldier
    await context.bot.send_message(
        chat_id=soldier_id,
        text=(
            "❌ REPORT SICK REJECTED\n\n"
            f"📋 Report #{report_id}\n\n"
            f"📍 Platoon: {report[2]}\n"
            f"📅 Date: {report[6]}\n"
            f"🕒 Time: {report[7]}\n\n"
            f"Reason for rejection:\n"
            f"{rejection_reason}"
        )
    )

    await update.message.reply_text(
        (
            "❌ REPORT REJECTED\n\n"
            f"📋 Report #{report_id}\n"
            f"📍 Platoon: {report[2]}\n\n"
            f"Reason:\n"
            f"{rejection_reason}\n\n"
            "Status: 🔴 Rejected"
        )
    )

    context.user_data.pop(
        "rejection_report_id",
        None
    )

    return ConversationHandler.END