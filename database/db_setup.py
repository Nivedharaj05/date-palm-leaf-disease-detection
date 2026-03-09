import sqlite3

with sqlite3.connect("users.db") as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            name TEXT,
            email TEXT,
            phone TEXT,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
