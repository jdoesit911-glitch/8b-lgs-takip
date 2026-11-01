"""
ŞÖK Öğrenci Veri Toplama ve Değerlendirme Modülü
Şube Öğretmenler Kurulu (ŞÖK) evrakları (Madde 11 Bireysel Tablo ve Sınıf Gözlem Formu)
için öğrencilere yöneltilebilecek veya öğretmen/admin tarafından girilebilecek
pedagojik veri toplama anketini ve veritabanı işlemlerini yönetir.
"""

import sqlite3
import pandas as pd
from config import DATABASE_PATH

def init_sok_survey_table():
    """sok_student_survey tablosunu oluştur."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sok_student_survey (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER UNIQUE NOT NULL,
            kisilik_ozellikleri TEXT,
            saglik_durumu       TEXT,
            beslenme_durumu     TEXT,
            sosyal_iliskiler    TEXT,
            calisma_ve_ekonomik TEXT,
            akademik_durum      TEXT,
            oneri_ve_tedbir     TEXT,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)
    conn.commit()
    conn.close()

def save_sok_survey(student_id: int, data: dict):
    """Öğrenciye ait ŞÖK anket / değerlendirme verisini kaydet veya güncelle."""
    init_sok_survey_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sok_student_survey (
            student_id, kisilik_ozellikleri, saglik_durumu, beslenme_durumu,
            sosyal_iliskiler, calisma_ve_ekonomik, akademik_durum, oneri_ve_tedbir,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id) DO UPDATE SET
            kisilik_ozellikleri = excluded.kisilik_ozellikleri,
            saglik_durumu       = excluded.saglik_durumu,
            beslenme_durumu     = excluded.beslenme_durumu,
            sosyal_iliskiler    = excluded.sosyal_iliskiler,
            calisma_ve_ekonomik = excluded.calisma_ve_ekonomik,
            akademik_durum      = excluded.akademik_durum,
            oneri_ve_tedbir     = excluded.oneri_ve_tedbir,
            updated_at          = CURRENT_TIMESTAMP
    """, (
        student_id,
        data.get("kisilik_ozellikleri", "").strip(),
        data.get("saglik_durumu", "").strip(),
        data.get("beslenme_durumu", "").strip(),
        data.get("sosyal_iliskiler", "").strip(),
        data.get("calisma_ve_ekonomik", "").strip(),
        data.get("akademik_durum", "").strip(),
        data.get("oneri_ve_tedbir", "").strip()
    ))
    conn.commit()
    conn.close()

def get_sok_survey(student_id: int) -> dict:
    """Öğrencinin kaydedilmiş ŞÖK anket verisini getir."""
    init_sok_survey_table()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM sok_student_survey WHERE student_id = ?", (student_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}

def get_all_sok_surveys(class_name: str = "8/B") -> list[dict]:
    """Sınıftaki tüm öğrencilerin ŞÖK anket verilerini getir."""
    init_sok_survey_table()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT s.id as student_id, s.school_no, s.name, s.class_name,
               sv.kisilik_ozellikleri, sv.saglik_durumu, sv.beslenme_durumu,
               sv.sosyal_iliskiler, sv.calisma_ve_ekonomik, sv.akademik_durum,
               sv.oneri_ve_tedbir, sv.updated_at
        FROM students s
        LEFT JOIN sok_student_survey sv ON s.id = sv.student_id
        WHERE s.class_name = ?
        ORDER BY CAST(s.school_no AS INTEGER) ASC
    """, (class_name,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_sok_surveys_df(class_name: str = "8/B") -> pd.DataFrame:
    """Excel çıktısı ve tablo görünümü için DataFrame üret."""
    records = get_all_sok_surveys(class_name)
    df_data = []
    for r in records:
        has_survey = bool(r.get("kisilik_ozellikleri") or r.get("saglik_durumu") or r.get("sosyal_iliskiler"))
        df_data.append({
            "Okul No": r["school_no"],
            "Adı Soyadı": r["name"],
            "Form Durumu": "Dolduruldu" if has_survey else "Bekliyor / Varsayılan",
            "Kişilik ve Karakter": r.get("kisilik_ozellikleri") or "-",
            "Sağlık Durumu": r.get("saglik_durumu") or "-",
            "Beslenme Alışkanlığı": r.get("beslenme_durumu") or "-",
            "Sosyal İlişkiler": r.get("sosyal_iliskiler") or "-",
            "Çalışma Ortamı & Kaynak": r.get("calisma_ve_ekonomik") or "-",
            "Akademik Başarı & Güçlük": r.get("akademik_durum") or "-",
            "Alınacak Önlem / Öneri": r.get("oneri_ve_tedbir") or "-",
            "Son Güncelleme": r.get("updated_at") or "-"
        })
    return pd.DataFrame(df_data)
