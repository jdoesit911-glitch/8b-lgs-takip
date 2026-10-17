import urllib.parse

YOUTUBE_RESOURCES = {
    "Matematik": {
        "temel": {
            "channel": "Partikül Matematik",
            "action_text": "Partikül Matematik ile Konu & Soru Çözümünü İzle",
            "search_term": "Partikül Matematik LGS Matematik",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Temel Kavramlar & Adım Adım Konu Anlatımı",
            "study_tip": "Videoyu durdurarak hocayla birlikte işlem yap; temel soru tiplerini not alıp kavrama testlerine geç."
        },
        "orta": {
            "channel": "İMT HOCA",
            "action_text": "İMT Hoca ile Yeni Nesil Matematik İzle",
            "search_term": "İMT Hoca LGS Matematik",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Yeni Nesile Geçiş & Soru Çözüm Taktikleri",
            "study_tip": "Yeni nesil sorularda verilenleri şemaya dökme ve matematiksel model kurma tekniklerine odaklan."
        },
        "iyi": {
            "channel": "Çopur Hoca",
            "action_text": "Çopur Hoca ile İleri Düzey Matematik İzle",
            "search_term": "Çopur Hoca LGS Matematik",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "İleri Düzey Soru Kalıpları & Derece Hedefi",
            "study_tip": "Süre tutarak soruyu hocadan önce çözmeye çalış; kestirme püf noktaları Hata Defterine ekle."
        }
    },
    "Türkçe": {
        "temel": {
            "channel": "Tonguç Akademi",
            "action_text": "Tonguç Akademi ile Türkçe İzle",
            "search_term": "Tonguç Akademi LGS Türkçe",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Konu Kavrama & Görsel Özetler",
            "study_tip": "Dil bilgisi ve metin türü kurallarını renkli kavram kartlarıyla not alarak çalış."
        },
        "orta": {
            "channel": "Hız Yayınları veya Ebubekir Hoca ile Türkçe",
            "action_text": "Hız Yayınları veya Ebubekir Hoca ile Türkçe Dinle",
            "search_term": "Hız Yayınları Ebubekir Hoca LGS Türkçe",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Paragraf Taktikleri & Çeldirici Eleme",
            "study_tip": "Paragraf sorularında hocanın anahtar kelimeleri ve metin kanıtlarını nasıl çizdiğine dikkat et."
        },
        "iyi": {
            "channel": "Hız Yayınları veya Ebubekir Hoca ile Türkçe",
            "action_text": "Hız Yayınları veya Ebubekir Hoca ile Türkçe Dinle",
            "search_term": "Hız Yayınları Ebubekir Hoca LGS Türkçe yeni nesil",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "MEB Çıkmış & Özgün Yeni Nesil Çözümleri",
            "study_tip": "İki güçlü çeldirici arasında kaldığında doğru seçeneğe götüren mantık ipuçlarını incele."
        }
    },
    "Fen Bilimleri": {
        "temel": {
            "channel": "Derslike",
            "action_text": "Derslike ile Fen Bilimleri İzle",
            "search_term": "Derslike LGS Fen Bilimleri",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Görsel ve 3D Animasyonlu Temel Anlatım",
            "study_tip": "Mevsimler ve İklim konularındaki 3D modellemeleri ve Güneş ışınlarının geliş açılarını dikkatle izle."
        },
        "orta": {
            "channel": "Mehmet Hoca ile Fen",
            "action_text": "Mehmet Hoca ile Fen Konu & Deneylerini İzle",
            "search_term": "Mehmet Hoca ile Fen LGS",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Kazanım Pekiştirme & Deney Analizi",
            "study_tip": "Deney sorularındaki bağımsız/bağımlı/kontrol değişkeni çözüm adımlarını birebir uygula."
        },
        "iyi": {
            "channel": "Hız Yayınları veya dnz hoca ile Fen",
            "action_text": "Hız Yayınları veya dnz hoca ile Fen İzle",
            "search_term": "dnz hoca Fen LGS Hız Yayınları",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "İleri Seviye Grafik & Deney Yorumlama",
            "study_tip": "Karmaşık grafik ve çok adımlı deney sorularında hızlı yorumlama tekniklerini not al."
        }
    },
    "İnkılap Tarihi": {
        "temel": {
            "channel": "Sosyal Kale",
            "action_text": "Sosyal Kale ile İnkılap Tarihi Dinle / İzle",
            "search_term": "Sosyal Kale LGS İnkılap Tarihi",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Kronolojik Hikayeleştirme & Kavram Haritaları",
            "study_tip": "Mustafa Kemal'in askerlik ve fikir hayatını harita ve kronoloji üzerinden hocayla takip et."
        },
        "orta": {
            "channel": "Sosyal Kale",
            "action_text": "Sosyal Kale ile İnkılap Tarihi Dinle / İzle",
            "search_term": "Sosyal Kale LGS İnkılap Tarihi soru çözümü",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Soru Çözüm Taktikleri & Neden-Sonuç İlişkisi",
            "study_tip": "'Yalnızca bu bilgiye göre' tarzı sorularda metin dışına çıkmama kuralını pekiştir."
        },
        "iyi": {
            "channel": "Buğra Hoca Sosyal Bilgiler Dersliği",
            "action_text": "Buğra Hoca ile İnkılap Tarihi Dinle / İzle",
            "search_term": "Buğra Hoca Sosyal Bilgiler Dersliği LGS İnkılap Tarihi",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "Kritik Çeldiriciler & MEB Tarzı Uç Sorular",
            "study_tip": "Tarihsel kavramların güncel yorumlarla ilişkilendirildiği zor soru tiplerine odaklan."
        }
    },
    "Din Kültürü": {
        "temel": {
            "channel": "Cebrail Hocam",
            "action_text": "Cebrail Hocam ile Din Kültürü Dinle / İzle",
            "search_term": "Cebrail Hocam LGS Din Kültürü",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Kaza-Kader Temel Kavramları & Ayet Mealleri",
            "study_tip": "Ömür, ecel, rızık, tevekkül ve yasalar konusunu hocanın kavram tablolarından tekrar et."
        },
        "orta": {
            "channel": "Cebrail Hocam",
            "action_text": "Cebrail Hocam ile Din Kültürü Dinle / İzle",
            "search_term": "Cebrail Hocam LGS Din Kültürü soru çözümü",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Ayet Yorumlama & MEB Örnek Soruları",
            "study_tip": "Ayet-el Kürsi ana fikri ve evrensel yasalarla ilgili soru kalıplarını videoyla paralel çöz."
        },
        "iyi": {
            "channel": "Cebrail Hocam",
            "action_text": "Cebrail Hocam ile Din Kültürü Dinle / İzle",
            "search_term": "Cebrail Hocam LGS Din Kültürü deneme",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "10'da 10 Hedefi & Dikkat/Çeldirici Analizi",
            "study_tip": "Kelimelerin ince anlam farklarına dayalı soru kalıplarını yakalayarak full yapmayı hedefle."
        }
    },
    "İngilizce": {
        "temel": {
            "channel": "Tonguç Akademi",
            "action_text": "Tonguç Akademi ile İngilizce İzle",
            "search_term": "Tonguç Akademi LGS İngilizce",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Temel Kelimeler & Kalıp Cümleler",
            "study_tip": "Friendship ünitesi kelimelerini ve Türkçelerini sesli tekrar ederek kelime defterine geçir."
        },
        "orta": {
            "channel": "Dilek Demirel",
            "action_text": "Dilek Demirel ile İngilizce Dinle / İzle",
            "search_term": "Dilek Demirel LGS İngilizce",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Diyalog Tamamlama & Soru Çözüm Metotları",
            "study_tip": "Davet, kabul, ret ve mazeret cümlelerini diyalog içi bağlamıyla öğren."
        },
        "iyi": {
            "channel": "Ümitcan Hoca",
            "action_text": "Ümitcan Hoca ile İngilizce Dinle / İzle",
            "search_term": "Ümitcan Hoca LGS İngilizce",
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
    search_base = info.get("search_term", info["channel"] + " LGS " + sub_key)
    query_parts = [search_base]
    if target_topic and str(target_topic).strip():
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
        "channel": info["channel"],
        "action_text": info.get("action_text", f"{info['channel']} ile Dersi İzle"),
        "focus": info["focus"],
        "study_tip": info["study_tip"],
        "search_url": search_url,
        "search_query": query_str
    }
