import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("chat_logs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_reply TEXT NOT NULL,
            summary TEXT,
            actions TEXT,
            intent TEXT,
            assigned_team TEXT,
            assigned_agent TEXT,
            emotions TEXT,
            tags TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_chat_log(user_input, ai_response, summary, actions,
                  intent=None, assigned_team=None, assigned_agent=None,
                  emotions=None, tags=None):
    conn = sqlite3.connect("chat_logs.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_logs (
            user_message, ai_reply, summary, actions,
            intent, assigned_team, assigned_agent,
            emotions, tags, timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_input,
        ai_response,
        summary,
        str(actions),
        intent,
        assigned_team,
        assigned_agent,
        str(emotions),
        str(tags),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
