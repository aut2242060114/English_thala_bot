import os
import json
import random
import logging
from telegram import Update, ParseMode
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)
from datetime import datetime
import database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN is missing! Set it in Render → Environment.")
    exit(1)


# --------------------------
# LOAD JSON DATA FILES
# --------------------------
def load_json(fname):
    with open(fname, "r", encoding="utf-8") as f:
        return json.load(f)

grammar = load_json("grammar.json")
vocab = load_json("vocabulary.json")
puzzles = load_json("puzzles.json")
lessons = load_json("lessons.json")


# --------------------------
# HELPER FUNCTIONS
# --------------------------
def choose_for_level(items, level):
    filtered = [i for i in items if i.get("level", level) == level]
    return random.choice(filtered if filtered else items)


def format_daily_payload(uid):
    user = database.get_user(uid)
    level = user[2] if user else "Beginner"

    g = choose_for_level(grammar, level)
    v = choose_for_level(vocab, level)
    p = choose_for_level(puzzles, level)
    l = choose_for_level(lessons, level)

    return {
        "text": (
            "🌅 *Good morning!* Here is your daily English practice:\n\n"
            f"📝 *Grammar:*\n{g['q']}\n\n"
            f"📚 *Vocabulary:*\nWord: *{v['word']}*\nMeaning: {v['meaning']}\nExample: {v['example']}\n\n"
            f"🧠 *Puzzle:*\n{p['q']}\n\n"
            f"📖 *Mini Lesson:*\n{l['text']}\n\n"
            "➡ Reply using this format:\n"
            "`B || Answer to puzzle`\n"
        ),
        "answers": {
            "grammar": g.get("answer"),
            "puzzle": p.get("answer")
        }
    }


# --------------------------
# COMMAND HANDLERS
# --------------------------
def start(update: Update, context: CallbackContext):
    uid = update.effective_chat.id
    username = update.effective_user.username or ""

    database.add_user(uid, username)

    update.message.reply_text(
        "🎓 *English THALA Bot Activated!*\n"
        "Use these commands:\n"
        "/daily – Get today's English tasks\n"
        "/score – Show your score\n"
        "/level – Show level\n"
        "/streak – Show your streak",
        parse_mode=ParseMode.MARKDOWN
    )


def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/daily – today's tasks\n"
        "/score – your score\n"
        "/level – your level\n"
        "/streak – your streak\n"
        "Format answer as: `B || puzzle answer`"
    )


def daily_cmd(update: Update, context: CallbackContext):
    uid = update.effective_chat.id
    database.add_user(uid, update.effective_user.username or "")

    payload = format_daily_payload(uid)

    context.user_data["pending"] = payload["answers"]

    update.message.reply_text(
        payload["text"],
        parse_mode=ParseMode.MARKDOWN
    )


def check_answer(update: Update, context: CallbackContext):
    if "pending" not in context.user_data:
        update.message.reply_text("No quiz found. Type /daily.")
        return

    uid = update.effective_chat.id
    text = update.message.text.strip()

    if "||" not in text:
        update.message.reply_text("Wrong format. Use: `B || answer`")
        return

    grammar_part, puzzle_part = [x.strip() for x in text.split("||", 1)]

    correct = context.user_data["pending"]
    gained = 0

    if grammar_part.lower() == str(correct["grammar"]).lower():
        gained += 1
    if puzzle_part.lower() == str(correct["puzzle"]).lower():
        gained += 1

    if gained > 0:
        database.increment_score(uid, gained)
        database.set_level_by_score(uid)

    streak = database.update_last_active_and_streak(uid)
    user = database.get_user(uid)

    update.message.reply_text(
        f"✅ Correct: {gained}\n"
        f"🏆 Score: {user[3]}\n"
        f"🎯 Level: {user[2]}\n"
        f"🔥 Streak: {streak} days"
    )

    context.user_data.pop("pending", None)


def score_cmd(update: Update, context: CallbackContext):
    user = database.get_user(update.effective_chat.id)
    if not user:
        update.message.reply_text("Type /start first.")
        return
    update.message.reply_text(f"🏆 Score: {user[3]}")


def level_cmd(update: Update, context: CallbackContext):
    user = database.get_user(update.effective_chat.id)
    if not user:
        update.message.reply_text("Type /start first.")
        return
    update.message.reply_text(f"🎯 Level: {user[2]}")


def streak_cmd(update: Update, context: CallbackContext):
    user = database.get_user(update.effective_chat.id)
    if not user:
        update.message.reply_text("Type /start first.")
        return
    update.message.reply_text(f"🔥 Streak: {user[4]} days")


# --------------------------
# MAIN BOT
# --------------------------
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("daily", daily_cmd))
    dp.add_handler(CommandHandler("score", score_cmd))
    dp.add_handler(CommandHandler("level", level_cmd))
    dp.add_handler(CommandHandler("streak", streak_cmd))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_answer))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
