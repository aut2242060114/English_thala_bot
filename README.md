English THALA Bot - Advanced Telegram English Tutor Bot

Files included:
- bot.py               : main telegram bot (uses polling + APScheduler)
- database.py          : sqlite helper to store users, score, level, streak
- grammar.json         : sample grammar questions
- vocabulary.json      : sample vocabulary entries
- puzzles.json         : sample puzzles
- lessons.json         : sample mini-lessons
- requirements.txt     : python deps
- Procfile             : start command for Railway

Quick start (Railway):
1. Upload the project or push to GitHub.
2. Create a Railway project (Python template) and add these files.
3. Add an environment variable: TELEGRAM_TOKEN with your BotFather token.
4. Set start command: python bot.py
5. Deploy

Note:
- The scheduler sends daily messages at 08:00 UTC. Change timezone or hour in bot.py if you want local time (Asia/Kolkata = UTC+5:30 -> schedule accordingly).
- Auto-sent quizzes currently do not persist 'pending answers' to DB; users can use /daily to receive a checkable quiz. If you want auto-sent quizzes to be checkable, I can add per-user pending-question storage in the DB.
