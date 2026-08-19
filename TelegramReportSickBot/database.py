import sqlite3
from datetime import datetime

DATABASE = "data/reportsick.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ==========================
    # USERS
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        telegram_id INTEGER PRIMARY KEY,

        rank TEXT NOT NULL,

        full_name TEXT NOT NULL,

        role TEXT DEFAULT 'Soldier',

        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        

    )
    """)

    # ==========================
    # COMMANDERS
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS platoons(

        platoon TEXT PRIMARY KEY,

        commander_id INTEGER,

        commander_rank TEXT,

        commander_name TEXT

    )
    """)

    # ==========================
    # REPORTS
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sick_reports(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id INTEGER NOT NULL,

        platoon TEXT NOT NULL,

        reason TEXT NOT NULL,

        remarks TEXT,

        status TEXT DEFAULT 'Pending',

        report_date TEXT,

        report_time TEXT,

        approved_by INTEGER,

        approved_at TEXT,
        
        rejection_reason TEXT

    )
    """)

    conn.commit()
    conn.close()


# ==========================
# USER FUNCTIONS
# ==========================

def add_user(telegram_id, rank, full_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO users(
        telegram_id,
        rank,
        full_name
    )

    VALUES(?,?,?)

    """, (

        telegram_id,
        rank,
        full_name

    ))

    conn.commit()
    conn.close()


def user_exists(telegram_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    SELECT telegram_id

    FROM users

    WHERE telegram_id=?

    """, (telegram_id,))

    result = cursor.fetchone()

    conn.close()

    return result is not None


def get_user(telegram_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    SELECT rank,
           full_name,
           role

    FROM users

    WHERE telegram_id=?

    """, (telegram_id,))

    user = cursor.fetchone()

    conn.close()

    return user


# ==========================
# COMMANDER FUNCTIONS
# ==========================

def set_commander(platoon, telegram_id, rank, name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    INSERT OR REPLACE INTO platoons(

        platoon,
        commander_id,
        commander_rank,
        commander_name

    )

    VALUES(?,?,?,?)

    """, (

        platoon,
        telegram_id,
        rank,
        name

    ))

    conn.commit()
    conn.close()


def get_commander(platoon):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    SELECT commander_id

    FROM platoons

    WHERE platoon=?

    """, (platoon,))

    commander = cursor.fetchone()

    conn.close()

    return commander


# ==========================
# REPORT FUNCTIONS
# ==========================
def add_report(telegram_id, platoon, reason, remarks):

    now = datetime.now()

    report_date = now.strftime("%d %b %Y")
    report_time = now.strftime("%I:%M %p")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sick_reports(
            telegram_id,
            platoon,
            reason,
            remarks,
            status,
            report_date,
            report_time
        )
        VALUES(?,?,?,?,?,?,?)
    """,(
        telegram_id,
        platoon,
        reason,
        remarks,
        "Pending",
        report_date,
        report_time
    ))

    report_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return report_id

def get_report(report_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM sick_reports
    WHERE id=?
    """, (report_id,))

    report = cursor.fetchone()

    conn.close()

    return report

def approve_report(report_id, commander_id):

    conn = get_connection()
    cursor = conn.cursor()

    approved_at = datetime.now().strftime("%d %b %Y %I:%M %p")

    cursor.execute("""
    UPDATE sick_reports
    SET
        status='Approved',
        approved_by=?,
        approved_at=?
    WHERE id=?
    """, (
        commander_id,
        approved_at,
        report_id
    ))

    conn.commit()
    conn.close()

def reject_report(
    report_id,
    commander_id,
    rejection_reason
):

    conn = get_connection()
    cursor = conn.cursor()

    approved_at = datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )

    cursor.execute("""
    UPDATE sick_reports
    SET
        status='Rejected',
        approved_by=?,
        approved_at=?,
        rejection_reason=?
    WHERE id=?
    """, (
        commander_id,
        approved_at,
        rejection_reason,
        report_id
    ))

    conn.commit()
    conn.close()


def get_all_users():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT telegram_id,
           rank,
           full_name
    FROM users
    ORDER BY rank, full_name
    """)

    users = cursor.fetchall()

    conn.close()

    return users


def assign_commander(platoon, telegram_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT rank,
           full_name
    FROM users
    WHERE telegram_id=?
    """, (telegram_id,))

    user = cursor.fetchone()

    if user is None:
        conn.close()
        return False

    rank = user[0]
    name = user[1]

    cursor.execute("""
    UPDATE users
    SET role='Commander'
    WHERE telegram_id=?
    """, (telegram_id,))

    cursor.execute("""
    INSERT OR REPLACE INTO platoons(
        platoon,
        commander_id,
        commander_rank,
        commander_name
    )
    VALUES(?,?,?,?)
    """, (
        platoon,
        telegram_id,
        rank,
        name
    ))

    conn.commit()
    conn.close()
    
    return True