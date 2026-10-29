"""
Risk Haritası Modülü — Sınıf risk faktörü yönetimi
Özel Eğitim ve Rehberlik Hizmetleri Genel Müdürlüğü S.İ.4.a formatı
"""
import sqlite3
import sys
import os
from config import DATABASE_PATH

# ─── 35 Risk Faktörü ───────────────────────────────────────────────────────────
RISK_FACTORS = [
    # Aile Yapısı (1-14)
    {"id": 1,  "label": "Anne en fazla ilkokul mezunu",              "category": "Aile Yapısı",    "teacher_only": True},
    {"id": 2,  "label": "Baba en fazla ilkokul mezunu",              "category": "Aile Yapısı",    "teacher_only": True},
    {"id": 3,  "label": "Tek çocuk olan",                            "category": "Aile Yapısı",    "teacher_only": False},
    {"id": 4,  "label": "5 ve üstü kardeşi olan",                   "category": "Aile Yapısı",    "teacher_only": False},
    {"id": 5,  "label": "Anne ve babası ayrı yaşayan",               "category": "Aile Yapısı",    "teacher_only": False},
    {"id": 6,  "label": "Anne ve babası boşanmış olan",              "category": "Aile Yapısı",    "teacher_only": False},
    {"id": 7,  "label": "Yalnızca annesi ile yaşayan",               "category": "Aile Yapısı",    "teacher_only": False},
    {"id": 8,  "label": "Yalnızca babası ile yaşayan",               "category": "Aile Yapısı",    "teacher_only": False},
    {"id": 9,  "label": "Annesi hayatta olmayan",                    "category": "Aile Yapısı",    "teacher_only": True},
    {"id": 10, "label": "Babası hayatta olmayan",                    "category": "Aile Yapısı",    "teacher_only": True},
    {"id": 11, "label": "Anne ve babası hayatta olmayan",            "category": "Aile Yapısı",    "teacher_only": True},
    {"id": 12, "label": "Şehit Çocuğu",                             "category": "Aile Yapısı",    "teacher_only": True},
    {"id": 13, "label": "Yalnızca büyükanne/büyükbabasıyla yaşayan","category": "Aile Yapısı",    "teacher_only": True},
    {"id": 14, "label": "Yalnızca diğer akrabalarıyla yaşayan",     "category": "Aile Yapısı",    "teacher_only": True},
    # Özel Durum (15-17)
    {"id": 15, "label": "Koruyucu aile gözetiminde olan",            "category": "Özel Durum",     "teacher_only": True},
    {"id": 16, "label": "Sevgi Evlerinde kalan",                     "category": "Özel Durum",     "teacher_only": True},
    {"id": 17, "label": "Sosyal Hizmetler / Çocuk Esirgeme Kurumu", "category": "Özel Durum",     "teacher_only": True},
    # Aile Sağlığı / Sosyal Risk (18-23)
    {"id": 18, "label": "Ailesinde süreğen hastalığı olan",         "category": "Aile Sağlığı",   "teacher_only": True},
    {"id": 19, "label": "Ailesinde ruhsal hastalığı olan",          "category": "Aile Sağlığı",   "teacher_only": True},
    {"id": 20, "label": "Ailesinde bağımlı bireyler bulunan (alkol/madde)", "category": "Aile Sağlığı", "teacher_only": True},
    {"id": 21, "label": "Ailesinde cezai hükmü bulunan",            "category": "Aile Sağlığı",   "teacher_only": True},
    {"id": 22, "label": "Ailesi mevsimlik işçi olan",               "category": "Aile Sağlığı",   "teacher_only": True},
    {"id": 23, "label": "Aile içi şiddete maruz kalan",             "category": "Aile Sağlığı",   "teacher_only": True},
    # Öğrenci Durumu (24-35)
    {"id": 24, "label": "Özel Yetenekli tanısı olan",               "category": "Öğrenci Durumu", "teacher_only": True},
    {"id": 25, "label": "Yetersizlik alanında özel eğitim raporu olan", "category": "Öğrenci Durumu", "teacher_only": True},
    {"id": 26, "label": "Süreğen hastalığı olan",                   "category": "Öğrenci Durumu", "teacher_only": True},
    {"id": 27, "label": "Ruhsal hastalığı olan",                    "category": "Öğrenci Durumu", "teacher_only": True},
    {"id": 28, "label": "Danışmanlık Tedbir Kararı Olan",           "category": "Öğrenci Durumu", "teacher_only": True},
    {"id": 29, "label": "Eğitim Tedbir Kararı Olan",               "category": "Öğrenci Durumu", "teacher_only": True},
    {"id": 30, "label": "Maddi Sıkıntı Yaşayan",                   "category": "Öğrenci Durumu", "teacher_only": True},
    {"id": 31, "label": "Sürekli Devamsız olan",                    "category": "Öğrenci Durumu", "teacher_only": False},
    {"id": 32, "label": "Bir işte çalışan",                         "category": "Öğrenci Durumu", "teacher_only": False},
    {"id": 33, "label": "Akademik Başarısı Düşük",                  "category": "Öğrenci Durumu", "teacher_only": False},
    {"id": 34, "label": "Riskli akran grubuna dahil olan",          "category": "Öğrenci Durumu", "teacher_only": True},
    {"id": 35, "label": "Diğer",                                    "category": "Öğrenci Durumu", "teacher_only": False},
]

