"""
Öğrenci Katılım ve Aktivite Takip Modülü
8/B sınıfı öğrencilerinin sisteme giriş sayılarını, son giriş zamanlarını,
aktif kalma sürelerini, ŞÖK anketi ve Öğrenci Tanıma Formu tamamlama durumlarını takip eder.
"""

import sqlite3
import time
from datetime import datetime
from config import DATABASE_PATH
from core.student_profile import is_student_profile_complete

def init_activity_table():
    """Kullanıcı aktivite takip tablosunu hazırla."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER UNIQUE NOT NULL,
            login_count INTEGER DEFAULT 0,
            first_login TIMESTAMP,
            last_login TIMESTAMP,
            total_duration_seconds INTEGER DEFAULT 0,
            last_heartbeat REAL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)
    conn.commit()
    conn.close()

def record_login(student_id: int):
    """Öğrenci PIN ile başarıyla giriş yaptığında çağrılır."""
    if not student_id:
        return
    init_activity_table()
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    now_ts = time.time()
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_activity_log (student_id, login_count, first_login, last_login, total_duration_seconds, last_heartbeat)
        VALUES (?, 1, ?, ?, 0, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            login_count = login_count + 1,
            last_login = excluded.last_login,
            last_heartbeat = excluded.last_heartbeat
    """, (int(student_id), now_str, now_str, now_ts))
    conn.commit()
    conn.close()

def update_heartbeat(student_id: int):
    """
    Öğrenci her sayfa etkileşiminde çağrılır.
    Oturum süresini (duration) güvenli aralıklarla artırır.
    """
    if not student_id:
        return
    init_activity_table()
    now_ts = time.time()
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT last_heartbeat, total_duration_seconds FROM user_activity_log WHERE student_id = ?", (int(student_id),))
    row = c.fetchone()
    if row:
        last_hb = row[0]
        curr_dur = row[1] or 0
        if last_hb:
            elapsed = now_ts - float(last_hb)
            # Eğer son etkileşim 15 dakikadan kısaysa aktif süre olarak ekle
            if 0 < elapsed < 900:
                new_dur = curr_dur + int(elapsed)
            else:
                new_dur = curr_dur
        else:
            new_dur = curr_dur
            
        c.execute("""
            UPDATE user_activity_log
            SET total_duration_seconds = ?, last_heartbeat = ?
            WHERE student_id = ?
        """, (new_dur, now_ts, int(student_id)))
        conn.commit()
    else:
        record_login(student_id)
    conn.close()

def get_student_tracking_report() -> list[dict]:
    """
    Tüm 8/B sınıfı (29 öğrenci) için birleştirilmiş katılım, aktivite ve form durum raporunu döner.
    """
    init_activity_table()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Öğrenciler
    c.execute("SELECT id, school_no, name FROM students ORDER BY CAST(school_no AS INTEGER)")
    students = [dict(r) for r in c.fetchall()]

    # 2. ŞÖK anketleri
    c.execute("SELECT student_id, updated_at FROM sok_student_survey_detailed")
    sok_rows = {r["student_id"]: r["updated_at"] for r in c.fetchall()}

    # 3. Aktivite logları
    c.execute("SELECT * FROM user_activity_log")
    act_rows = {r["student_id"]: dict(r) for r in c.fetchall()}

    conn.close()

    report = []
    for idx, s in enumerate(students, 1):
        s_id = s["id"]
        act = act_rows.get(s_id, {})
        login_cnt = act.get("login_count", 0)
        last_log = act.get("last_login", "-")
        dur_sec = act.get("total_duration_seconds", 0) or 0
        dur_min = int(dur_sec // 60)
        if dur_sec > 0 and dur_min == 0:
            dur_str = f"{dur_sec} sn"
        elif dur_min > 0:
            dur_str = f"{dur_min} dk"
        else:
            dur_str = "-"

        # ŞÖK Form Durumu
        has_sok = s_id in sok_rows
        sok_time_raw = sok_rows.get(s_id)
        if has_sok:
            sok_status = "✅ Dolduruldu"
            try:
                # Format date if possible
                sok_date = str(sok_time_raw)[:16].replace("T", " ")
            except Exception:
                sok_date = str(sok_time_raw)
        else:
            sok_status = "⏳ Doldurmadı"
            sok_date = "-"

        # Öğrenci Tanıma Form Durumu
        is_prof_comp, missing = is_student_profile_complete(s_id)
        if is_prof_comp:
            prof_status = "✅ Tamamlandı"
            prof_detail = "Tüm bilgiler eksiksiz"
        else:
            prof_status = "⚠️ Eksik"
            prof_detail = ", ".join(missing) if missing else "Doldurulmamış"

        report.append({
            "sira": idx,
            "student_id": s_id,
            "school_no": str(s["school_no"]).strip(),
            "name": str(s["name"]).strip(),
            "login_count": login_cnt,
            "last_login": last_log,
            "duration_seconds": dur_sec,
            "duration_minutes": dur_min,
            "duration_str": dur_str,
            "has_sok": has_sok,
            "sok_status": sok_status,
            "sok_date": sok_date,
            "is_prof_complete": is_prof_comp,
            "prof_status": prof_status,
            "prof_detail": prof_detail
        })

    return report
