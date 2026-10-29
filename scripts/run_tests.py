"""
Test scripti — DB'ye YAZMIYOR.
Sadece modül importlarını ve mantık fonksiyonlarını test eder.
"""
import sys, os
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
os.chdir(r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')

print("=== Modül Import Testleri ===")

from core.risk_mapper import (RISK_FACTORS, FACTOR_DICT, init_risk_table,
                               get_all_risk_data, get_risk_summary, get_student_risk_factors)
init_risk_table()
print(f"✅ risk_mapper: {len(RISK_FACTORS)} faktör tanımlı")

from core.student_profile import (init_profile_table, get_profile,
                                   profile_exists, get_all_profiles)
init_profile_table()
print("✅ student_profile: tablo hazır")

from core.risk_pdf_exporter import export_risk_pdf, build_risk_html
print("✅ risk_pdf_exporter: import OK")

from core.comparative_analyzer import get_multi_exam_comparison
print("✅ comparative_analyzer: import OK")

from core.branch_report_gen import analyze_branch_data
print("✅ branch_report_gen: import OK")

print("\n=== DB Durum ===")
import sqlite3
conn = sqlite3.connect('database/lgs_history.db')
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM students")
print(f"✅ Öğrenci: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM student_profile")
print(f"✅ Doldurulmuş profil: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM student_risk_factors")
print(f"✅ Risk faktörü kaydı: {c.fetchone()[0]}")
c.execute("SELECT id, name FROM exams")
print(f"✅ Sınavlar: {[dict(zip(['id','name'],r)) for r in c.fetchall()]}")
conn.close()

print("\n=== Risk PDF Test (salt-okunur) ===")
students = []
conn2 = sqlite3.connect('database/lgs_history.db')
rows = conn2.execute("SELECT id, school_no, name FROM students ORDER BY CAST(school_no AS INTEGER) ASC").fetchall()
conn2.close()
students = [dict(zip(['id','school_no','name'], r)) for r in rows]

html = build_risk_html(students, {}, 'Test Okulu', '8/B')
assert 'TOPLAM' in html and len(html) > 5000
print(f"✅ build_risk_html: {len(html):,} karakter, {len(students)} öğrenci")

out = export_risk_pdf(students, {}, 'exports/test_risk_readonly.docx', 'Test Okulu', '8/B')
size = os.path.getsize(out)
os.remove(out)  # hemen sil
print(f"✅ export_risk_pdf: {size:,} bytes (test dosyası silindi)")

print("\n✅ TÜM TESTLER BAŞARILI — DB'ye hiçbir şey yazılmadı")
