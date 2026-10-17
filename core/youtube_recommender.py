import urllib.parse

YOUTUBE_RESOURCES = {
    "Matematik": {
        "temel": {
            "channel": "Partikül Matematik",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Temel Kavramlar & Adım Adım Konu Anlatımı",
            "study_tip": "Videoyu durdurarak hocayla birlikte işlem yap; temel soru tiplerini not alıp kavrama testlerine geç.",
            "options": [
                {
                    "name": "Partikül Matematik",
                    "action_text": "▶️ Partikül Matematik ile İzle",
                    "url": "https://www.youtube.com/results?search_query=Partik%C3%BCl+Matematik+8+s%C4%B1n%C4%B1f+LGS",
                    "theme": "primary"
                }
            ]
        },
        "orta": {
            "channel": "İMT Hoca",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Yeni Nesile Geçiş & Soru Çözüm Taktikleri",
            "study_tip": "Yeni nesil sorularda verilenleri şemaya dökme ve matematiksel model kurma tekniklerine odaklan.",
            "options": [
                {
                    "name": "İMT Hoca",
                    "action_text": "▶️ İMT Hoca ile İzle",
                    "url": "https://www.youtube.com/results?search_query=%C4%B0MT+Hoca+8+s%C4%B1n%C4%B1f+LGS+Matematik",
                    "theme": "orange"
                }
            ]
        },
        "iyi": {
            "channel": "Çopur Hoca",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "İleri Düzey Soru Kalıpları & Derece Hedefi",
            "study_tip": "Süre tutarak soruyu hocadan önce çözmeye çalış; kestirme püf noktaları Hata Defterine ekle.",
            "options": [
                {
                    "name": "Çopur Hoca",
                    "action_text": "▶️ Çopur Hoca ile İzle",
                    "url": "https://www.youtube.com/results?search_query=%C3%87opur+Hoca+8+s%C4%B1n%C4%B1f+LGS+Matematik",
                    "theme": "green"
                }
            ]
        }
    },
    "Türkçe": {
        "temel": {
            "channel": "Tonguç Akademi",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Konu Kavrama & Görsel Özetler",
            "study_tip": "Dil bilgisi ve metin türü kurallarını renkli kavram kartlarıyla not alarak çalış.",
            "options": [
                {
                    "name": "Tonguç Akademi",
                    "action_text": "▶️ Tonguç Akademi ile İzle",
                    "url": "https://www.youtube.com/results?search_query=Tongu%C3%A7+Akademi+8+s%C4%B1n%C4%B1f+T%C3%BCrk%C3%A7e",
                    "theme": "primary"
                }
            ]
        },
        "orta": {
            "channel": "Hız Yayınları veya Ebubekir Hoca",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Paragraf Taktikleri & Çeldirici Eleme",
            "study_tip": "Paragraf sorularında hocanın anahtar kelimeleri ve metin kanıtlarını nasıl çizdiğine dikkat et.",
            "options": [
                {
                    "name": "Hız Yayınları",
                    "action_text": "▶️ Hız Yayınları ile Dinle",
                    "url": "https://www.youtube.com/results?search_query=H%C4%B1z+Yay%C4%B1nlar%C4%B1+LGS+T%C3%BCrk%C3%A7e",
                    "theme": "red"
                },
                {
                    "name": "Ebubekir Hoca",
                    "action_text": "▶️ Ebubekir Hoca ile Dinle",
                    "url": "https://www.youtube.com/results?search_query=Ebubekir+Hoca+LGS+T%C3%BCrk%C3%A7e",
                    "theme": "blue"
                }
            ]
        },
        "iyi": {
            "channel": "Hız Yayınları veya Ebubekir Hoca",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "MEB Çıkmış & Özgün Yeni Nesil Çözümleri",
            "study_tip": "İki güçlü çeldirici arasında kaldığında doğru seçeneğe götüren mantık ipuçlarını incele.",
            "options": [
                {
                    "name": "Hız Yayınları",
                    "action_text": "▶️ Hız Yayınları ile Dinle",
                    "url": "https://www.youtube.com/results?search_query=H%C4%B1z+Yay%C4%B1nlar%C4%B1+LGS+T%C3%BCrk%C3%A7e",
                    "theme": "green"
                },
                {
                    "name": "Ebubekir Hoca",
                    "action_text": "▶️ Ebubekir Hoca ile Dinle",
                    "url": "https://www.youtube.com/results?search_query=Ebubekir+Hoca+LGS+T%C3%BCrk%C3%A7e",
                    "theme": "blue"
                }
            ]
        }
    },
    "Fen Bilimleri": {
        "temel": {
            "channel": "Derslike",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Görsel ve 3D Animasyonlu Temel Anlatım",
            "study_tip": "Mevsimler ve İklim konularındaki 3D modellemeleri ve Güneş ışınlarının geliş açılarını dikkatle izle.",
            "options": [
                {
                    "name": "Derslike",
                    "action_text": "▶️ Derslike ile İzle",
                    "url": "https://www.youtube.com/results?search_query=Derslike+8+s%C4%B1n%C4%B1f+Fen+Bilimleri",
                    "theme": "primary"
                }
            ]
        },
        "orta": {
            "channel": "Mehmet Hoca ile Fen",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Kazanım Pekiştirme & Deney Analizi",
            "study_tip": "Deney sorularındaki bağımsız/bağımlı/kontrol değişkeni çözüm adımlarını birebir uygula.",
            "options": [
                {
                    "name": "Mehmet Hoca ile Fen",
                    "action_text": "▶️ Mehmet Hoca ile Fen İzle",
                    "url": "https://www.youtube.com/results?search_query=Mehmet+Hoca+ile+Fen+8+s%C4%B1n%C4%B1f",
                    "theme": "orange"
                }
            ]
        },
        "iyi": {
            "channel": "Hız Yayınları veya DNZ Hoca",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "İleri Seviye Grafik & Deney Yorumlama",
            "study_tip": "Karmaşık grafik ve çok adımlı deney sorularında hızlı yorumlama tekniklerini not al.",
            "options": [
                {
                    "name": "Hız Yayınları",
                    "action_text": "▶️ Hız Yayınları ile Fen İzle",
                    "url": "https://www.youtube.com/results?search_query=H%C4%B1z+Yay%C4%B1nlar%C4%B1+LGS+Fen",
                    "theme": "green"
                },
                {
                    "name": "DNZ Hoca",
                    "action_text": "▶️ DNZ Hoca ile Fen İzle",
                    "url": "https://www.youtube.com/results?search_query=DNZ+Hoca+8+s%C4%B1n%C4%B1f+Fen",
                    "theme": "purple"
                }
            ]
        }
    },
    "İnkılap Tarihi": {
        "temel": {
            "channel": "Sosyal Kale",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Kronolojik Hikayeleştirme & Kavram Haritaları",
            "study_tip": "Mustafa Kemal'in askerlik ve fikir hayatını harita ve kronoloji üzerinden hocayla takip et.",
            "options": [
                {
                    "name": "Sosyal Kale",
                    "action_text": "▶️ Sosyal Kale ile Dinle / İzle",
                    "url": "https://www.youtube.com/results?search_query=Sosyal+Kale+8+s%C4%B1n%C4%B1f+LGS",
                    "theme": "primary"
                }
            ]
        },
        "orta": {
            "channel": "Sosyal Kale",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Soru Çözüm Taktikleri & Neden-Sonuç İlişkisi",
            "study_tip": "'Yalnızca bu bilgiye göre' tarzı sorularda metin dışına çıkmama kuralını pekiştir.",
            "options": [
                {
                    "name": "Sosyal Kale",
                    "action_text": "▶️ Sosyal Kale ile Dinle / İzle",
                    "url": "https://www.youtube.com/results?search_query=Sosyal+Kale+%C4%B0nk%C4%B1lap+Tarihi",
                    "theme": "orange"
                }
            ]
        },
        "iyi": {
            "channel": "Buğra Hoca – Sosyal Bilgiler Dersliği",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "Kritik Çeldiriciler & MEB Tarzı Uç Sorular",
            "study_tip": "Tarihsel kavramların güncel yorumlarla ilişkilendirildiği zor soru tiplerine odaklan.",
            "options": [
                {
                    "name": "Buğra Hoca (S.B. Dersliği)",
                    "action_text": "▶️ Buğra Hoca ile Dinle / İzle",
                    "url": "https://www.youtube.com/results?search_query=Bu%C4%9Fra+Hoca+Sosyal+Bilgiler+Dersli%C4%9Fi+LGS",
                    "theme": "green"
                }
            ]
        }
    },
    "Din Kültürü": {
        "temel": {
            "channel": "Cebrail Hocam",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Kaza-Kader Temel Kavramları & Ayet Mealleri",
            "study_tip": "Ömür, ecel, rızık, tevekkül ve yasalar konusunu hocanın kavram tablolarından tekrar et.",
            "options": [
                {
                    "name": "Cebrail Hocam (Konu)",
                    "action_text": "▶️ Cebrail Hocam ile Dinle / İzle",
                    "url": "https://www.youtube.com/results?search_query=Cebrail+Hocam+8+s%C4%B1n%C4%B1f+Din",
                    "theme": "primary"
                }
            ]
        },
        "orta": {
            "channel": "Cebrail Hocam",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Ayet Yorumlama & MEB Örnek Soruları",
            "study_tip": "Ayet-el Kürsi ana fikri ve evrensel yasalarla ilgili soru kalıplarını videoyla paralel çöz.",
            "options": [
                {
                    "name": "Cebrail Hocam (LGS)",
                    "action_text": "▶️ Cebrail Hocam ile Dinle / İzle",
                    "url": "https://www.youtube.com/results?search_query=Cebrail+Hocam+LGS+Din+K%C3%BClt%C3%BCr%C3%BC",
                    "theme": "orange"
                }
            ]
        },
        "iyi": {
            "channel": "Cebrail Hocam",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "10'da 10 Hedefi & Dikkat/Çeldirici Analizi",
            "study_tip": "Kelimelerin ince anlam farklarına dayalı soru kalıplarını yakalayarak full yapmayı hedefle.",
            "options": [
                {
                    "name": "Cebrail Hocam (Soru Çözüm)",
                    "action_text": "▶️ Cebrail Hocam ile Soru Çözümü İzle",
                    "url": "https://www.youtube.com/results?search_query=Cebrail+Hocam+LGS+soru+%C3%A7%C3%B6z%C3%BCm%C3%BC",
                    "theme": "green"
                }
            ]
        }
    },
    "İngilizce": {
        "temel": {
            "channel": "Tonguç Akademi",
            "level_name": "Temel Seviye",
            "badge_color": "#E74C3C",
            "focus": "Temel Kelimeler & Kalıp Cümleler",
            "study_tip": "Friendship ünitesi kelimelerini ve Türkçelerini sesli tekrar ederek kelime defterine geçir.",
            "options": [
                {
                    "name": "Tonguç Akademi",
                    "action_text": "▶️ Tonguç Akademi ile İngilizce İzle",
                    "url": "https://www.youtube.com/results?search_query=Tongu%C3%A7+Akademi+8+s%C4%B1n%C4%B1f+%C4%B0ngilizce",
                    "theme": "primary"
                }
            ]
        },
        "orta": {
            "channel": "Dilek Demirel",
            "level_name": "Orta Seviye",
            "badge_color": "#F39C12",
            "focus": "Diyalog Tamamlama & Soru Çözüm Metotları",
            "study_tip": "Davet, kabul, ret ve mazeret cümlelerini diyalog içi bağlamıyla öğren.",
            "options": [
                {
                    "name": "Dilek Demirel",
                    "action_text": "▶️ Dilek Demirel ile Dinle / İzle",
                    "url": "https://www.youtube.com/results?search_query=Dilek+Demirel+8+s%C4%B1n%C4%B1f+LGS+%C4%B0ngilizce",
                    "theme": "orange"
                }
            ]
        },
        "iyi": {
            "channel": "Ümitcan Hoca",
            "level_name": "İleri Düzey (Şampiyon)",
            "badge_color": "#27AE60",
            "focus": "Yeni Nesil Okuma Parçaları, Tablo & Grafik Yorumlama",
            "study_tip": "Afiş, davetiye ve soru kökündeki 'NOT / except' gibi olumsuzluk ifadelerine dikkat ederek hızlan.",
            "options": [
                {
                    "name": "Ümitcan Hoca",
                    "action_text": "▶️ Ümitcan Hoca ile Dinle / İzle",
                    "url": "https://www.youtube.com/results?search_query=%C3%9Cmitcan+Hoca+8+s%C4%B1n%C4%B1f+LGS+%C4%B0ngilizce",
                    "theme": "green"
                }
            ]
        }
    }
}

