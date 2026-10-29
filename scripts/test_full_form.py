import sys; sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')

# 1. Test student_profile modülü
from core.student_profile import (init_profile_table, save_profile, get_profile,
                                   profile_exists, profile_to_risk_factors, get_all_profiles)
init_profile_table()
print("✅ init_profile_table: OK")

# 2. Test kayıt — öğrenci ID 1 (ORHAN EFE ÇELİKDEMİR)
test_data = {
    "cinsiyet": "Erkek",
    "dogum_yeri": "İstanbul",
    "dogum_tarihi": "15.03.2011",
    "okul_adi": "Test Ortaokulu",
    "adres": "Test Mah. No:1",
    "cep_telefon": "05551234567",
    "evde_kimseler": ["Annem ve babam", "Abim / ablam / kardeşlerim"],
    "anne_adi": "Ayşe Test",
    "anne_sag": "Evet",
    "anne_egitim": "İlkokul",
    "anne_meslek": "Ev hanımı",
    "baba_adi": "Mehmet Test",
    "baba_sag": "Evet",
    "baba_egitim": "Ortaokul",
    "baba_meslek": "İşçi",
    "ebeveyn_birlikte": "Evet, birlikte yaşıyorlar",
    "mevsimlik_isci": "Hayır",
    "kardes_sayisi": 3,
    "kacinci_cocuk": 1,
    "okula_giden_kardes": 2,
    "ilac_kullaniyor": "Hayır",
    "ilac_adi": "",
    "tani_var": "Hayır",
    "tani_aciklama": "",
    "ozel_egitim": "Hayır",
    "ailede_hastalik": "Hayır",
    "devamsizlik_gun": "1–3 gün",
    "ders_zorluk": "Bazı derslerde zorlanıyorum",
    "zor_dersler": ["Matematik", "Fen Bilimleri"],
    "okul_degistirdi": "Hayır, bu okulda sürekliyim",
    "arkadas_edinme": "Kolaylıkla arkadaş edinebiliyorum",
    "calisma_durumu": "Hayır",
    "ders_ortami": "Evet, rahat bir çalışma yerim var",
    "internet_erisim": "Evet, evde var",
    "teknoloji_aleti": "Akıllı telefon",
    "hobiler": ["Spor / Hareket", "Teknoloji / Oyun"],
    "kurs_kulup": "Hayır",
    "kurs_adi": "",
    "genel_his": "😊 İyi, mutluyum",
    "zorlastiran_sey": "",
    "destek_istek": "Hayır, şu an gerek duymuyorum",
    "onemli_olay": "Hayır",
    "veli_adi": "Mehmet Test",
    "veli_yakinligi": "Baba",
    "veli_telefon": "05559876543",
    "veli_egitim": "Ortaokul",
    "veli_meslek": "İşçi",
}

save_profile(1, test_data)
print("✅ save_profile: OK")

profile = get_profile(1)
assert profile["cinsiyet"] == "Erkek"
assert profile["anne_egitim"] == "İlkokul"
print(f"✅ get_profile: OK — {len(profile)} alan")

exists = profile_exists(1)
assert exists
print("✅ profile_exists: OK")

# 3. Risk faktörü çıkarımı
profile_to_risk_factors(1, test_data)
print("✅ profile_to_risk_factors: OK")

from core.risk_mapper import get_student_risk_factors
factors = get_student_risk_factors(1)
print(f"✅ Otomatik risk faktörleri: {sorted(factors)}")
# Anne ilkokul mezunu → F1 beklenir
assert 1 in factors, f"F1 (Anne ilkokul) bekleniyor ama yok! factors={factors}"
print("✅ F1 (Anne ilkokul) doğrulandı")

# 4. get_all_profiles
all_p = get_all_profiles()
print(f"✅ get_all_profiles: {len(all_p)} profil")

# 5. risk_pdf_exporter
from core.risk_pdf_exporter import export_risk_pdf
from core.risk_mapper import get_all_risk_data
import sqlite3
conn = sqlite3.connect('database/lgs_history.db')
students = [dict(zip(['id','school_no','name'], r)) for r in
            conn.execute('SELECT id, school_no, name FROM students ORDER BY CAST(school_no AS INTEGER) ASC, id ASC').fetchall()]
conn.close()
all_risk = get_all_risk_data()
out = export_risk_pdf(students, all_risk, 'exports/8B_Sinif_Risk_Haritasi.docx', 'Test Okulu', '8/B')
import os as _os
print(f"✅ risk_pdf_exporter: {_os.path.getsize(out)} bytes")

print("\n" + "="*50)
print("TÜM TESTLER BAŞARILI ✅")
