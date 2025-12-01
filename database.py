import sqlite3
import datetime

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level TEXT,
    score INTEGER,
    streak INTEGER,
    last_active TEXT
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT user_id, username, level, score, streak, last_active FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def add_user(user_id, username):
    if get_user(user_id) is None:
        now = datetime.date.today().isoformat()
        cursor.execute("INSERT INTO users (user_id, username, level, score, streak, last_active) VALUES (?, ?, ?, ?, ?, ?)", 
                       (user_id, username or '', "Beginner", 0, 0, now))
        conn.commit()

def update_user_field(user_id, field, value):
    cursor.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
    conn.commit()

def increment_score(user_id, delta=1):
    u = get_user(user_id)
    if u is None:
        return
    new_score = u[3] + delta
    cursor.execute("UPDATE users SET score=? WHERE user_id=?", (new_score, user_id))
    conn.commit()
    return new_score

def update_last_active_and_streak(user_id):
    u = get_user(user_id)
    if u is None:
        return
    last = u[5]
    today = datetime.date.today().isoformat()
    if last == today:
        return u[4]  # unchanged streak
    # if yesterday -> increment, else reset
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if last == yesterday:
        new_streak = u[4] + 1
    else:
        new_streak = 1
    cursor.execute("UPDATE users SET streak=?, last_active=? WHERE user_id=?", (new_streak, today, user_id))
    conn.commit()
    return new_streak

def set_level_by_score(user_id):
    u = get_user(user_id)
    if u is None:
        return "Beginner"
    score = u[3]
    if score < 10:
        level = "Beginner"
    elif score < 25:
        level = "Intermediate"
    else:
        level = "Advanced"
    cursor.execute("UPDATE users SET level=? WHERE user_id=?", (level, user_id))
    conn.commit()
    return level
