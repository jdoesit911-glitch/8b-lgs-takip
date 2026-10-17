import urllib.parse

YOUTUBE_RESOURCES = {
    "Matematik": {
        "temel": {
            "channel": "Partikül Matematik",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Temel Kavramlar & Adım Adım Konu Anlatımı",
            "study_tip": "Videoyu durdurarak hocayla birlikte işlem yap; temel soru tiplerini not alıp kavrama testlerine geç."
        },
        "orta": {
            "channel": "İMT HOCA",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Yeni Nesile Geçiş & Soru Çözüm Taktikleri",
            "study_tip": "Yeni nesil sorularda verilenleri şemaya dökme ve matematiksel model kurma tekniklerine odaklan."
        },
        "iyi": {
            "channel": "Çopur Hoca",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "İleri Düzey Soru Kalıpları & Derece Hedefi",
            "study_tip": "Süre tutarak soruyu hocadan önce çözmeye çalış; kestirme püf noktaları Hata Defterine ekle."
        }
    },
    "Türkçe": {
        "temel": {
            "channel": "Tonguç Akademi",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Konu Kavrama & Görsel Özetler",
            "study_tip": "Dil bilgisi ve metin türü kurallarını renkli kavram kartlarıyla not alarak çalış."
        },
        "orta": {
            "channel": "Hız Yayınları - Ebubekir Hoca",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Paragraf Taktikleri & Çeldirici Eleme",
            "study_tip": "Paragraf sorularında hocanın anahtar kelimeleri ve metin kanıtlarını nasıl çizdiğine dikkat et."
        },
        "iyi": {
            "channel": "Hız Yayınları / Ebubekir Hoca",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "MEB Çıkmış & Özgün Yeni Nesil Çözümleri",
            "study_tip": "İki güçlü çeldirici arasında kaldığında doğru seçeneğe götüren mantık ipuçlarını incele."
        }
    },
    "Fen Bilimleri": {
        "temel": {
            "channel": "Derslike",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Görsel ve 3D Animasyonlu Temel Anlatım",
            "study_tip": "Mevsimler ve İklim konularındaki 3D modellemeleri ve Güneş ışınlarının geliş açılarını dikkatle izle."
        },
        "orta": {
            "channel": "Mehmet Hoca ile Fen",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Kazanım Pekiştirme & Deney Analizi",
            "study_tip": "Deney sorularındaki bağımsız/bağımlı/kontrol değişkeni çözüm adımlarını birebir uygula."
        },
        "iyi": {
            "channel": "Hız Yayınları / dnz hoca",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "İleri Seviye Grafik & Deney Yorumlama",
            "study_tip": "Karmaşık grafik ve çok adımlı deney sorularında hızlı yorumlama tekniklerini not al."
        }
    },
    "İnkılap Tarihi": {
        "temel": {
            "channel": "Sosyal Kale",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Kronolojik Hikayeleştirme & Kavram Haritaları",
            "study_tip": "Mustafa Kemal'in askerlik ve fikir hayatını harita ve kronoloji üzerinden hocayla takip et."
        },
        "orta": {
            "channel": "Sosyal Kale",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Soru Çözüm Taktikleri & Neden-Sonuç İlişkisi",
            "study_tip": "'Yalnızca bu bilgiye göre' tarzı sorularda metin dışına çıkmama kuralını pekiştir."
        },
        "iyi": {
            "channel": "Buğra Hoca Sosyal Bilgiler Dersliği",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "Kritik Çeldiriciler & MEB Tarzı Uç Sorular",
            "study_tip": "Tarihsel kavramların güncel yorumlarla ilişkilendirildiği zor soru tiplerine odaklan."
        }
    },
    "Din Kültürü": {
        "temel": {
            "channel": "Cebrail Hocam",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Kaza-Kader Temel Kavramları & Ayet Mealleri",
            "study_tip": "Ömür, ecel, rızık, tevekkül ve yasalar konusunu hocanın kavram tablolarından tekrar et."
        },
        "orta": {
            "channel": "Cebrail Hocam",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Ayet Yorumlama & MEB Örnek Soruları",
            "study_tip": "Ayet-el Kürsi ana fikri ve evrensel yasalarla ilgili soru kalıplarını videoyla paralel çöz."
        },
        "iyi": {
            "channel": "Cebrail Hocam",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "10'da 10 Hedefi & Dikkat/Çeldirici Analizi",
            "study_tip": "Kelimelerin ince anlam farklarına dayalı soru kalıplarını yakalayarak full yapmayı hedefle."
        }
    },
    "İngilizce": {
        "temel": {
            "channel": "Tonguç Akademi",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Temel Kelimeler & Kalıp Cümleler",
            "study_tip": "Friendship ünitesi kelimelerini ve Türkçelerini sesli tekrar ederek kelime defterine geçir."
        },
        "orta": {
            "channel": "Dilek Demirel",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Diyalog Tamamlama & Soru Çözüm Metotları",
            "study_tip": "Davet, kabul, ret ve mazeret cümlelerini diyalog içi bağlamıyla öğren."
        },
        "iyi": {
            "channel": "Ümitcan Hoca",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "Yeni Nesil Okuma Parçaları, Tablo & Grafik Yorumlama",
            "study_tip": "Afiş, davetiye ve soru kökündeki 'NOT / except' gibi olumsuzluk ifadelerine dikkat ederek hızlan."
        }
    }
}

def determine_level(subject_name, net):
    """
    Determines student level ('temel', 'orta', 'iyi') based on subject net score.
    20-question subjects (Mat, Fen, Türkçe):
      - < 8.0: temel
      - 8.0 - 14.99: orta
      - >= 15.0: iyi
    10-question subjects (İnkılap, Din, İngilizce):
      - < 5.0: temel
      - 5.0 - 7.99: orta
      - >= 8.0: iyi
    """
    sub_clean = subject_name.strip()
    if sub_clean in ["Matematik", "Fen Bilimleri", "Türkçe"]:
        if net < 8.0:
            return "temel"
        elif net < 15.0:
            return "orta"
        else:
            return "iyi"
    else:
        if net < 5.0:
            return "temel"
        elif net < 8.0:
            return "orta"
        else:
            return "iyi"

def get_youtube_advice(subject_name, net, target_topic=None):
    """
    Returns full recommendation object including channel, level, search url, and study tips.
    """
    sub_key = None
    for k in YOUTUBE_RESOURCES.keys():
        if k.lower() in subject_name.lower():
            sub_key = k
            break
            
    if not sub_key:
        sub_key = "Matematik"
        
    level = determine_level(sub_key, net)
    info = YOUTUBE_RESOURCES[sub_key][level]
    
    # Generate YouTube search link
    channel_name = info["channel"]
    query_parts = [channel_name, "LGS", sub_key]
    if target_topic and str(target_topic).strip():
        # Clean topic name
        clean_top = str(target_topic).split('(')[0].strip()
        query_parts.append(clean_top)
    else:
        query_parts.append("konu anlatımı soru çözümü")
        
    query_str = " ".join(query_parts)
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query_str)}"
    
    return {
        "subject": sub_key,
        "level": level,
        "level_name": info["level_name"],
        "badge_color": info["badge_color"],
        "channel": channel_name,
        "focus": info["focus"],
        "study_tip": info["study_tip"],
        "search_url": search_url,
        "search_query": query_str
    }
