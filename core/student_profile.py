"""
Öğrenci Profil Modülü — Öğrenci Tanıma Formu verilerini saklar ve
risk haritası faktörlerine otomatik olarak dönüştürür.
"""
import sqlite3
from config import DATABASE_PATH
from core.risk_mapper import set_risk_factor, init_risk_table
import json

def safe_parse_list(val):
    if not val:
        return []
    if isinstance(val, (list, tuple, set)):
        return list(val)
    if isinstance(val, str):
        s = val.strip()
        if not s or s == "[]":
            return []
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
            except Exception:
                pass
        return [x.strip() for x in s.split(",") if x.strip()]
    return [str(val)]

def safe_format_list(val, empty_str="-"):
    items = safe_parse_list(val)
    return ", ".join(items) if items else empty_str



# ─── Tablo Oluştur ─────────────────────────────────────────────────────────────
def init_profile_table():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS student_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER UNIQUE NOT NULL,

            -- Bölüm 1: Öğrenci Bilgileri
            cinsiyet          TEXT,
            dogum_yeri        TEXT,
            dogum_tarihi      TEXT,
            okul_adi          TEXT,
            adres             TEXT,
            cep_telefon       TEXT,

            -- Bölüm 2: Aile ve Ev Hayatı
            evde_kimseler     TEXT,   -- JSON listesi
            anne_adi          TEXT,
            anne_sag          TEXT,   -- 'Evet' / 'Hayır'
            anne_egitim       TEXT,
            anne_meslek       TEXT,
            baba_adi          TEXT,
            baba_sag          TEXT,
            baba_egitim       TEXT,
            baba_meslek       TEXT,
            ebeveyn_birlikte  TEXT,   -- 'Evet, birlikte' / 'Hayır, ayrı'
            mevsimlik_isci    TEXT,   -- 'Evet' / 'Hayır' / 'Bazen'

            -- Bölüm 3: Kardeşler
            kardes_sayisi     INTEGER,
            kacinci_cocuk     INTEGER,
            okula_giden_kardes INTEGER,

            -- Bölüm 4: Sağlık
            ilac_kullaniyor   TEXT,
            ilac_adi          TEXT,
            tani_var          TEXT,
            tani_aciklama     TEXT,
            ozel_egitim       TEXT,
            ailede_hastalik   TEXT,
            ailede_aciklama   TEXT,

            -- Bölüm 5: Okul Hayatı
            devamsizlik_gun   TEXT,   -- '0' / '1-3' / '4-9' / '10+'
            ders_zorluk       TEXT,
            zor_dersler       TEXT,   -- JSON listesi
            okul_degistirdi   TEXT,
            arkadas_edinme    TEXT,

            -- Bölüm 6: Günlük Hayat
            calisma_durumu    TEXT,
            ders_ortami       TEXT,
            internet_erisim   TEXT,
            teknoloji_aleti   TEXT,

            -- Bölüm 7: İlgi ve Hobiler
            hobiler           TEXT,   -- JSON listesi
            kurs_kulup        TEXT,
            kurs_adi          TEXT,
            kurs_brans        TEXT,
            akademik_destek   TEXT,   -- JSON listesi

            -- Bölüm 8: Kendini Anlat
            genel_his         TEXT,
            zorlastiran_sey   TEXT,
            destek_istek      TEXT,
            onemli_olay       TEXT,

            -- Bölüm 9: Veli Bilgileri
            veli_adi          TEXT,
            veli_yakinligi    TEXT,
            veli_telefon      TEXT,
            veli_egitim       TEXT,
            veli_meslek       TEXT,

            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)
    conn.commit()
    conn.close()


