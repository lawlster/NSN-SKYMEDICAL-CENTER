from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

from config import SUPER_ADMINS
from database import (
    get_all_users,
    assign_commander,
    get_all_reports_today,
    get_attendance_today,
    get_commander
)


def is_admin(telegram_id):
    return telegram_id in SUPER_ADMINS


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in SUPER_ADMINS:
        await update.message.reply_text(
            "❌ Access Denied."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "👤 Commander Management",
                callback_data="admin_commanders"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 View Reports",
                callback_data="admin_reports"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Attendance",
                callback_data="admin_attendance"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Registered Users",
                callback_data="admin_users"
            )
        ]
    ]

    await update.message.reply_text(
        "⚙️ COMPANY ADMIN PANEL\n\n"
        "Please select an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# COMMANDER MANAGEMENT
# =========================================================

async def commander_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer(
            "❌ Access Denied.",
            show_alert=True
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "🏢 HQ",
                callback_data="assign_HQ"
            )
        ],
        [
            InlineKeyboardButton(
                "1️⃣ Platoon 1",
                callback_data="assign_1"
            )
        ],
        [
            InlineKeyboardButton(
                "2️⃣ Platoon 2",
                callback_data="assign_2"
            )
        ],
        [
            InlineKeyboardButton(
                "3️⃣ Platoon 3",
                callback_data="assign_3"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="admin_back"
            )
        ]
    ]

    await query.edit_message_text(
        "👤 COMMANDER MANAGEMENT\n\n"
        "Select the platoon you want to assign a commander to:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def choose_commander(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    platoon = query.data.replace(
        "assign_",
        ""
    )

    context.user_data["selected_platoon"] = platoon

    users = get_all_users()

    if not users:

        await query.edit_message_text(
            "❌ There are no registered users yet.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="admin_commanders"
                    )
                ]
            ])
        )

        return

    keyboard = []

    for telegram_id, rank, full_name in users:

        keyboard.append([
            InlineKeyboardButton(
                f"{rank} {full_name}",
                callback_data=f"selectcommander_{telegram_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Back",
            callback_data="admin_commanders"
        )
    ])

    await query.edit_message_text(
        f"👤 ASSIGN COMMANDER\n\n"
        f"Platoon: {platoon}\n\n"
        "Select the registered user who should "
        "be the commander:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def save_commander(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    telegram_id = int(
        query.data.replace(
            "selectcommander_",
            ""
        )
    )

    platoon = context.user_data.get(
        "selected_platoon"
    )

    if not platoon:

        await query.edit_message_text(
            "❌ Platoon selection was lost."
        )
        return

    success = assign_commander(
        platoon,
        telegram_id
    )

    if not success:

        await query.edit_message_text(
            "❌ Could not assign commander.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="admin_commanders"
                    )
                ]
            ])
        )

        return

    await query.edit_message_text(
        f"✅ COMMANDER ASSIGNED\n\n"
        f"Platoon: {platoon}\n\n"
        "The commander has been successfully assigned.\n\n"
        "All future sick reports from this platoon "
        "will be sent to this commander.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 Back",
                    callback_data="admin_commanders"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 Admin Menu",
                    callback_data="admin_back"
                )
            ]
        ])
    )


# =========================================================
# VIEW REPORTS
# =========================================================

async def view_reports(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    reports = get_all_reports_today()

    if not reports:

        text = (
            "📋 TODAY'S REPORTS\n\n"
            "There are no sick reports for today."
        )

    else:

        lines = [
            "📋 TODAY'S SICK REPORTS\n"
        ]

        for report in reports:

            report_id = report[0]
            telegram_id = report[1]
            platoon = report[2]
            reason = report[3]
            remarks = report[4]
            status = report[5]
            report_date = report[6]
            report_time = report[7]

            user = get_user_safe(telegram_id)

            if user:
                rank = user[0]
                name = user[1]
            else:
                rank = "Unknown"
                name = "Unknown"

            if status == "Approved":
                status_icon = "✅"

            elif status == "Rejected":
                status_icon = "❌"

            else:
                status_icon = "🟡"

            lines.append(
                f"{status_icon} #{report_id} "
                f"{rank} {name}\n"
                f"   Platoon: {platoon}\n"
                f"   Reason: {reason}\n"
                f"   Remarks: {remarks}\n"
                f"   Time: {report_time}\n"
                f"   Status: {status}\n"
            )

        text = "\n".join(lines)

    keyboard = [
        [
            InlineKeyboardButton(
                "🔄 Refresh",
                callback_data="admin_reports"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="admin_back"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# ATTENDANCE
# =========================================================

async def attendance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    attendance_data = get_attendance_today()

    lines = [
        "📊 TODAY'S ATTENDANCE\n"
    ]

    if not attendance_data:

        lines.append(
            "No registered personnel found."
        )

    else:

        for person in attendance_data:

            rank = person["rank"]
            name = person["name"]
            platoon = person["platoon"]
            status = person["status"]

            if status == "Approved":
                icon = "❌"

            elif status == "Pending":
                icon = "🟡"

            elif status == "Rejected":
                icon = "❌"

            else:
                icon = "✅"

            lines.append(
                f"{icon} {rank} {name}"
                f" — {platoon}\n"
            )

    lines.append(
        "\nLegend:\n"
        "❌ Reported sick\n"
        "✅ Present / did not report sick\n"
        "🟡 Sick report pending"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🔄 Refresh",
                callback_data="admin_attendance"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="admin_back"
            )
        ]
    ]

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# REGISTERED USERS
# =========================================================

async def registered_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    users = get_all_users()

    lines = [
        "👥 REGISTERED USERS\n"
    ]

    if not users:

        lines.append(
            "No users are registered."
        )

    else:

        for telegram_id, rank, full_name in users:

            lines.append(
                f"• {rank} {full_name}"
            )

    keyboard = [
        [
            InlineKeyboardButton(
                "🔄 Refresh",
                callback_data="admin_users"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="admin_back"
            )
        ]
    ]

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# BACK TO ADMIN MENU
# =========================================================

async def admin_back(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "👤 Commander Management",
                callback_data="admin_commanders"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 View Reports",
                callback_data="admin_reports"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Attendance",
                callback_data="admin_attendance"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Registered Users",
                callback_data="admin_users"
            )
        ]
    ]

    await query.edit_message_text(
        "⚙️ COMPANY ADMIN PANEL\n\n"
        "Please select an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def get_user_safe(telegram_id):

    from database import get_user

    return get_user(telegram_id)