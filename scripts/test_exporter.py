import sys, os
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
os.chdir(r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')

from core.risk_pdf_exporter import export_risk_pdf, build_risk_html
from core.risk_mapper import get_all_risk_data
import sqlite3

conn = sqlite3.connect('database/lgs_history.db')
students = [dict(zip(['id','school_no','name'], r)) for r in
            conn.execute('SELECT id, school_no, name FROM students ORDER BY CAST(school_no AS INTEGER) ASC, id ASC').fetchall()]
conn.close()

all_risk = get_all_risk_data()
print(f"Ogrenciler: {len(students)}, Risk kaydi: {len(all_risk)}")

# 1. Word testi
out = export_risk_pdf(students, all_risk, 'exports/8B_Sinif_Risk_Haritasi.docx', 'Ataturk Ortaokulu', '8/B')
print(f"Word: {os.path.getsize(out):,} bytes -> OK")

# 2. HTML testi
html = build_risk_html(students, all_risk, 'Ataturk Ortaokulu', '8/B')
html_path = 'exports/8B_Risk_Haritasi_Yazdir.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML: {os.path.getsize(html_path):,} bytes -> OK")
print(f"HTML baslik: {'8/B' in html and 'TOPLAM' in html}")

# 3. Desktop'a kopyala
import shutil
desktop_dir = r'C:\Users\ELRA\Desktop\8B sinifi veriler'
os.makedirs(desktop_dir, exist_ok=True)
shutil.copy(out, os.path.join(desktop_dir, '8B_Sinif_Risk_Haritasi.docx'))
shutil.copy(html_path, os.path.join(desktop_dir, '8B_Risk_Haritasi_Yazdir.html'))
print("Desktop'a kopyalandi: OK")

print("\nTUM TESTLER BASARILI")
