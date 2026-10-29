import sys, os
sys.path.insert(0, r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
os.chdir(r'C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu')
sys.stdout.reconfigure(encoding='utf-8')

from core.student_profile import (init_profile_table, save_profile, get_profile,
                                   profile_exists, profile_to_risk_factors, get_all_profiles)
init_profile_table()
print("init_profile_table: OK")

test_data = {
    "cinsiyet": "Erkek", "dogum_yeri": "Istanbul", "dogum_tarihi": "15.03.2011",
    "okul_adi": "Test Okul", "adres": "Test Mah", "cep_telefon": "05551234567",
    "evde_kimseler": ["Annem ve babam"],
    "anne_adi": "Ayse", "anne_sag": "Evet", "anne_egitim": "Ilkokul", "anne_meslek": "Ev hanimi",
    "baba_adi": "Mehmet", "baba_sag": "Evet", "baba_egitim": "Ortaokul", "baba_meslek": "Isci",
    "ebeveyn_birlikte": "Evet, birlikte yasiyorlar", "mevsimlik_isci": "Hayir",
    "kardes_sayisi": 3, "kacinci_cocuk": 1, "okula_giden_kardes": 2,
    "ilac_kullaniyor": "Hayir", "ilac_adi": "", "tani_var": "Hayir", "tani_aciklama": "",
    "ozel_egitim": "Hayir", "ailede_hastalik": "Hayir",
    "devamsizlik_gun": "1-3 gun", "ders_zorluk": "Bazi derslerde zorlaniyorum",
    "zor_dersler": ["Matematik"], "okul_degistirdi": "Hayir, bu okulda surekliyim",
    "arkadas_edinme": "Kolaylikla arkadas edinebiliyorum",
    "calisma_durumu": "Hayir", "ders_ortami": "Evet, rahat bir calisma yerim var",
    "internet_erisim": "Evet, evde var", "teknoloji_aleti": "Akilli telefon",
    "hobiler": ["Spor / Hareket"], "kurs_kulup": "Hayir", "kurs_adi": "",
    "genel_his": "Iyi, mutluyum", "zorlastiran_sey": "",
    "destek_istek": "Hayir, su an gerek duymuyorum", "onemli_olay": "Hayir",
    "veli_adi": "Mehmet", "veli_yakinligi": "Baba",
    "veli_telefon": "05559876543", "veli_egitim": "Ortaokul", "veli_meslek": "Isci",
}

save_profile(1, test_data)
print("save_profile: OK")

p = get_profile(1)
print(f"get_profile: OK — {len(p)} alan, cinsiyet={p.get('cinsiyet')}")
print(f"profile_exists: {profile_exists(1)}")

profile_to_risk_factors(1, test_data)
from core.risk_mapper import get_student_risk_factors
factors = get_student_risk_factors(1)
print(f"Risk faktörleri: {sorted(factors)}")

all_p = get_all_profiles()
print(f"get_all_profiles: {len(all_p)} profil")

from core.risk_pdf_exporter import export_risk_pdf
from core.risk_mapper import get_all_risk_data
import sqlite3
conn = sqlite3.connect('database/lgs_history.db')
students = [dict(zip(['id','school_no','name'], r)) for r in
            conn.execute('SELECT id, school_no, name FROM students').fetchall()]
conn.close()
out = export_risk_pdf(students, get_all_risk_data(), 'exports/8B_Sinif_Risk_Haritasi.docx', 'Test Okulu', '8/B')
print(f"risk_pdf_exporter: {os.path.getsize(out)} bytes")

print("\nTUM TESTLER BASARILI")
