import sqlite3
import time

def init_db():
    conn = sqlite3.connect("foup_log.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 uid TEXT, action TEXT, role TEXT, time TEXT)''')
    conn.commit()
    conn.close()

def insert_log(uid, action, role):
    init_db()
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("foup_log.db")
    c = conn.cursor()
    c.execute("INSERT INTO logs (uid, action, role, time) VALUES (?,?,?,?)",
              (uid, action, role, t))
    conn.commit()
    conn.close()