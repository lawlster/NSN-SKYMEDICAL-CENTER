from telegram import Update

from telegram.ext import ContextTypes


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "ℹ️ HELP\n\n"

        "🩺 Report Sick\n"
        "Use this when you need to report sick.\n\n"

        "1. Select your platoon.\n"
        "2. Enter your reason.\n"
        "3. Enter your remarks.\n"
        "4. Check your information.\n"
        "5. Press Submit.\n\n"

        "Your report will be sent to the "
        "commander assigned to your platoon.\n\n"

        "📝 Register\n"
        "New users must register before using "
        "the Report Sick system.\n\n"

        "⚠️ If you experience a problem with "
        "the system, contact your commander "
        "or company administrator."
    )