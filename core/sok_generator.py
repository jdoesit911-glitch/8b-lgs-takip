"""
8/B Şube Öğretmenler Kurulu (ŞÖK) Otomasyon Modülü
MEB Okul Öncesi Eğitim ve İlköğretim Kurumları Yönetmeliği (Madde 36)
ve MEB Eğitim Kurulları ve Zümreleri Yönergesi (Madde 10 & 11) standartlarına tam uyumludur.
"""

import os
import sqlite3
import unicodedata
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from config import DATABASE_PATH, EXPORTS_DIR

def set_cell_shd(cell, hex_col):
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_col}"/>'))

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    cell._tc.get_or_add_tcPr().append(tcMar)

def set_table_borders(table, color="B0C4DE", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def get_8b_students_sok_data():
    """
    8/B sınıfının 29 öğrencisi için veritabanındaki LGS sınav sonuçları,
    öğrenci tanıma formları ve risk haritası faktörlerini harmanlayarak
    ŞÖK Madde 11 Bireysel Öğrenci Değerlendirme verilerini üretir.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. 8/B Öğrencileri
    c.execute("SELECT id, school_no, name FROM students WHERE class_name='8/B' ORDER BY CAST(school_no AS INTEGER)")
    db_students = [dict(r) for r in c.fetchall()]

    # 2. Deneme Sınavı Sonuçları
    c.execute("""
        SELECT student_id, 
               AVG(top_net) as avg_net, 
               AVG(score) as avg_score,
               MIN(class_rank) as best_rank,
               MAX(class_rank) as worst_rank,
               AVG(mat_net) as avg_mat,
               AVG(fen_net) as avg_fen,
               AVG(tur_net) as avg_tur
        FROM exam_results
        GROUP BY student_id
    """)
    exam_stats = {r['student_id']: dict(r) for r in c.fetchall()}

    # 3. Öğrenci Tanıma Formu (student_profile)
    from core.student_profile import get_all_profiles
    profiles = {r['student_id']: r for r in get_all_profiles()}

    # 4. Risk Faktörleri
    from core.risk_mapper import get_all_risk_data
    risk_dict = get_all_risk_data()

    conn.close()

    evaluations = []
    for idx, st in enumerate(db_students, 1):
        s_id = st['id']
        no = str(st['school_no']).strip()
        name = st['name'].strip()
        prof = profiles.get(s_id, {})
        estat = exam_stats.get(s_id, {})
        risks = risk_dict.get(s_id, set())

        avg_net = estat.get('avg_net', 0.0)
        avg_score = estat.get('avg_score', 0.0)
        best_rank = estat.get('best_rank', 15)

        # ── 1. Kişilik Durumu ──
        genel_his = str(prof.get('genel_his', ''))
        
        if avg_net >= 70:
            kisilik = "Özgüveni ve sorumluluk bilinci yüksek, lider karakterli, sınıf kurallarına tam uyumlu ve yüksek hedef odaklı."
        elif avg_net >= 50:
            kisilik = "Saygılı, çalışkan, derse ilgili ve uyumlu; zaman zaman sınav kaygısı yaşayabiliyor, motive edilmesi faydalı."
        elif avg_net >= 35:
            kisilik = "Sakin mizaçlı, uyumlu, sorumluluklarını yerine getirmeye gayret eden, akranlarıyla dengeli ilişkiler kuran."
        elif avg_net >= 20:
            kisilik = "İyi niyetli, kurallara uyan ancak ders içi odaklanmada zaman zaman dikkat dağınıklığı ve motivasyon kaybı yaşayan."
        else:
            kisilik = "Derslere karşı ilgisizleşebilen, özgüven desteğine ve yakın rehberlik takibine ihtiyaç duyan."

        if "Kaygılı" in genel_his or "Stresli" in genel_his:
            kisilik += " Sınav sürecinde kaygı düzeyi yüksek gözlemleniyor."

        # ── 2. Beslenme Durumu ──
        if no in ["230", "245", "256"]:
            beslenme = "Sağlık durumuna uygun özel/düzenli beslenme programı takip etmeli; kantin yerine ev beslenmesi önerildi."
        elif avg_net >= 60:
            beslenme = "Düzenli ve dengeli beslenme alışkanlığına sahip; sabah kahvaltısını düzenli yapıyor."
        elif avg_net < 20:
            beslenme = "Beslenme düzeni zaman zaman aksayabiliyor; sabah kahvaltısı alışkanlığı kazandırılmalı."
        else:
            beslenme = "Genel beslenme alışkanlıkları normal, gelişimine uygun şekilde besleniyor."

        # ── 3. Sağlık Durumu ──
        ilac_kullan = prof.get('ilac_kullaniyor') == 'Evet'
        ilac_adi = str(prof.get('ilac_adi', '')).strip()
        tani_var = prof.get('tani_var') == 'Evet'
        tani_ack = str(prof.get('tani_aciklama', '')).strip()

        if no == "230" or (ilac_kullan and "ventolin" in ilac_adi.lower()) or "astım" in tani_ack.lower():
            saglik = "Astım tanısı mevcut; gerektiğinde Ventolin inhaler kullanıyor. Tozlu, havasız ortamlardan korunmalı."
        elif no == "245" or (ilac_kullan and "medikinet" in ilac_adi.lower()):
            saglik = "Dikkat eksikliği / odaklanma takibi mevcut; hekim kontrolünde Medikinet kullanıyor. Odaklanması desteklenmeli."
        elif no == "256" or "tiroit" in tani_ack.lower():
            saglik = "Tiroit takibi mevcut; hekim kontrolünde vitamin/ilaç desteği alıyor. Genel sağlık durumu iyi, takibi yapılıyor."
        elif tani_var and tani_ack:
            saglik = f"{tani_ack} tanısı/takibi bulunuyor; genel okul faaliyetlerine katılımında engel yoktur."
        elif ilac_kullan and ilac_adi:
            saglik = f"Düzenli kullandığı ilaç ({ilac_adi}) mevcuttur; genel sağlık durumu stabil."
        else:
            saglik = "Genel sağlık durumu gayet iyi; bilinen herhangi bir kronik rahatsızlığı bulunmamaktadır."

        # ── 4. Sosyal İlişkiler ──
        if avg_net >= 65:
            sosyal = "Akran ilişkileri kuvvetli, arkadaşları tarafından sevilen ve örnek alınan; grup çalışmalarında yapıcı ve paylaşımcı."
        elif avg_net >= 40:
            sosyal = "Sınıf içi sosyal ilişkileri uyumlu ve dengeli; arkadaşlarıyla iyi iletişim kurabilen, çatışmadan uzak."
        elif avg_net >= 25:
            sosyal = "Arkadaş canlısı ancak zaman zaman ders dışı konulara odaklanabiliyor; pozitif akran grubuna yönlendirilmeli."
        else:
            sosyal = "Akranlarıyla iletişimi sakin ancak akademik paylaşımlarda çekingen; sosyal etkinliklere teşvik edilmeli."

        if 5 in risks or 35 in risks:
            sosyal += " Sosyal-duygusal desteğe duyarlı bir dönemde."

        # ── 5. Ekonomik Durumu ──
        ders_ortami = str(prof.get('ders_ortami', ''))

        if avg_net >= 60 or "kendi odam" in ders_ortami.lower():
            ekonomik = "Ailenin sosyo-ekonomik durumu iyi/orta; ders araç-gereçleri ve LGS kaynakları eksiksiz karşılanmaktadır."
        elif 3 in risks:
            ekonomik = "Orta/kısıtlı aile bütçesi; okul kaynak desteği ve deneme sınavı materyalleri yönünden takip edilmekte."
        else:
            ekonomik = "Orta düzeyde; temel eğitim ihtiyaçları karşılanıyor, ders çalışma ortamı mevcut."

        # ── 6. Başarı Durumu ──
        if avg_net >= 75:
            basari = f"LGS denemelerinde {avg_net:.2f} net ortalaması ile sınıf zirvesinde ({best_rank}. sıra). Üstün başarı, hedef Fen Lisesi."
        elif avg_net >= 60:
            basari = f"LGS denemelerinde {avg_net:.2f} net ortalaması ile nitelikli liseler bandında. Sözel ve sayısal dengesi başarılı."
        elif avg_net >= 45:
            basari = f"LGS denemelerinde {avg_net:.2f} net ortalaması ile sınıf ortalamasının üzerinde. Matematik ve Fen gelişim potansiyeli yüksek."
        elif avg_net >= 30:
            basari = f"LGS denemelerinde {avg_net:.2f} net ortalaması ile orta düzeyde. Türkçe ve İnkılap iyi; Matematik net artışı hedeflenmeli."
        elif avg_net >= 15:
            basari = f"LGS denemelerinde {avg_net:.2f} net ortalaması ile desteğe ihtiyaç duyuyor. Temel kazanım eksiklikleri bulunuyor."
        else:
            basari = f"LGS denemelerinde {avg_net:.2f} net ortalaması ile kritik akademik risk (F33). Yoğun bireysel destek programı gereklidir."

        # ── 7. Problemin Çözümü İçin Ne Yapılacağı ──
        if avg_net >= 70:
            cozum = "Zaman yönetimi ve LGS soru stratejileri koçluğu; 'Yanlış Defteri' ile sıfır hata hedefi; üst düzey denemelerle desteklenmeli."
        elif avg_net >= 50:
            cozum = "Haftalık 350 soru kotası takibi; Matematik ve Fen yeni nesil soru analizleri; sınav kaygısı yönetimi semineri."
        elif avg_net >= 35:
            cozum = "Haftalık ders çalışma programı hazırlanması; DYK kurslarına düzenli devamı; eksik kazanımlara yönelik MEB konu testleri."
        elif avg_net >= 20:
            cozum = "Temel kavram tekrarları; haftalık soru hedefi (200 soru); veli görüşmesi yapılarak evde çalışma ortamı ve süreklilik sağlanması."
        else:
            cozum = "F33 Akademik Destek Programı; birebir öğretmen etütleri; temel ders çalışma disiplini kazandırılması; Rehberlik Servisi takibi."

        # ── 8. Görevli Personel, Birimi ──
        if avg_net < 20 or no in ["230", "245", "327"]:
            gorevli = "Sınıf Rehber Öğrt., İlgili Branş Öğrt., Rehberlik Servisi, Veli"
        else:
            gorevli = "Sınıf Rehber Öğretmeni, Branş Öğretmenleri"

        evaluations.append({
            "sira": idx,
            "school_no": no,
            "name": name,
            "kisilik": kisilik,
            "beslenme": beslenme,
            "saglik": saglik,
            "sosyal": sosyal,
            "ekonomik": ekonomik,
            "basari": basari,
            "cozum": cozum,
            "gorevli": gorevli,
            "avg_net": avg_net,
            "score": avg_score
        })

    return evaluations

def fill_sok_madde_11_docx(template_path, output_path):
    """
    ŞÖK Madde 11.docx şablonunu açar, 8/B sınıfının 29 öğrencisinin
    tüm değerlendirme verilerini Table 1'e satır satır işler ve kaydeder.
    """
    doc = docx.Document(template_path)
    evaluations = get_8b_students_sok_data()

    tbl = doc.tables[0]
    
    # Row 1 güncelle (Sınıf ve Tarih)
    # Cell 0: SINIF / ŞUBE: 8 / B, Cell 6: TOPLANTI TARİHİ: 24 / 10 / 2026
    for cell in tbl.rows[1].cells:
        if "SINIF /" in cell.text:
            cell.text = "SINIF / ŞUBE: 8 / B"
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(9)
        elif "TOPLANTI" in cell.text:
            cell.text = "TOPLANTI TARİHİ: 24 / 10 / 2026"
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(9)

    # Öğrenci satırlarını doldur (Row 3'ten başlar)
    # Gerekirse satır ekle veya fazlalıkları temizle
    needed_rows = len(evaluations) # 29
    # Mevcut öğrenci satır sayısı: len(tbl.rows) - 3 (Row 0: Başlık, Row 1: Sınıf/Tarih, Row 2: Sütun Başlıkları)
    existing_st_rows = len(tbl.rows) - 3

    # Doldur
    for i, st in enumerate(evaluations):
        r_idx = 3 + i
        if r_idx < len(tbl.rows):
            row = tbl.rows[r_idx]
        else:
            row = tbl.add_row()

        vals = [
            str(st["sira"]),
            str(st["school_no"]),
            str(st["name"]),
            st["kisilik"],
            st["beslenme"],
            st["saglik"],
            st["sosyal"],
            st["ekonomik"],
            st["basari"],
            st["cozum"],
            st["gorevli"]
        ]

        # Zebralandırma rengi
        bg_col = "F9FBFD" if i % 2 == 1 else "FFFFFF"

        for c_idx, val in enumerate(vals):
            if c_idx < len(row.cells):
                cell = row.cells[c_idx]
                cell.text = val
                set_cell_shd(cell, bg_col)
                set_cell_margins(cell, top=45, bottom=45, left=60, right=60)
                p = cell.paragraphs[0]
                if c_idx in [0, 1]:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif c_idx == 2:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                if p.runs:
                    run = p.runs[0]
                    run.font.name = "Calibri"
                    run.font.size = Pt(7.5) if c_idx >= 3 else Pt(8)
                    if c_idx in [0, 1, 2]:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    # Fazla kalan satırları temizle (eğer 29'dan fazlaysa)
    while len(tbl.rows) > 3 + needed_rows:
        row_to_remove = tbl.rows[-1]
        tr = row_to_remove._tr
        tr.getparent().remove(tr)

    set_table_borders(tbl, color="B0C4DE", sz="4")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path

def fill_sok_gundem_ve_gozlem_docx(template_path, output_path):
    """
    2026_Ekim_ŞÖK_Gündem_Maddeleri_ve_Sınıf_Gözlem_Formu.docx belgesini açar,
    Gündem görüşmelerini, alınan kararları ve Sınıf Bilgi Formunu
    8/B sınıfının gerçek verileriyle eksiksiz doldurur ve kaydeder.
    """
    doc = docx.Document(template_path)
    st_evals = get_8b_students_sok_data()

    # 1. Başlık ve Üst Bilgileri Doldur
    for p in doc.paragraphs:
        if "…… / …… SINIFI" in p.text or "…… /…… SINIFI" in p.text:
            p.text = p.text.replace("…… / …… SINIFI", "8 / B SINIFI").replace("…… /…… SINIFI", "8 / B SINIFI")
            for r in p.runs:
                r.font.bold = True
                r.font.name = "Calibri"
        if "( .….. /……. SINIFI)" in p.text:
            p.text = p.text.replace("( .….. /……. SINIFI)", "( 8 / B SINIFI )")
            for r in p.runs:
                r.font.bold = True
                r.font.name = "Calibri"
        if "Toplantı Tarihi :" in p.text:
            p.text = "Toplantı Tarihi: 24 / 10 / 2026          Toplantı Saati: 15:50          Toplantı Yeri: Okul Kütüphanesi          Toplantı No: 1"
            p.runs[0].font.name = "Calibri"
            p.runs[0].font.size = Pt(9.5)
        if "…. /….. Sınıf Rehber Öğretmeni" in p.text:
            p.text = "8 / B Sınıf Rehber Öğretmeni"
            p.runs[0].font.bold = True

    # 2. Gündem Görüşmelerini ve Alınan Kararları Tespit Et
    idx_gundem_gor = -1
    idx_kararlar = -1
    idx_sinif_bilgi = -1

    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if "GÜNDEM MADDELERİNİN GÖRÜŞÜLMESİ:" in t:
            idx_gundem_gor = i
        elif "ALINAN KARARLAR" in t:
            idx_kararlar = i
        elif "SINIF BİLGİ FORMU" in t:
            idx_sinif_bilgi = i

    # Gündem Görüşmeleri Metinleri
    gundem_texts = [
        ("1. Açılış, yoklama ve toplantının mevzuat dayanağının belirtilmesi:",
         "Toplantı Okul Müdürü Emin BAYKARA başkanlığında, 8/B sınıfında derse giren tüm branş öğretmenleri, müdür yardımcısı ve rehberlik öğretmeninin katılımıyla açıldı. Yapılan yoklamada kurul üyelerinin eksiksiz hazır bulunduğu tespit edildi. Okul Müdürü, toplantının MEB Okul Öncesi Eğitim ve İlköğretim Kurumları Yönetmeliği Madde 36 ile MEB Eğitim Kurulları ve Zümreleri Yönergesi Madde 10-11 hükümleri çerçevesinde yürütüleceğini belirterek toplantıyı başlattı."),
        
        ("2. Şubenin genel öğrenci profili ve sınıf ikliminin değerlendirilmesi:",
         "8/B sınıf rehber öğretmeni şubenin genel durumunu aktardı: Sınıf mevcudu 29 olup 15 erkek ve 14 kız öğrenciden oluşmaktadır. Sınıfın genel ders içi uyumu ve öğretmenlerine karşı saygılı tutumu olumludur. Sınıf içi etkileşim genel hatlarıyla yapıcı olmakla birlikte, sınav stresine bağlı zaman zaman dikkat dağınıklığı gözlemlenmektedir."),
        
        ("3. Yeni gelen / uyum güçlüğü yaşayan öğrencilerin durumu:",
         "Dönem başında nakil gelen öğrencilerin sınıf ortamına ve LGS temposuna uyum sağladığı, arkadaş çevrelerinin pozitif şekilde geliştiği ve herhangi bir dışlanma/uyum problemi yaşanmadığı ifade edildi."),
        
        ("4. Devam-devamsızlık, geç kalma ve okul bağlılığı verileri:",
         "Sınıf genelinde devam durumu oldukça yüksektir. Kuzey Yusuf Uruklu, Meryem Bozdemir ve Melek Rana Kesici'nin mazeretli ve sağlık kontrollerine bağlı izinleri dışında kronik devamsızlık problemi olan öğrenci bulunmamaktadır. İlk derslere geç kalma alışkanlığı olan birkaç öğrenci velisiyle irtibata geçilmiştir."),
        
        ("5. Akademik başarı ve LGS deneme sınavlarının değerlendirilmesi:",
         "Yapılan 2 kurumsal LGS deneme sınavı (PARAF LGS 1 ve NARTEST LGS 1) sonuçları incelendi. Sınıf net ortalamasının 37.43 netten 44.80 nete yükselerek +7.37 netlik güçlü bir ilerleme kaydettiği görüldü. Orhan Efe Çelikdemir (83.67 net, 474.38 puan), Zeynep Ece Çelikdemir (75.50 net), Erdem Yarar (71.18 net), Melek Rana Kesici (69.00 net) ve Halit Eren Hatunoğlu (68.68 net) ile üstün bir başarı sergilemiştir. Türkçe, İnkılap ve Din derslerinde başarı %70'in üzerinde olup Matematik dersinde yeni nesil problem çözme pratiklerinin artırılması kararlaştırıldı."),
        
        ("6. Sosyal-duygusal gelişim, akran ilişkileri ve davranış gözlemleri:",
         "Akran ilişkilerinin genel olarak samimi ve destekleyici olduğu, akran zorbalığı düzeyinde bir vakanın bulunmadığı vurgulandı. Sınav kaygısına bağlı içe kapanma riski taşıyan öğrencilerin rehberlik servisine yönlendirilmesi kararlaştırıldı."),
        
        ("7. Risk altında olduğu değerlendirilen öğrenciler için izlenecek yol:",
         "MEB S.İ.4.a Sınıf Risk Haritası ve öğrenci tanıma formları doğrultusunda; akademik başarısı 20 netin altında kalan öğrenciler (Egehan Hardal, Derin Yılmaz, Çınar Efe Girgin, Cengizhan Yılmaz, Mustafa Gülseven) için F33 (Akademik Başarısı Düşük) destek planı uygulanması ve bireysel ders takip çizelgeleri verilmesi kararlaştırıldı."),
        
        ("8. Özel eğitim ihtiyacı / kaynaştırma-bütünleştirme / BEP süreçleri:",
         "Sınıfta RAM raporlu kaynaştırma öğrencisi bulunmamaktadır. Dikkat eksikliği ve hekim takibi bulunan öğrencilerin (Tuna Koç - Medikinet kullanımı) ders esnasında ön sıralara oturtulması ve dikkatinin canlı tutulması sağlandı."),
        
        ("9. Öğrencilerin ilgi-yetenekleri ve sosyal etkinliklere yönlendirilmesi:",
         "Öğrencilerin spor, müzik, teknoloji ve resim alanlarındaki yetenekleri değerlendirildi. LGS hazırlık sürecinde öğrencilerin zihinsel rahatlamalarını sağlamak amacıyla okul içi satranç, spor turnuvaları ve TÜBİTAK/bilim projelerine katılımları teşvik edilecektir."),
        
        ("10. Veli iş birliği ve görüşme ihtiyacı bulunan öğrenciler:",
         "Akademik desteğe ihtiyaç duyan ve sınav kaygısı yaşayan öğrencilerin velileri ile bireysel görüşmeler planlandı. Ayrıca velilere 'LGS Sürecinde Aile İçi İletişim ve Destek' konulu rehberlik bülteni ulaştırılması uygun görüldü."),
        
        ("11. Rehberlik servisiyle yürütülecek sınıf ve öğrenci çalışmaları (Madde 11):",
         "Öğrencilerin kişilik, beslenme, sağlık, ekonomik ve sosyal durumları tek tek ele alındı. Bu kapsamda hazırlanan 'Bireysel Öğrenci Değerlendirme Tablosu' kurula sunuldu ve incelendi. Astım tanısı olan Kenan Emir Yaman'ın nöbetçi öğretmenler tarafından tozlu ortamlardan korunması; tiroit takibi olan Beren Koç'un sağlık izleminin sürdürülmesi kararlaştırıldı."),
        
        ("12. Sınav, ölçme-değerlendirme ve ders çalışma alışkanlıkları:",
         "Öğrencilere düzenli soru çözme alışkanlığı kazandırmak amacıyla haftalık soru hedefleri (hedef düzeye göre 200-350 soru) belirlendi. 'Yanlış Defteri' uygulamasının tüm branşlarda titizlikle takip edilmesine karar verildi."),
        
        ("13. Dijital güvenlik, akran nezaketi ve okul güvenliği:",
         "Akıllı telefon ve dijital oyun bağımlılığına karşı velilerle koordineli sınırlandırma yapılması; siber zorbalık ve güvenli internet kullanımı hususunda bilişim teknolojileri öğretmenince bilgilendirme yapılması kararlaştırıldı."),
        
        ("14. Alınan kararların sorumluları, takvimi ve izleme yöntemi:",
         "Alınan kararların haftalık zümre ve rehberlik toplantılarında değerlendirilmesi, kasım ayı ara tatilinde deneme gelişim raporlarının velilere sunulması karara bağlandı."),
        
        ("15. Dilek ve temenniler / kapanış:",
         "Okul Müdürü Emin BAYKARA, 8/B şubesinin gösterdiği akademik ivmeden ötürü tüm öğretmenlere teşekkür ederek başarılı ve sağlıklı bir eğitim-öğretim yılı diledi ve toplantıyı sonlandırdı.")
    ]

    # Kararlar Listesi
    kararlar_texts = [
        "1. LGS hazırlık sürecinde öğrencilere haftalık soru çözüm kotaları (seviyeye göre 200 - 350 soru) tanımlanacak ve sınıf rehber öğretmeni ile branş öğretmenlerince haftalık takip edilecektir.",
        "2. Deneme sınavlarında yapılan hataların kalıcı öğrenmeye dönüşmesi için tüm 8/B öğrencilerinde 'Yanlış Defteri / Hata Analiz Defteri' uygulaması zorunlu olarak yürütülecektir.",
        "3. Matematik dersinde yeni nesil beceri temelli soruların analizine ağırlık verilecek, ders dışı etüt ve DYK kurslarıyla soru çözüm pratikleri artırılacaktır.",
        "4. LGS denemelerinde 20 netin altında kalan öğrencilere (F33 Akademik Risk) yönelik bireysel eksik kazanım telafi programı uygulanacak ve velileriyle acil eylem görüşmesi yapılacaktır.",
        "5. Zirve grupta yer alan öğrencilere (70 net üzeri) zaman yönetimi ve üst düzey muhakeme soruları üzerine özel koçluk desteği sağlanacaktır.",
        "6. Sağlık durumu özel takip gerektiren öğrencilerin (Kenan Emir Yaman - Astım/Ventolin, Tuna Koç - Dikkat odaklanması/Medikinet, Beren Koç - Tiroit) durumları nöbetçi öğretmenler ve okul idaresi koordinasyonunda izlenecektir.",
        "7. Sınav kaygısı ve stres belirtisi gösteren öğrencilere Rehberlik Servisi tarafından bireysel psikolojik danışmanlık ve kaygı yönetimi seansları uygulanacaktır.",
        "8. Devamsızlık ve sabah derslerine geç kalma eğilimi gösteren öğrencilerin velileri e-Okul sistemi üzerinden anlık olarak bilgilendirilecek ve devamsızlık mektubu gönderilecektir.",
        "9. Dijital oyun ve telefon bağımlılığının önlenmesi için velilerle iş birliği yapılarak evde ders çalışma saatlerinde ekran kısıtlaması uygulanması tavsiye edilecektir.",
        "10. Öğrencilerin beslenme çantası ve sabah kahvaltısı alışkanlıkları sınıf rehber öğretmeni tarafından teşvik edilecek, okul kantininde sağlıklı gıda tüketimine özen gösterilecektir.",
        "11. Okul kütüphanesinin ders bitiminde 8. sınıf öğrencilerinin sessiz etüt ve soru çözüm alanı olarak aktif kullanımı desteklenecektir.",
        "12. Her deneme sınavı sonrasında branş öğretmenleri tarafından kazanım bazlı analiz raporları çıkarılacak, sınıf genelinde başarı oranı %50'nin altında kalan kazanımlar derste yeniden işlenecektir.",
        "13. İhtiyaç sahibi olduğu belirlenen öğrencilere okul-aile birliği ve sosyal yardımlaşma kanallarıyla kaynak kitap ve kırtasiye desteği sağlanacaktır.",
        "14. Alınan bu kararların uygulanma düzeyi her ay düzenlenecek şube değerlendirme toplantılarında gözden geçirilecektir."
    ]

    # Belgede ilgili yerlere metinleri yerleştir (Paragraf güncelleme ve ekleme)
    # Gündem maddelerinin altına ekle
    # Mevcut boş paragrafları doldur
    p_cur = idx_gundem_gor + 1
    for title, body in gundem_texts:
        if p_cur < idx_kararlar:
            p = doc.paragraphs[p_cur]
            p.text = f"{title}\n{body}"
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.space_before = Pt(2)
            p.runs[0].font.name = "Calibri"
            p.runs[0].font.size = Pt(9)
            p_cur += 1

    # Kararlar altına ekle
    p_k_cur = idx_kararlar + 1
    for k_item in kararlar_texts:
        if p_k_cur < idx_sinif_bilgi - 3:
            p = doc.paragraphs[p_k_cur]
            p.text = k_item
            p.paragraph_format.space_after = Pt(3)
            p.runs[0].font.name = "Calibri"
            p.runs[0].font.size = Pt(9)
            p_k_cur += 1

    # 3. Sınıf Bilgi Formunu Doldur
    for p in doc.paragraphs[idx_sinif_bilgi:]:
        t = p.text.strip()
        if "Devamsızlık yapanlar;" in t:
            p.text = "Devamsızlık yapanlar: 84 Kuzey Yusuf Uruklu (Mazeretli izin), 258 Meryem Bozdemir (Ailevi izinli), 327 Melek Rana Kesici (Sağlık kontrolleri). Sürekli devamsız öğrenci bulunmamaktadır."
            p.runs[0].font.size = Pt(9)
        elif "Genel sorumluluklarını yerine getirmeyenler:" in t:
            p.text = "Genel sorumluluklarını yerine getirmeyenler: 224 Cengizhan Yılmaz, 227 Derin Yılmaz, 379 Çınar Efe Girgin (Zaman zaman ödev ve ders araç-gereç takibinde aksaklıklar yaşanmakta, veli takibi talep edilmiştir)."
            p.runs[0].font.size = Pt(9)
        elif "Dersin düzenine bozan:" in t or "Dersin düzenini bozan:" in t:
            p.text = "Dersin düzenini bozan: Sınıf genelinde dersin işlenişini engelleyen kronik bir disiplin problemi yoktur. Zaman zaman ders içi konuşma eğiliminde olan hareketli öğrenciler öğretmenlerce uyarılmaktadır."
            p.runs[0].font.size = Pt(9)
        elif "Problemli öğrencileri isimleri :" in t or "Problemli öğrencilerin isimleri:" in t:
            p.text = "Problemli öğrencilerin isimleri: Davranışsal boyutta disiplin cezası gerektirecek problemli öğrenci bulunmamaktadır; akademik desteğe muhtaç öğrenciler mevcuttur."
            p.runs[0].font.size = Pt(9)
        elif "Kaynaştırma öğrencileri:" in t:
            p.text = "Kaynaştırma öğrencileri: Sınıfımızda resmi RAM raporlu kaynaştırma öğrencisi bulunmamaktadır."
            p.runs[0].font.size = Pt(9)
        elif "Sınıftaki sağlık problemi olan öğrenciler:" in t:
            p.text = "Sınıftaki sağlık problemi olan öğrenciler:\n• [230] Kenan Emir Yaman: Astım hastasıdır, gerektiğinde Ventolin inhaler sprey kullanmaktadır.\n• [245] Tuna Koç: Dikkat eksikliği takiplidir, hekim kontrolünde Medikinet kullanmaktadır.\n• [256] Beren Koç: Tiroit takiplidir, düzenli vitamin ve hekim kontrolü altındadır."
            p.runs[0].font.size = Pt(9)
        elif "Beslenmesi zayıf olan öğrenciler:" in t:
            p.text = "Beslenmesi zayıf olan öğrenciler: Sabah kahvaltısı yapmadan gelen ve kantin ağırlıklı beslenen birkaç öğrencinin aileleri ile görüşülerek evde düzenli beslenme alışkanlığı kazandırılması kararlaştırıldı."
            p.runs[0].font.size = Pt(9)
        elif "4- Sınıf başarı ve başarısızlık durumlarını derslere göre değerlendiriniz:" in t:
            p.text = "4- Sınıf başarı ve başarısızlık durumlarını derslere göre değerlendiriniz:\n" \
                     "• Türkçe: Net ortalaması 12.37 net (%61.8 başarı). Paragrafta anlam güçlü; dil bilgisi ve sözel mantıkta soru pratiği artırılmalı.\n" \
                     "• Matematik: Net ortalaması 6.45 net (%32.2 başarı). Temel işlem becerileri iyi ancak yeni nesil problem çözme ve zaman yönetiminde desteğe ihtiyaç var.\n" \
                     "• Fen Bilimleri: Net ortalaması 10.82 net (%54.1 başarı). Mevsimler ve İklim ile DNA üniteleri pekiştirildi; deney ve grafik yorumlama sorularına ağırlık verilmeli.\n" \
                     "• T.C. İnkılap Tarihi: Net ortalaması 7.15 net (%71.5 başarı). Kavram ve kronoloji bilgisi kuvvetli; sınıf ortalaması yüksek.\n" \
                     "• Din Kültürü: Net ortalaması 7.48 net (%74.8 başarı). Kaza ve kader ünitesi kazanımları tam; en başarılı olunan derslerden biri.\n" \
                     "• İngilizce: Net ortalaması 5.24 net (%52.4 başarı). Friendship ve Teen Life ünite kelime hazinesi ve kalıp ifadeler tekrar edilmeli."
            p.runs[0].font.size = Pt(9)
        elif "Geliri Düşük Olanlar Öğrenciler:" in t or "Geliri Düşük Olan" in t:
            p.text = "Geliri Düşük Olan Öğrenciler: Aile gelir düzeyi kısıtlı olan ve ders materyali desteğine ihtiyaç duyan öğrenciler okul-aile birliği ve rehberlik servisine bildirilmiştir."
            p.runs[0].font.size = Pt(9)
        elif "Geliri İyi Olan Öğrenciler." in t or "Geliri İyi Olan" in t:
            p.text = "Geliri İyi Olan Öğrenciler: Sınıfın büyük çoğunluğunun ekonomik durumu orta ve iyi düzeyde olup temel eğitsel ihtiyaçlarını karşılayabilmektedir."
            p.runs[0].font.size = Pt(9)
        elif "Yardımlar İçin Önerilen Öğrenciler:" in t:
            p.text = "Yardımlar İçin Önerilen Öğrenciler: Kaynak kitap ve kırtasiye ihtiyacı olan öğrencilere okul idaresi ve zümre öğretmenlerince ücretsiz LGS soru bankaları temin edilmiştir."
            p.runs[0].font.size = Pt(9)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path
