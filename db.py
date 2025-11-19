import os
import aiosqlite

DB_PATH = os.getenv('SQLITE_DB', 'bot_data.sqlite3')

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS rate_limits (
            chat_id TEXT PRIMARY KEY,
            tokens INTEGER,
            last_ts INTEGER
        )''')
        await db.commit()

async def save_message(chat_id, role, message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT INTO conversations (chat_id, role, message) VALUES (?, ?, ?)', (str(chat_id), role, message))
        await db.commit()

async def get_history(chat_id, limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT role, message, created_at FROM conversations WHERE chat_id=? ORDER BY id DESC LIMIT ?', (str(chat_id), limit))
        rows = await cur.fetchall()
        return rows[::-1]
