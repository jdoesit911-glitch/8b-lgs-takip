import sys, os
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
os.chdir(r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
conn = sqlite3.connect('database/lgs_history.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print('Tablolar:', tables)
for t in tables:
    c.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'  {t}: {c.fetchone()[0]} kayit')
print()
c.execute("SELECT COUNT(*) FROM students")
print('Ogrenci:', c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM student_profile")
print('Doldurulmus profil:', c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM student_risk_factors")
print('Risk faktoru kaydı:', c.fetchone()[0])
conn.close()