FACTOR_DICT = {f["id"]: f for f in RISK_FACTORS}
STUDENT_VISIBLE_IDS = [f["id"] for f in RISK_FACTORS if not f["teacher_only"]]

# Öğrenciye sorulacak sorular (dolaylı, pedagojik dil)
STUDENT_SURVEY_QUESTIONS = [
    {"factor_id": 3,  "question": "Ailende kaç kardeşin var?",
     "type": "select",
     "options": ["Tek çocuğum (kardeşim yok)", "1-2 kardeşim var", "3-4 kardeşim var", "5 veya daha fazla kardeşim var"],
     "map": {0: 3, 3: 4}},  # Tek çocuk → #3, 5+ → #4
    {"factor_id": 7,  "question": "Şu an evde kimlerle yaşıyorsun?",
     "type": "select",
     "options": ["Annem ve babamla birlikte", "Yalnızca annemle", "Yalnızca babamla",
                 "Büyükanne/büyükbabamla", "Diğer akrabalarımla"],
     "map": {1: 7, 2: 8, 3: 13, 4: 14}},
    {"factor_id": 31, "question": "Bu dönem kaç gün okula gidemedin? (hastalık, zorunluluk vb.)",
     "type": "select",
     "options": ["Hiç devamsızlığım yok", "1-3 gün", "4-9 gün", "10 gün ve üzeri"],
     "map": {3: 31}},  # 10+ gün → devamsız
    {"factor_id": 32, "question": "Okul dışında bir işte ya da tezgâhta çalışıyor musun?",
     "type": "yesno", "yes_factor": 32},
    {"factor_id": 33, "question": "Derslerinizi yetişirmekte ya da anlamakta ciddi zorluk çekiyor musun?",
     "type": "yesno", "yes_factor": 33},
    {"factor_id": 35, "question": "Paylaşmak istediğin başka bir durum var mı? (İsteğe bağlı)",
     "type": "text"},
]


def init_risk_table():
    """Risk haritası tablosunu oluştur."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS student_risk_factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            factor_id INTEGER NOT NULL,
            source TEXT DEFAULT 'teacher',   -- 'teacher' veya 'student'
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            UNIQUE (student_id, factor_id)
        )
    """)
    conn.commit()
    conn.close()


def set_risk_factor(student_id: int, factor_id: int, active: bool, source: str = "teacher", note: str = ""):
    """Bir öğrencinin risk faktörünü ayarla (ekle/kaldır)."""
    init_risk_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    if active:
        c.execute("""
            INSERT OR REPLACE INTO student_risk_factors
                (student_id, factor_id, source, note, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (student_id, factor_id, source, note))
    else:
        c.execute("DELETE FROM student_risk_factors WHERE student_id = ? AND factor_id = ?",
                  (student_id, factor_id))
    conn.commit()
    conn.close()


def get_student_risk_factors(student_id: int) -> set:
    """Öğrencinin aktif risk faktörü ID'lerini döndür."""
    init_risk_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT factor_id FROM student_risk_factors WHERE student_id = ?", (student_id,))
    ids = {row[0] for row in c.fetchall()}
    conn.close()
    return ids


def get_all_risk_data() -> dict:
    """Tüm öğrencilerin risk verisi: {student_id: set(factor_ids)}"""
    init_risk_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT student_id, factor_id FROM student_risk_factors")
    data = {}
    for row in c.fetchall():
        data.setdefault(row[0], set()).add(row[1])
    conn.close()
    return data


def get_risk_summary() -> dict:
    """Her faktör için kaç öğrenci var, sıralı özet."""
    init_risk_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT factor_id, COUNT(*) as cnt
        FROM student_risk_factors
        GROUP BY factor_id
        ORDER BY cnt DESC
    """)
    return {row[0]: row[1] for row in c.fetchall()}


def save_student_survey(student_id: int, answers: dict):
    """Öğrenci anket yanıtlarını risk tablosuna kaydet."""
    for q in STUDENT_SURVEY_QUESTIONS:
        fid = q["factor_id"]
        ans = answers.get(fid)
        if ans is None:
            continue
        if q["type"] == "yesno":
            set_risk_factor(student_id, fid, ans is True, source="student")
        elif q["type"] == "select" and "map" in q:
            for opt_idx, mapped_fid in q["map"].items():
                set_risk_factor(student_id, mapped_fid, (ans == opt_idx), source="student")
        elif q["type"] == "text" and ans:
            set_risk_factor(student_id, fid, True, source="student", note=str(ans)[:200])