def determine_level(subject_name, net):
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
    sub_key = None
    for k in YOUTUBE_RESOURCES.keys():
        if k.lower() in subject_name.lower():
            sub_key = k
            break
            
    if not sub_key:
        sub_key = "Matematik"
        
    level = determine_level(sub_key, net)
    info = YOUTUBE_RESOURCES[sub_key][level]
    
    # Generate buttons list with exact URLs
    buttons = []
    for opt in info.get("options", []):
        opt_url = opt["url"]
        # If target topic exists, append it to query
        if target_topic and str(target_topic).strip():
            clean_top = str(target_topic).split('(')[0].strip()
            opt_url += "+" + urllib.parse.quote_plus(clean_top)
            
        buttons.append({
            "name": opt["name"],
            "action_text": opt.get("action_text", f"▶️ {opt['name']} ile İzle"),
            "url": opt_url,
            "theme": opt.get("theme", "primary")
        })
    
    primary_url = buttons[0]["url"] if buttons else "https://www.youtube.com"
    primary_action = buttons[0]["action_text"] if buttons else "İzle"

    return {
        "subject": sub_key,
        "level": level,
        "level_name": info["level_name"],
        "badge_color": info["badge_color"],
        "channel": info["channel"],
        "action_text": primary_action,
        "focus": info["focus"],
        "study_tip": info["study_tip"],
        "search_url": primary_url,
        "buttons": buttons
    }