# ─── Profil Kaydet ─────────────────────────────────────────────────────────────
def save_profile(student_id: int, data: dict):
    """Form verilerini student_profile tablosuna kaydet."""
    init_profile_table()
    import json

    def jl(val):
        """Liste değerini JSON string'e çevir."""
        if isinstance(val, list):
            return json.dumps(val, ensure_ascii=False)
        return val or ""

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO student_profile (
            student_id, cinsiyet, dogum_yeri, dogum_tarihi, okul_adi, adres, cep_telefon,
            evde_kimseler, anne_adi, anne_sag, anne_egitim, anne_meslek,
            baba_adi, baba_sag, baba_egitim, baba_meslek,
            ebeveyn_birlikte, mevsimlik_isci,
            kardes_sayisi, kacinci_cocuk, okula_giden_kardes,
            ilac_kullaniyor, ilac_adi, tani_var, tani_aciklama, ozel_egitim, ailede_hastalik, ailede_aciklama,
            devamsizlik_gun, ders_zorluk, zor_dersler, okul_degistirdi, arkadas_edinme,
            calisma_durumu, ders_ortami, internet_erisim, teknoloji_aleti,
            hobiler, kurs_kulup, kurs_adi, kurs_brans, akademik_destek,
            genel_his, zorlastiran_sey, destek_istek, onemli_olay,
            veli_adi, veli_yakinligi, veli_telefon, veli_egitim, veli_meslek
        ) VALUES (
            ?,?,?,?,?,?,?,
            ?,?,?,?,?,
            ?,?,?,?,
            ?,?,
            ?,?,?,
            ?,?,?,?,?,?,?,
            ?,?,?,?,?,
            ?,?,?,?,
            ?,?,?,?,
            ?,
            ?,?,?,?,
            ?,?,?,?,?
        )
        ON CONFLICT(student_id) DO UPDATE SET
            cinsiyet=excluded.cinsiyet, dogum_yeri=excluded.dogum_yeri,
            dogum_tarihi=excluded.dogum_tarihi, okul_adi=excluded.okul_adi,
            adres=excluded.adres, cep_telefon=excluded.cep_telefon,
            evde_kimseler=excluded.evde_kimseler,
            anne_adi=excluded.anne_adi, anne_sag=excluded.anne_sag,
            anne_egitim=excluded.anne_egitim, anne_meslek=excluded.anne_meslek,
            baba_adi=excluded.baba_adi, baba_sag=excluded.baba_sag,
            baba_egitim=excluded.baba_egitim, baba_meslek=excluded.baba_meslek,
            ebeveyn_birlikte=excluded.ebeveyn_birlikte,
            mevsimlik_isci=excluded.mevsimlik_isci,
            kardes_sayisi=excluded.kardes_sayisi,
            kacinci_cocuk=excluded.kacinci_cocuk,
            okula_giden_kardes=excluded.okula_giden_kardes,
            ilac_kullaniyor=excluded.ilac_kullaniyor, ilac_adi=excluded.ilac_adi,
            tani_var=excluded.tani_var, tani_aciklama=excluded.tani_aciklama,
            ozel_egitim=excluded.ozel_egitim, ailede_hastalik=excluded.ailede_hastalik, ailede_aciklama=excluded.ailede_aciklama,
            devamsizlik_gun=excluded.devamsizlik_gun, ders_zorluk=excluded.ders_zorluk,
            zor_dersler=excluded.zor_dersler, okul_degistirdi=excluded.okul_degistirdi,
            arkadas_edinme=excluded.arkadas_edinme,
            calisma_durumu=excluded.calisma_durumu, ders_ortami=excluded.ders_ortami,
            internet_erisim=excluded.internet_erisim, teknoloji_aleti=excluded.teknoloji_aleti,
            hobiler=excluded.hobiler, kurs_kulup=excluded.kurs_kulup, kurs_adi=excluded.kurs_adi,
            kurs_brans=excluded.kurs_brans, akademik_destek=excluded.akademik_destek,
            genel_his=excluded.genel_his, zorlastiran_sey=excluded.zorlastiran_sey,
            destek_istek=excluded.destek_istek, onemli_olay=excluded.onemli_olay,
            veli_adi=excluded.veli_adi, veli_yakinligi=excluded.veli_yakinligi,
            veli_telefon=excluded.veli_telefon, veli_egitim=excluded.veli_egitim,
            veli_meslek=excluded.veli_meslek,
            updated_at=CURRENT_TIMESTAMP
    """, (
        student_id,
        data.get("cinsiyet", ""),
        data.get("dogum_yeri", ""),
        data.get("dogum_tarihi", ""),
        data.get("okul_adi", ""),
        data.get("adres", ""),
        data.get("cep_telefon", ""),
        jl(data.get("evde_kimseler", [])),
        data.get("anne_adi", ""),
        data.get("anne_sag", ""),
        data.get("anne_egitim", ""),
        data.get("anne_meslek", ""),
        data.get("baba_adi", ""),
        data.get("baba_sag", ""),
        data.get("baba_egitim", ""),
        data.get("baba_meslek", ""),
        data.get("ebeveyn_birlikte", ""),
        data.get("mevsimlik_isci", ""),
        data.get("kardes_sayisi", None),
        data.get("kacinci_cocuk", None),
        data.get("okula_giden_kardes", None),
        data.get("ilac_kullaniyor", ""),
        data.get("ilac_adi", ""),
        data.get("tani_var", ""),
        data.get("tani_aciklama", ""),
        data.get("ozel_egitim", ""),
        data.get("ailede_hastalik", ""),
        data.get("ailede_aciklama", ""),
        data.get("devamsizlik_gun", ""),
        data.get("ders_zorluk", ""),
        jl(data.get("zor_dersler", [])),
        data.get("okul_degistirdi", ""),
        data.get("arkadas_edinme", ""),
        data.get("calisma_durumu", ""),
        data.get("ders_ortami", ""),
        data.get("internet_erisim", ""),
        data.get("teknoloji_aleti", ""),
        jl(data.get("hobiler", [])),
        data.get("kurs_kulup", ""),
        data.get("kurs_adi", ""),
        data.get("kurs_brans", ""),
        jl(data.get("akademik_destek", [])),
        data.get("genel_his", ""),
        data.get("zorlastiran_sey", ""),
        data.get("destek_istek", ""),
        data.get("onemli_olay", ""),
        data.get("veli_adi", ""),
        data.get("veli_yakinligi", ""),
        data.get("veli_telefon", ""),
        data.get("veli_egitim", ""),
        data.get("veli_meslek", ""),
    ))
    conn.commit()
    conn.close()


def get_profile(student_id: int) -> dict:
    """Öğrencinin kaydedilmiş profilini döndür."""
    init_profile_table()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM student_profile WHERE student_id = ?", (student_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}


def profile_exists(student_id: int) -> bool:
    """Öğrencinin profil formu doldurulmuş mu?"""
    init_profile_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM student_profile WHERE student_id = ?", (student_id,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def get_all_profiles() -> list:
    """Tüm öğrenci profillerini döndür (admin görünümü için)."""
    init_profile_table()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT p.*, s.name, s.school_no
        FROM student_profile p
        JOIN students s ON p.student_id = s.id
        ORDER BY CAST(s.school_no AS INTEGER) ASC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ─── Risk Haritası Otomatik Çıkarım ───────────────────────────────────────────
def profile_to_risk_factors(student_id: int, data: dict):
    """
    Form verilerinden risk haritası faktörlerini otomatik çıkar
    ve student_risk_factors tablosuna kaydet.
    Risk Haritası Örtüşme Tablosuna göre:
    """
    init_risk_table()

    def sf(factor_id, active, note=""):
        set_risk_factor(student_id, factor_id, active, source="student", note=note)

    # ── Bölüm 2: Aile Yapısı ──────────────────────────────────
    # F1: Anne en fazla ilkokul mezunu
    sf(1, data.get("anne_egitim") in ("Okuryazar değil", "İlkokul"))
    # F2: Baba en fazla ilkokul mezunu
    sf(2, data.get("baba_egitim") in ("Okuryazar değil", "İlkokul"))

    evde_raw = data.get("evde_kimseler") or []
    if isinstance(evde_raw, str):
        import json
        try:
            evde = json.loads(evde_raw)
        except Exception:
            evde = [x.strip() for x in evde_raw.split(",") if x.strip()]
    elif isinstance(evde_raw, (list, tuple, set)):
        evde = list(evde_raw)
    else:
        evde = []

    anne_baba_birlikte = data.get("ebeveyn_birlikte", "")

    # F5: Anne ve babası ayrı yaşayan
    sf(5, anne_baba_birlikte == "Hayır, ayrı yaşıyorlar")

    # F7: Yalnızca annesiyle yaşayan
    sf(7, "Yalnızca annem" in evde and anne_baba_birlikte != "Evet, birlikte yaşıyorlar")
    # F8: Yalnızca babasıyla yaşayan
    sf(8, "Yalnızca babam" in evde and anne_baba_birlikte != "Evet, birlikte yaşıyorlar")
    # F9: Annesi hayatta olmayan
    sf(9, data.get("anne_sag") == "Hayır")
    # F10: Babası hayatta olmayan
    sf(10, data.get("baba_sag") == "Hayır")
    # F11: Anne ve babası hayatta olmayan
    sf(11, data.get("anne_sag") == "Hayır" and data.get("baba_sag") == "Hayır")
    # F13: Büyükanne/büyükbabasıyla yaşayan
    sf(13, "Büyükanne / büyükbabam" in evde)
    # F14: Yalnızca diğer akrabalarıyla yaşayan
    sf(14, "Diğer akrabalarım (hala, amca, dayı vb.)" in evde
       and "Annem ve babam" not in evde
       and "Yalnızca annem" not in evde
       and "Yalnızca babam" not in evde)

    # ── Bölüm 2.5: Mevsimlik İşçilik ─────────────────────────
    # F22: Ailesi mevsimlik işçi olan
    sf(22, data.get("mevsimlik_isci") in ("Evet", "Bazen"))

    # ── Bölüm 3: Kardeşler ────────────────────────────────────
    kardes = data.get("kardes_sayisi")
    if kardes is not None:
        try:
            kardes = int(kardes)
            # F3: Tek çocuk
            sf(3, kardes == 0)
            # F4: 5 ve üstü kardeş
            sf(4, kardes >= 5)
        except (ValueError, TypeError):
            pass

    # ── Bölüm 4: Sağlık ───────────────────────────────────────
    # F26: Süreğen hastalığı olan (ilaç kullanımı veya tanı)
    _saglik_notlari = []
    if data.get("tani_aciklama"):
        _saglik_notlari.append(f"Tanı: {data['tani_aciklama']}")
    if data.get("ilac_adi"):
        _saglik_notlari.append(f"İlaç: {data['ilac_adi']}")
    sf(26, data.get("ilac_kullaniyor") == "Evet" or data.get("tani_var") == "Evet",
       note=" | ".join(_saglik_notlari))
    # F25: Yetersizlik alanında özel eğitim raporu
    ozel_egitim = data.get("ozel_egitim", "")
    sf(25, ozel_egitim in ("Evet, özel eğitim alıyorum", "Evet, kaynaştırma öğrencisiyim"))
    # F18: Ailesinde süreğen hastalığı olan
    sf(18, data.get("ailede_hastalik") == "Evet",
       note=data.get("ailede_aciklama", ""))

    # ── Bölüm 5: Okul Hayatı ──────────────────────────────────
    # F31: Sürekli devamsız olan
    sf(31, data.get("devamsizlik_gun") == "10 gün ve üzeri")
    # F33: Akademik başarısı düşük
    sf(33, data.get("ders_zorluk") == "Evet, çoğu derste ciddi zorluk çekiyorum")

    # ── Bölüm 6: Günlük Hayat ────────────────────────────────
    # F32: Bir işte çalışan
    sf(32, data.get("calisma_durumu") in (
        "Evet, hafta sonları yardım ediyorum",
        "Evet, hafta içi düzenli çalışıyorum"
    ))
    # F30: Maddi sıkıntı yaşayan (ortam yok + internet yok)
    maddi_ipucu = (
        data.get("ders_ortami") == "Hayır, genellikle çalışacak ortam bulamıyorum"
        and data.get("internet_erisim") == "Hayır, çoğu zaman erişemiyorum"
    )
    sf(30, maddi_ipucu)

    # ── Bölüm 8: Kendini Anlat ────────────────────────────────
    # F35: Diğer (özel risk veya rehberlik müdahalesi gerektiren durumlar)
    zorl = (data.get("zorlastiran_sey") or "").strip()
    onemli = (data.get("onemli_olay") or "").strip()

    # "yok", "yoktur", "hayır", "-" gibi cevaplar veya genel "ödev" risk faktörü sayılmaz
    _gecersiz = {"yok", "yok.", "yoktur", "yoktur.", "hayır", "hayir", "-", "none", "nan", "ödev", "odev"}
    zorl_risk = bool(zorl) and (zorl.lower().strip() not in _gecersiz)

    f35_notlar = []
    if zorl_risk:
        f35_notlar.append(f"Zorlayan: {zorl}")
    if onemli.startswith("Evet"):
        f35_notlar.append("Son 1-2 yılda derinden etkileyen önemli olay yaşandı")

    is_f35 = zorl_risk or onemli.startswith("Evet")
    sf(35, is_f35, note=" | ".join(f35_notlar)[:200] if is_f35 else "")


# ─── Profil Tamamlanma Kontrolü ────────────────────────────────────────────────
def is_student_profile_complete(student_id: int) -> tuple[bool, list[str]]:
    """
    Öğrencinin Öğrenci Tanıma Formunu eksiksiz ve geçerli doldurup doldurmadığını denetler.
    Dönen değer: (tamamlandi_mi: bool, eksik_alanlar: list[str])
    Eğer tüm zorunlu alanlar doluysa True döner.
    """
    init_profile_table()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM student_profile WHERE student_id = ?", (student_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return False, ["Form henüz hiç doldurulmamış"]

    p = dict(row)
    missing = []
    
    if not p.get("cinsiyet") or str(p.get("cinsiyet")).strip() == "":
        missing.append("Cinsiyet")
    if not p.get("dogum_tarihi") or str(p.get("dogum_tarihi")).strip() == "":
        missing.append("Doğum Tarihi")
    if not (p.get("anne_adi") or p.get("baba_adi")):
        missing.append("Anne veya Baba Adı")
    if not p.get("anne_sag") or str(p.get("anne_sag")).strip() == "":
        missing.append("Anne Sağ/Vefat Durumu")
    if not p.get("baba_sag") or str(p.get("baba_sag")).strip() == "":
        missing.append("Baba Sağ/Vefat Durumu")
    if not p.get("ders_ortami") or str(p.get("ders_ortami")).strip() == "":
        missing.append("Ders Çalışma Ortamı")
    if not p.get("genel_his") or str(p.get("genel_his")).strip() == "":
        missing.append("Genel Duygu/His Durumu")

    return (len(missing) == 0), missing
