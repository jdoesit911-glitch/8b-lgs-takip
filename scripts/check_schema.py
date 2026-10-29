import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
conn = sqlite3.connect('database/lgs_history.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print([r[0] for r in c.fetchall()])
c.execute('PRAGMA table_info(students)')
print('students:', [r[1] for r in c.fetchall()])
conn.close()
