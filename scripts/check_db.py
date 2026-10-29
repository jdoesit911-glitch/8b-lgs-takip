import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database/lgs_history.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('TABLES:', [r[0] for r in c.fetchall()])
c.execute('SELECT id, name, pin FROM students ORDER BY CAST(school_no AS INTEGER) ASC, id ASC')
rows = c.fetchall()
print(f'STUDENTS ({len(rows)}):')
for r in rows:
    print(r)
conn.close()
