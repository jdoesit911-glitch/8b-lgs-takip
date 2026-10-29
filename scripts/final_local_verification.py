import os
import sys
import sqlite3
import openpyxl
import docx
import win32com.client

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import DATABASE_PATH, EXPORTS_DIR

desktop_dir = r"C:\Users\ELRA\Desktop\8B sınıfı veriler"
karneler_dir = os.path.join(desktop_dir, "karneler")
brans_dir = os.path.join(desktop_dir, "brans_raporlari")
excel_file = os.path.join(desktop_dir, "8B_LGS_Takip_Sistemi.xlsx")
karneler_zip = os.path.join(desktop_dir, "8B_Tum_Karneler.zip")
brans_zip = os.path.join(desktop_dir, "8B_Tum_Brans_Ogretmen_Raporlari.zip")

print("=" * 70)
print("🎯 8/B LGS ANALİZ VE TAKİP SİSTEMİ - BİLGİSAYAR / DESKTOP DOĞRULAMA")
print("=" * 70)

# 1. Database Check
print("\n[1] VERİ TABANI KONTROLÜ (database/lgs_history.db):")
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute("SELECT id, name, exam_date, publisher FROM exams ORDER BY id ASC")
exams = c.fetchall()
print(f" ✓ Kayıtlı Deneme Sınavı Sayısı: {len(exams)}")
for e in exams:
    c.execute("SELECT count(*) FROM exam_results WHERE exam_id = ?", (e[0],))
    cnt = c.fetchone()[0]
    print(f"   • Sınav #{e[0]}: {e[1]} ({e[2]}) - {e[3]} -> {cnt} Öğrenci Sonucu")

c.execute("SELECT count(*) FROM students")
total_students = c.fetchone()[0]
c.execute("SELECT count(*) FROM students WHERE pin IS NOT NULL AND length(pin) = 4")
total_pins = c.fetchone()[0]
print(f" ✓ Toplam Kayıtlı Öğrenci (Sınıf Mevcudu): {total_students} Öğrenci")
print(f" ✓ 4 Haneli Giriş PIN Kodu Atanmış Öğrenci: {total_pins} / {total_students}")
conn.close()

# 2. Student Cards (.docx)
print(f"\n[2] BİREYSEL ÖĞRENCİ KARNELERİ ({karneler_dir}):")
k_files = [f for f in os.listdir(karneler_dir) if f.endswith(".docx") and not f.startswith("~$")]
print(f" ✓ Klasördeki Karne Sayısı: {len(k_files)} adet .docx dosyası")
assert len(k_files) == 29, f"Hata: 29 karne bekleniyordu, {len(k_files)} bulundu!"
print(f" ✓ Karneler ZIP Paketi: {karneler_zip} ({os.path.getsize(karneler_zip):,} bytes)")

# 3. Branch Reports (.docx)
print(f"\n[3] BRANŞ ÖĞRETMEN RAPORLARI ({brans_dir}):")
b_files = [
    "8B_TURKCE_Brans_Raporu.docx",
    "8B_MATEMATIK_Brans_Raporu.docx",
    "8B_FEN_BILIMLERI_Brans_Raporu.docx",
    "8B_INKILAP_TARIHI_Brans_Raporu.docx",
    "8B_DIN_KULTURU_Brans_Raporu.docx",
    "8B_INGILIZCE_Brans_Raporu.docx"
]

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
all_single = True
for bf in b_files:
    bp = os.path.join(brans_dir, bf)
    d = docx.Document(bp)
    sec = d.sections[0]
    w = round(sec.page_width.inches, 2)
    h = round(sec.page_height.inches, 2)
    
    # Word COM page check
    wdoc = word.Documents.Open(os.path.abspath(bp))
    pages = wdoc.ComputeStatistics(2)
    wdoc.Close(False)
    
    status = "✓ 1 SAYFA (GEÇTİ)" if pages == 1 else f"✗ {pages} SAYFA (UYARI!)"
    if pages != 1: all_single = False
    print(f"   • {bf:<35} -> {status} [{w} x {h} in Landscape]")

word.Quit()
print(f" ✓ Branş Raporları ZIP Paketi: {brans_zip} ({os.path.getsize(brans_zip):,} bytes)")
assert all_single, "Tüm branş raporları 1 sayfa olmalıdır!"

# 4. Master Excel Tracker
print(f"\n[4] MASTER EXCEL TAKİP SİSTEMİ ({excel_file}):")
wb = openpyxl.load_workbook(excel_file, data_only=True)
print(f" ✓ Dosya Boyutu: {os.path.getsize(excel_file):,} bytes")
print(f" ✓ Sayfa (Sheet) Listesi ({len(wb.sheetnames)} sayfa):")
for sname in wb.sheetnames:
    ws = wb[sname]
    print(f"   • Sheet: '{sname}' -> {ws.max_row} Satır x {ws.max_column} Sütun")

print("\n" + "=" * 70)
print("🏆 TÜM DOĞRULAMALAR %100 BAŞARIYLA GEÇTİ!")
print("=" * 70)
