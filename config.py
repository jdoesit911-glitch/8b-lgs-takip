import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "lgs_history.db")

# Cross-platform exports directory (local desktop fallback to internal exports)
LOCAL_DESKTOP = r"C:\Users\ELRA\Desktop\8B sınıfı veriler"
if os.path.exists(LOCAL_DESKTOP):
    EXPORTS_DIR = LOCAL_DESKTOP
else:
    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

os.makedirs(EXPORTS_DIR, exist_ok=True)

# LGS Subject Parameters
SUBJECTS = {
    "Türkçe": {"questions": 20, "weight": 4.0, "short": "tur"},
    "İnkılap Tarihi": {"questions": 10, "weight": 1.0, "short": "ink"},
    "Din Kültürü": {"questions": 10, "weight": 1.0, "short": "din"},
    "İngilizce": {"questions": 10, "weight": 1.0, "short": "ing"},
    "Matematik": {"questions": 20, "weight": 4.0, "short": "mat"},
    "Fen Bilimleri": {"questions": 20, "weight": 4.0, "short": "fen"},
}

TOTAL_QUESTIONS = 90
MAX_SCORE = 500.0

# Academic Performance Tiers
TIER_THRESHOLDS = [
    {"tier": "Tier 1: İleri Düzey (Şampiyonlar)", "min_net": 65.0, "max_net": 90.0, "color": "#1B4F72", "target_desc": "Fen Liseleri & Türkiye Derecesi"},
    {"tier": "Tier 2: Orta-Üst Düzey (Gelişim Liderleri)", "min_net": 40.0, "max_net": 64.99, "color": "#117864", "target_desc": "Nitelikli Anadolu Liseleri"},
    {"tier": "Tier 3: Gelişim Alanı (Hassas Müdahale)", "min_net": 25.0, "max_net": 39.99, "color": "#B7950B", "target_desc": "35-45 Net Bandına Geçiş"},
    {"tier": "Tier 4: Temel Destek (Bireysel Takviye)", "min_net": 0.0, "max_net": 24.99, "color": "#78281F", "target_desc": "Temel Kavramlar & Taktik Boş Bırakma"}
]

# Kazanım Priority Thresholds
KAZANIM_LEVELS = [
    {"code": "A - ACİL MÜDAHALE", "max_rate": 39.99, "bg_color": "#FADBD8", "text_color": "#900C3F", "rec": "5-8 soruluk tanı testi + 10 dk mikro anlatım"},
    {"code": "B - YÜKSEK ÖNCELİK", "max_rate": 59.99, "bg_color": "#FCF3CF", "text_color": "#7D6608", "rec": "Soru kökü analizi + yanlış defteri tekrarı"},
    {"code": "C - GELİŞTİRİLEBİLİR", "max_rate": 79.99, "bg_color": "#D4EFDF", "text_color": "#145A32", "rec": "Pekiştirme testi + yeni nesil soru pratiği"},
    {"code": "D - GÜÇLÜ ALAN", "max_rate": 100.0, "bg_color": "#E8F8F5", "text_color": "#0E6655", "rec": "Aralıklı tekrar ile formu koruma"}
]
