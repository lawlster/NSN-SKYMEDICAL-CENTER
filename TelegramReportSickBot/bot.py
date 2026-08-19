from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from handlers.admin import admin_panel
from config import TOKEN
from database import create_tables

from handlers.start import start


from handlers.approval import (
    approve_request,
    reject_request,
    get_rejection_reason,
    REJECTION_REASON
)



from handlers.register import (
    register,
    get_rank,
    get_name,
    RANK,
    NAME
)

from handlers.report import (
    report,
    get_platoon,
    get_reason,
    get_remarks,
    submit_report,
    cancel_report,
    PLATOON,
    REASON,
    REMARKS,
    CONFIRM
)

# Create database tables
create_tables()

# Create bot
app = Application.builder().token(TOKEN).build()

# -------------------------
# Registration Conversation
# -------------------------
register_handler = ConversationHandler(
    entry_points=[
        CommandHandler("register", register),
        MessageHandler(filters.Regex("^📝 Register$"), register)
    ],
    states={
        RANK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_rank)
        ],
        NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)
        ],
    },
    fallbacks=[]
)
approval_handler = ConversationHandler(

    entry_points=[
        CallbackQueryHandler(
            reject_request,
            pattern=r"^reject_\d+$"
        )
    ],

    states={

        REJECTION_REASON: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_rejection_reason
            )
        ]

    },

    fallbacks=[]
)

app.add_handler(approval_handler)

app.add_handler(
    CallbackQueryHandler(
        approve_request,
        pattern=r"^approve_\d+$"
    )
)
# -------------------------
# Report Sick Conversation
# -------------------------

report_handler = ConversationHandler(

    entry_points=[
        MessageHandler(
            filters.Regex("^🩺 Report Sick$"),
            report
        )
    ],

    states={

        PLATOON: [
            CallbackQueryHandler(
                get_platoon,
                pattern=r"^platoon_(HQ|1|2|3)$"
            )
        ],

        REASON: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_reason
            )
        ],

        REMARKS: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_remarks
            )
        ],

        CONFIRM: [
            CallbackQueryHandler(
                submit_report,
                pattern=r"^submit_report$"
            ),

            CallbackQueryHandler(
                cancel_report,
                pattern=r"^cancel_report$"
            )
        ]
    },

    fallbacks=[]
)

from handlers.admin import (
    admin_panel,
    commander_menu,
    choose_commander,
    save_commander
)
# -------------------------
# Handlers
# -------------------------
app.add_handler(CommandHandler("start", start))
app.add_handler(register_handler)
app.add_handler(report_handler)
app.add_handler(CommandHandler("admin", admin_panel))


app.add_handler(
    CallbackQueryHandler(
        commander_menu,
        pattern="^manage_commanders$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        choose_commander,
        pattern="^platoon_"
    )
)

app.add_handler(
    CallbackQueryHandler(
        save_commander,
        pattern="^user_"
    )
)

app.add_handler(
    CallbackQueryHandler(
        approve_request,
        pattern=r"^approve_\d+$"
    )
)
print("🏥 Nee Soon Node Report Sick Bot Started!")

app.run_polling()