def render_lgs_youtube_table_html():
    """
    Returns a beautifully styled, compact HTML table containing all 6 LGS subjects,
    their recommended YouTube teachers by level with distinct, stylish pill badges.
    """
    html = """
    <div style="background-color: #FFFFFF; border: 1.5px solid #D5D8DC; border-radius: 10px; padding: 12px; margin-top: 15px; box-shadow: 0 3px 8px rgba(0,0,0,0.06);">
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #C0392B; padding-bottom: 6px; margin-bottom: 10px;">
            <span style="font-weight: 800; color: #1F497D; font-size: 14px;">
                📺 8. Sınıf LGS YouTube Öğretmen Listesi
            </span>
            <span style="background-color: #FDEDEC; color: #C0392B; border: 1px solid #F5B7B1; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">
                Canlı Linkler
            </span>
        </div>
        <p style="font-size: 11.5px; color: #555; margin-bottom: 8px;">
            Konu eksiğinize veya seviyenize göre dilediğiniz hocayı seçip doğrudan ders videolarına ulaşabilirsiniz:
        </p>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: separate; border-spacing: 0 4px; font-size: 11.5px; text-align: left;">
                <thead>
                    <tr style="background-color: #F4F6F7; color: #2C3E50;">
                        <th style="padding: 6px 8px; border-radius: 6px 0 0 6px;">Ders</th>
                        <th style="padding: 6px 8px; color: #C0392B;">🔴 Temel Seviye</th>
                        <th style="padding: 6px 8px; color: #D35400;">🟡 Orta Seviye</th>
                        <th style="padding: 6px 8px; color: #27AE60; border-radius: 0 6px 6px 0;">🟢 İyi Seviye</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- MATEMATİK -->
                    <tr style="background-color: #FFFFFF;">
                        <td style="padding: 8px 10px; font-weight: bold; color: #1F497D; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">Matematik</td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Partik%C3%BCl+Matematik+8+s%C4%B1n%C4%B1f+LGS" target="_blank" style="display:inline-block; background-color: #FDEDEC; color: #C0392B; border: 1.5px solid #F5B7B1; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Partikül Mat. ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=%C4%B0MT+Hoca+8+s%C4%B1n%C4%B1f+LGS+Matematik" target="_blank" style="display:inline-block; background-color: #FEF9E7; color: #B7950B; border: 1.5px solid #F9E79F; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ İMT Hoca ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=%C3%87opur+Hoca+8+s%C4%B1n%C4%B1f+LGS+Matematik" target="_blank" style="display:inline-block; background-color: #E8F8F5; color: #1E8449; border: 1.5px solid #A3E4D7; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Çopur Hoca ↗</a>
                        </td>
                    </tr>
                    <!-- TÜRKÇE -->
                    <tr style="background-color: #FAFCFD;">
                        <td style="padding: 8px 10px; font-weight: bold; color: #1F497D; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">Türkçe</td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Tongu%C3%A7+Akademi+8+s%C4%B1n%C4%B1f+T%C3%BCrk%C3%A7e" target="_blank" style="display:inline-block; background-color: #FDEDEC; color: #C0392B; border: 1.5px solid #F5B7B1; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Tonguç Akd. ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <div style="display: flex; flex-direction: column; gap: 4px; min-width: 145px;">
                                <a href="https://www.youtube.com/results?search_query=H%C4%B1z+Yay%C4%B1nlar%C4%B1+LGS+T%C3%BCrk%C3%A7e" target="_blank" style="display: flex; align-items: center; justify-content: space-between; background-color: #FEF3C7; color: #92400E; border: 1.5px solid #F59E0B; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold; font-size: 11px;">
                                    <span>📕 Hız Yayınları</span>
                                    <span style="background: #F59E0B; color: white; font-size: 9.5px; padding: 1px 6px; border-radius: 4px;">İzle ↗</span>
                                </a>
                                <div style="display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 9px; color: #64748B; font-weight: 800; letter-spacing: 0.5px;">
                                    <span style="height: 1px; background: #CBD5E1; flex: 1;"></span>
                                    <span>VEYA</span>
                                    <span style="height: 1px; background: #CBD5E1; flex: 1;"></span>
                                </div>
                                <a href="https://www.youtube.com/results?search_query=Ebubekir+Hoca+LGS+T%C3%BCrk%C3%A7e" target="_blank" style="display: flex; align-items: center; justify-content: space-between; background-color: #DBEAFE; color: #1E40AF; border: 1.5px solid #3B82F6; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold; font-size: 11px;">
                                    <span>🎓 Ebubekir Hoca</span>
                                    <span style="background: #3B82F6; color: white; font-size: 9.5px; padding: 1px 6px; border-radius: 4px;">İzle ↗</span>
                                </a>
                            </div>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <div style="display: flex; flex-direction: column; gap: 4px; min-width: 145px;">
                                <a href="https://www.youtube.com/results?search_query=H%C4%B1z+Yay%C4%B1nlar%C4%B1+LGS+T%C3%BCrk%C3%A7e" target="_blank" style="display: flex; align-items: center; justify-content: space-between; background-color: #D1FAE5; color: #065F46; border: 1.5px solid #10B981; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold; font-size: 11px;">
                                    <span>🏆 Hız Yayınları</span>
                                    <span style="background: #10B981; color: white; font-size: 9.5px; padding: 1px 6px; border-radius: 4px;">İzle ↗</span>
                                </a>
                                <div style="display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 9px; color: #64748B; font-weight: 800; letter-spacing: 0.5px;">
                                    <span style="height: 1px; background: #CBD5E1; flex: 1;"></span>
                                    <span>VEYA</span>
                                    <span style="height: 1px; background: #CBD5E1; flex: 1;"></span>
                                </div>
                                <a href="https://www.youtube.com/results?search_query=Ebubekir+Hoca+LGS+T%C3%BCrk%C3%A7e" target="_blank" style="display: flex; align-items: center; justify-content: space-between; background-color: #DBEAFE; color: #1E40AF; border: 1.5px solid #3B82F6; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold; font-size: 11px;">
                                    <span>🎓 Ebubekir Hoca</span>
                                    <span style="background: #3B82F6; color: white; font-size: 9.5px; padding: 1px 6px; border-radius: 4px;">İzle ↗</span>
                                </a>
                            </div>
                        </td>
                    </tr>
                    <!-- FEN BİLİMLERİ -->
                    <tr style="background-color: #FFFFFF;">
                        <td style="padding: 8px 10px; font-weight: bold; color: #1F497D; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">Fen Bilimleri</td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Derslike+8+s%C4%B1n%C4%B1f+Fen+Bilimleri" target="_blank" style="display:inline-block; background-color: #FDEDEC; color: #C0392B; border: 1.5px solid #F5B7B1; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Derslike ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Mehmet+Hoca+ile+Fen+8+s%C4%B1n%C4%B1f" target="_blank" style="display:inline-block; background-color: #FEF9E7; color: #B7950B; border: 1.5px solid #F9E79F; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Mehmet Hoca ile Fen ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <div style="display: flex; flex-direction: column; gap: 4px; min-width: 145px;">
                                <a href="https://www.youtube.com/results?search_query=H%C4%B1z+Yay%C4%B1nlar%C4%B1+LGS+Fen" target="_blank" style="display: flex; align-items: center; justify-content: space-between; background-color: #D1FAE5; color: #065F46; border: 1.5px solid #10B981; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold; font-size: 11px;">
                                    <span>🏆 Hız Yayınları</span>
                                    <span style="background: #10B981; color: white; font-size: 9.5px; padding: 1px 6px; border-radius: 4px;">İzle ↗</span>
                                </a>
                                <div style="display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 9px; color: #64748B; font-weight: 800; letter-spacing: 0.5px;">
                                    <span style="height: 1px; background: #CBD5E1; flex: 1;"></span>
                                    <span>VEYA</span>
                                    <span style="height: 1px; background: #CBD5E1; flex: 1;"></span>
                                </div>
                                <a href="https://www.youtube.com/results?search_query=DNZ+Hoca+8+s%C4%B1n%C4%B1f+Fen" target="_blank" style="display: flex; align-items: center; justify-content: space-between; background-color: #EDE9FE; color: #5B21B6; border: 1.5px solid #8B5CF6; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold; font-size: 11px;">
                                    <span>🔬 DNZ Hoca</span>
                                    <span style="background: #8B5CF6; color: white; font-size: 9.5px; padding: 1px 6px; border-radius: 4px;">İzle ↗</span>
                                </a>
                            </div>
                        </td>
                    </tr>
                    <!-- İNKILAP TARİHİ -->
                    <tr style="background-color: #FAFCFD;">
                        <td style="padding: 8px 10px; font-weight: bold; color: #1F497D; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">İnkılap Tarihi</td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Sosyal+Kale+8+s%C4%B1n%C4%B1f+LGS" target="_blank" style="display:inline-block; background-color: #FDEDEC; color: #C0392B; border: 1.5px solid #F5B7B1; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Sosyal Kale ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Sosyal+Kale+%C4%B0nk%C4%B1lap+Tarihi" target="_blank" style="display:inline-block; background-color: #FEF9E7; color: #B7950B; border: 1.5px solid #F9E79F; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Sosyal Kale ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Bu%C4%9Fra+Hoca+Sosyal+Bilgiler+Dersli%C4%9Fi+LGS" target="_blank" style="display:inline-block; background-color: #E8F8F5; color: #1E8449; border: 1.5px solid #A3E4D7; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Buğra Hoca ↗</a>
                        </td>
                    </tr>
                    <!-- DİN KÜLTÜRÜ -->
                    <tr style="background-color: #FFFFFF;">
                        <td style="padding: 8px 10px; font-weight: bold; color: #1F497D; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">Din Kültürü</td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Cebrail+Hocam+8+s%C4%B1n%C4%B1f+Din" target="_blank" style="display:inline-block; background-color: #FDEDEC; color: #C0392B; border: 1.5px solid #F5B7B1; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Cebrail Hocam (Konu) ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Cebrail+Hocam+LGS+Din+K%C3%BClt%C3%BCr%C3%BC" target="_blank" style="display:inline-block; background-color: #FEF9E7; color: #B7950B; border: 1.5px solid #F9E79F; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Cebrail Hocam (LGS) ↗</a>
                        </td>
                        <td style="padding: 8px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Cebrail+Hocam+LGS+soru+%C3%A7%C3%B6z%C3%BCm%C3%BC" target="_blank" style="display:inline-block; background-color: #E8F8F5; color: #1E8449; border: 1.5px solid #A3E4D7; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Cebrail Hocam (Soru) ↗</a>
                        </td>
                    </tr>
                    <!-- İNGİLİZCE -->
                    <tr style="background-color: #FAFCFD;">
                        <td style="padding: 8px 10px; font-weight: bold; color: #1F497D; vertical-align: middle;">İngilizce</td>
                        <td style="padding: 8px 10px; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Tongu%C3%A7+Akademi+8+s%C4%B1n%C4%B1f+%C4%B0ngilizce" target="_blank" style="display:inline-block; background-color: #FDEDEC; color: #C0392B; border: 1.5px solid #F5B7B1; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Tonguç Akd. ↗</a>
                        </td>
                        <td style="padding: 8px 10px; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=Dilek+Demirel+8+s%C4%B1n%C4%B1f+LGS+%C4%B0ngilizce" target="_blank" style="display:inline-block; background-color: #FEF9E7; color: #B7950B; border: 1.5px solid #F9E79F; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Dilek Demirel ↗</a>
                        </td>
                        <td style="padding: 8px 10px; vertical-align: middle;">
                            <a href="https://www.youtube.com/results?search_query=%C3%9Cmitcan+Hoca+8+s%C4%B1n%C4%B1f+LGS+%C4%B0ngilizce" target="_blank" style="display:inline-block; background-color: #E8F8F5; color: #1E8449; border: 1.5px solid #A3E4D7; border-radius: 6px; padding: 4px 8px; text-decoration: none; font-weight: bold;">▶ Ümitcan Hoca ↗</a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """
    return html

