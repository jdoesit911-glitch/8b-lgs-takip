import sys, os
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
os.chdir(r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
conn = sqlite3.connect('database/lgs_history.db')
c = conn.cursor()

# Öğrenci ID 1 = ORHAN EFE ÇELİKDEMİR'in test profilini sil
c.execute("DELETE FROM student_profile WHERE student_id = 1")
c.execute("DELETE FROM student_risk_factors WHERE student_id = 1 AND source = 'student'")

conn.commit()

# Doğrula
c.execute("SELECT COUNT(*) FROM student_profile")
print(f"student_profile kayit sayisi: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM student_risk_factors WHERE student_id = 1")
print(f"ID=1 risk faktoru: {c.fetchone()[0]}")

conn.close()
print("Test verisi temizlendi.")