def render_yt_buttons_html(buttons):
    """
    Renders one or multiple stylish buttons for YouTube channels.
    If multiple options exist, renders distinct buttons side-by-side with distinct themes.
    """
    if not buttons:
        return ""
    if len(buttons) == 1:
        b = buttons[0]
        return f"""
        <div style='margin-top:8px;'>
            <a href='{b['url']}' target='_blank' style='display:block; text-align:center; background:linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color:white; padding:8px 12px; border-radius:6px; text-decoration:none; font-size:12px; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.15);'>
                {b['action_text']} ↗
            </a>
        </div>
        """
    else:
        # Multiple distinct buttons with contrasting, vibrant colors
        palette = {
            "red": ("linear-gradient(135deg, #EF4444 0%, #B91C1C 100%)", "#FFFFFF", "#991B1B"),
            "amber": ("linear-gradient(135deg, #F59E0B 0%, #B45309 100%)", "#FFFFFF", "#78350F"),
            "orange": ("linear-gradient(135deg, #F97316 0%, #C2410C 100%)", "#FFFFFF", "#7C2D12"),
            "blue": ("linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)", "#FFFFFF", "#1E3A8A"),
            "green": ("linear-gradient(135deg, #10B981 0%, #047857 100%)", "#FFFFFF", "#064E3B"),
            "purple": ("linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)", "#FFFFFF", "#4C1D95"),
            "primary": ("linear-gradient(135deg, #DC2626 0%, #991B1B 100%)", "#FFFFFF", "#7F1D1D")
        }
        fallback_colors = [
            ("linear-gradient(135deg, #F59E0B 0%, #B45309 100%)", "#FFFFFF", "#78350F"),
            ("linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)", "#FFFFFF", "#1E3A8A")
        ]
        btn_htmls = []
        for i, b in enumerate(buttons):
            theme = b.get("theme", "")
            if theme in palette:
                bg, fg, border_c = palette[theme]
            else:
                bg, fg, border_c = fallback_colors[i % len(fallback_colors)]
            
            btn_htmls.append(f"""
            <a href='{b['url']}' target='_blank' style='flex:1; display:flex; align-items:center; justify-content:center; text-align:center; min-height:36px; background:{bg}; color:{fg}; padding:6px 6px; border-radius:6px; text-decoration:none; font-size:11px; font-weight:bold; box-shadow:0 2px 5px rgba(0,0,0,0.15); border:1px solid {border_c}; line-height:1.2;'>
                {b['action_text']} ↗
            </a>
            """)
        return f"""
        <div style='margin-top:8px;'>
            <div style='display:flex; gap:6px; align-items:center;'>
                {''.join(btn_htmls)}
            </div>
            <div style='text-align:center; font-size:10px; color:#6B7280; font-weight:600; margin-top:4px;'>
                (İki hocadan dilediğini seçip izleyebilirsin)
            </div>
        </div>
        """

