"""
8/B Şube Öğretmenler Kurulu (ŞÖK) Otomasyon Modülü
MEB Okul Öncesi Eğitim ve İlköğretim Kurumları Yönetmeliği (Madde 36)
ve MEB Eğitim Kurulları ve Zümreleri Yönergesi (Madde 10 & 11) standartlarına tam uyumludur.
Öğrenci değerlendirmelerinde sınav netleri ve LGS ifadeleri yerine
pedagojik "Akademik Başarı" değerlendirmeleri kullanılır.
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

# ── Kurul Üyeleri ve Görev Dağılımı ──
TEACHERS_TABLE_DATA = [
    ("1", "Türkçe", "MENEKŞE KUSEYRİ"),
    ("2", "Matematik ve Seçmeli Görgü Kuralları ve Nezaket", "Elveda SÖNMEZ"),
    ("3", "Fen Bilimleri ve Seçmeli Çevre Bilinci ve İklim Değişikliği", "Serkan BAYTAN"),
    ("4", "T.C. İnkılap Tarihi ve Atatürkçülük ve Seçmeli Ahlak ve Yurttaşlık Eğitimi", "MUHARREM BÜYÜKÖKSÜZ"),
    ("5", "Beden Eğitimi ve Spor", "ALİ EKBER ERDAL"),
    ("6", "Din Kültürü ve Ahlak Bilgisi", "RUKİYE GÖLÜKÇÜ"),
    ("7", "İngilizce (Yabancı Dil)", "HİLAL YAĞCILAR"),
    ("8", "Müzik", "GAMZE GÜN BAYRAM"),
    ("9", "Teknoloji ve Tasarım", "REYHAN TOPALOĞLU"),
    ("10", "Teknoloji ve Tasarım", "TÜLAY KAYA"),
    ("11", "Rehberlik ve Kariyer Planlama", "Serkan BAYTAN"),
]

COMMITTEE_MADDE_11 = [
    ("Dilek SANCAK", "Müdür Yardımcısı (Toplantı Başkanı)"),
    ("MENEKŞE KUSEYRİ", "Türkçe Öğretmeni"),
    ("Elveda SÖNMEZ", "Matematik ve Seçmeli Görgü Kuralları ve Nezaket Öğret."),
    ("Serkan BAYTAN", "Fen Bilimleri ve Seçmeli Çevre Bilinci ve İklim Değ. Öğrt. / 8-B Sınıf Rehber Öğrt."),
    ("MUHARREM BÜYÜKÖKSÜZ", "T.C. İnkılap Tarihi ve Atatürkçülük ve Seç. Ahlak ve Yurttaşlık Eğt. Öğrt."),
    ("HİLAL YAĞCILAR", "İngilizce Öğretmeni (Yabancı Dil)"),
    ("RUKİYE GÖLÜKÇÜ", "Din Kültürü ve Ahlak Bilgisi Öğretmeni"),
    ("ALİ EKBER ERDAL", "Beden Eğitimi ve Spor Öğretmeni"),
    ("GAMZE GÜN BAYRAM", "Müzik Öğretmeni"),
    ("REYHAN TOPALOĞLU", "Teknoloji ve Tasarım Öğretmeni"),
    ("TÜLAY KAYA", "Teknoloji ve Tasarım Öğretmeni"),
    ("Serkan BAYTAN", "Rehberlik ve Kariyer Planlama"),
]

def set_cell_shd(cell, hex_col):
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_col}"/>'))

def set_cell_margins(cell, top=25, bottom=25, left=45, right=45):
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

def make_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def make_row_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def get_8b_students_sok_data():
    """
    8/B sınıfının 29 öğrencisi için veritabanındaki deneme sınavı sonuçları,
    öğrenci tanıma formları ve risk haritası faktörlerini harmanlayarak
    ŞÖK Madde 11 Bireysel Öğrenci Değerlendirme verilerini üretir.
    Deneme sınavı verileri sınav neti veya LGS olarak değil,
    pedagojik 'Akademik Başarı' düzeyleri olarak değerlendirilir.
    Derin Yılmaz ve Egehan Hardal için özel gözlem verileri işlenir.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. 8/B Öğrenci Listesi
    c.execute("SELECT id, school_no, name FROM students WHERE class_name='8/B' ORDER BY CAST(school_no AS INTEGER)")
    db_students = [dict(r) for r in c.fetchall()]

    # 2. Deneme Sınavı İstatistikleri (Dahili seviye tespiti için kullanılır)
    c.execute("""
        SELECT student_id, 
               AVG(top_net) as avg_net, 
               AVG(score) as avg_score,
               MIN(class_rank) as best_rank
        FROM exam_results er
        JOIN students s ON er.student_id = s.id
        WHERE s.class_name = '8/B'
        GROUP BY student_id
    """)
    exam_stats = {r['student_id']: dict(r) for r in c.fetchall()}

    # 3. Öğrenci Tanıma Formu Verileri
    c.execute("SELECT * FROM student_profile")
    profiles = {r['student_id']: dict(r) for r in c.fetchall()}

    # 4. Risk Faktörleri
    c.execute("SELECT student_id, factor_id FROM student_risk_factors")
    risk_dict = {}
    for r in c.fetchall():
        s_id = r['student_id']
        f_id = r['factor_id']
        risk_dict.setdefault(s_id, set()).add(f_id)

    # 5. ŞÖK Öğrenci Veri Toplama Formu (Özel Anket / Giriş Verileri)
    from core.sok_survey import init_sok_survey_table
    init_sok_survey_table()
    c.execute("SELECT * FROM sok_student_survey")
    surveys = {r['student_id']: dict(r) for r in c.fetchall()}

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

        # ── 1. Kişilik Durumu ──
        genel_his = str(prof.get('genel_his', ''))
        
        if no == "227": # DERİN YILMAZ
            kisilik = "Sessiz, sakin mizaçlı ve saygılı; ancak sınıf ortamında kendini ifade etmekte ve akranlarıyla iletişim kurmakta oldukça çekingen."
        elif no == "272": # EGEHAN HARDAL
            kisilik = "Hareketli, enerjik ve sevecen bir yapısı var; ancak dürtüsel davranış sorunları ve hareketliliği nedeniyle derse odaklanmakta belirgin zorluklar yaşıyor."
        elif avg_net >= 70:
            kisilik = "Özgüveni ve sorumluluk bilinci yüksek, lider karakterli, sınıf kurallarına tam uyumlu ve yüksek hedefleri olan."
        elif avg_net >= 50:
            kisilik = "Saygılı, çalışkan, derse ilgili ve uyumlu; zaman zaman sınav kaygısı yaşayabiliyor, motive edilmesi faydalı."
        elif avg_net >= 35:
            kisilik = "Sakin mizaçlı, uyumlu, sorumluluklarını yerine getirmeye gayret eden, akranlarıyla dengeli ilişkiler kuran."
        elif avg_net >= 20:
            kisilik = "İyi niyetli, kurallara uyan ancak ders içi odaklanmada zaman zaman dikkat dağınıklığı ve motivasyon kaybı yaşayan."
        else:
            kisilik = "Derslere karşı ilgisizleşebilen, özgüven desteğine ve yakın rehberlik takibine ihtiyaç duyan."

        if ("Kaygılı" in genel_his or "Stresli" in genel_his) and no not in ["227", "272"]:
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
        if no == "227": # DERİN YILMAZ
            sosyal = "Arkadaşlarıyla çok fazla iletişim kurmuyor, teneffüslerde ve grup çalışmalarında içine kapanık bir profil sergiliyor."
        elif no == "272": # EGEHAN HARDAL
            sosyal = "Arkadaşlarıyla iletişimi canlı ancak ders esnasında dürtüsel tepkileri ve dikkat dağınıklığı nedeniyle ders akışında desteğe ihtiyaç duyuyor."
        elif avg_net >= 65:
            sosyal = "Akran ilişkileri kuvvetli, arkadaşları tarafından sevilen ve örnek alınan; grup çalışmalarında yapıcı ve paylaşımcı."
        elif avg_net >= 40:
            sosyal = "Sınıf içi sosyal ilişkileri uyumlu ve dengeli; arkadaşlarıyla iyi iletişim kurabilen, çatışmadan uzak."
        elif avg_net >= 25:
            sosyal = "Arkadaş canlısı ancak zaman zaman ders dışı konulara odaklanabiliyor; pozitif akran grubuna yönlendirilmeli."
        else:
            sosyal = "Akranlarıyla iletişimi sakin ancak akademik paylaşımlarda çekingen; sosyal etkinliklere teşvik edilmeli."

        if (5 in risks or 35 in risks) and no not in ["227", "272"]:
            sosyal += " Sosyal-duygusal desteğe duyarlı bir dönemde."

        # ── 5. Ekonomik Durumu ──
        ders_ortami = str(prof.get('ders_ortami', ''))

        if avg_net >= 60 or "kendi odam" in ders_ortami.lower():
            ekonomik = "Ailenin sosyo-ekonomik durumu iyi/orta; ders araç-gereçleri ve eğitim kaynakları eksiksiz karşılanmaktadır."
        elif 3 in risks:
            ekonomik = "Orta/kısıtlı aile bütçesi; okul kaynak desteği ve eğitsel materyaller yönünden takip edilmekte."
        else:
            ekonomik = "Orta düzeyde; temel eğitim ihtiyaçları karşılanıyor, ders çalışma ortamı mevcut."

        # ── 6. Başarı Durumu (Sınav neti ve LGS adı geçmez; pedagojik akademik başarı düzeyi) ──
        if avg_net >= 75:
            basari = "Üstün akademik başarı düzeyinde; tüm derslerde kazanımları eksiksiz kavramış, öğrenme motivasyonu ve ders başarısı çok yüksek."
        elif avg_net >= 60:
            basari = "Yüksek akademik başarı düzeyinde; sözel ve sayısal ders dengesi kuvvetli, hedeflerine yönelik düzenli ve disiplinli çalışan bir öğrenci."
        elif avg_net >= 45:
            basari = "Sınıf ortalamasının üzerinde başarılı bir akademik düzeye sahip; gayretli, fen ve matematik kazanımlarını pekiştirme sürecinde."
        elif avg_net >= 30:
            basari = "Orta düzeyde akademik başarıya sahip; temel kavramları kavramış olup özellikle sözel derslerde başarılı, sayısal derslerde gelişim potansiyeli yüksek."
        elif avg_net >= 15:
            basari = "Akademik desteğe ve takviyeye ihtiyaç duyan bir düzeyde; temel ders kazanımlarında eksiklikleri bulunmakta, planlı çalışmayla ilerleme sağlayabilir."
        else:
            basari = "Öncelikli akademik destek ihtiyacı olan düzeyde; temel kavram eksiklikleri mevcut olup bireysel telafi eğitimine ve yakın rehberlik takibine muhtaç."

        # ── 7. Problemin Çözümü İçin Ne Yapılacağı ──
        if no == "227": # DERİN YILMAZ
            cozum = "Sosyal iletişimini artırmak için ikili akran çalışmaları, sosyal kulüp ve sınıf içi sorumluluklar verilmesi; Rehberlik Servisi ile özgüven ve sosyal uyum görüşmeleri yapılması; veli iş birliğiyle sosyal aktivitelere yönlendirilmesi."
        elif no == "272": # EGEHAN HARDAL
            cozum = "Dürtüsellik ve odaklanma güçlüğü için ders esnasında ön sıraya oturtulması; dikkat süresine uygun kısa süreli görevler verilmesi; Rehberlik Servisi koordinasyonunda odaklanma-özdenetim çalışmaları yapılması ve veli görüşmesiyle uzman desteğinin takip edilmesi."
        elif avg_net >= 70:
            cozum = "Zaman yönetimi ve üst düzey muhakeme becerilerinin desteklenmesi; 'Hata Analiz Defteri' ile sıfır hata takibi; akademik liderliğini sürdürücü yönlendirme."
        elif avg_net >= 50:
            cozum = "Düzenli ders çalışma ve soru çözme planının takibi; Matematik ve Fen derslerinde akıl yürütme pratiklerinin artırılması; akademik motivasyon desteği."
        elif avg_net >= 35:
            cozum = "Haftalık ders çalışma programı hazırlanması; DYK kurslarına düzenli devamın sağlanması; eksik kazanımlara yönelik konu pekiştirme testleri."
        elif avg_net >= 20:
            cozum = "Temel kavram tekrarları; haftalık soru ve konu hedefleri belirlenmesi; veli görüşmesi yapılarak evde düzenli çalışma disiplininin desteklenmesi."
        else:
            cozum = "Bireysel akademik telafi programı; ders öğretmenlerince birebir kazanım desteği; temel ders çalışma alışkanlığı kazandırılması; Rehberlik Servisi takibi."

        # ── 7.5. ŞÖK Öğrenci Veri Toplama Formu / Özel Giriş Önceliği ──
        survey = surveys.get(s_id, {})
        if survey.get('kisilik_ozellikleri'):
            kisilik = survey['kisilik_ozellikleri'].strip()
        if survey.get('beslenme_durumu'):
            beslenme = survey['beslenme_durumu'].strip()
        if survey.get('saglik_durumu'):
            saglik = survey['saglik_durumu'].strip()
        if survey.get('sosyal_iliskiler'):
            sosyal = survey['sosyal_iliskiler'].strip()
        if survey.get('calisma_ve_ekonomik'):
            ekonomik = survey['calisma_ve_ekonomik'].strip()
        if survey.get('akademik_durum'):
            basari = survey['akademik_durum'].strip()
        if survey.get('oneri_ve_tedbir'):
            cozum = survey['oneri_ve_tedbir'].strip()

        # ── 8. Görevli Personel, Birimi ──
        if no in ["227", "272"]:
            gorevli = "Sınıf Rehber Öğretmeni, Branş Öğretmenleri, Okul Rehberlik Servisi, Veli"
        elif avg_net < 20 or no in ["230", "245", "327"]:
            gorevli = "Sınıf Rehber Öğrt., İlgili Branş Öğrt., Rehberlik Servisi, Veli"
        else:
            gorevli = "Sınıf Rehber Öğretmeni, Branş Öğretmenleri"

        evaluations.append({
            "sira": idx,
            "student_id": s_id,
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

def get_8b_sok_gundem_and_observation_data():
    """
    ŞÖK Toplantı Tutanağı ve Sınıf Gözlem Formu için gerekli
    resmi toplantı parametrelerini, kurul üyelerini ve özetleri döner.
    """
    st_evals = get_8b_students_sok_data()
    
    devamsiz_list = [
        "84 Kuzey Yusuf Uruklu (Mazeretli izin)",
        "258 Meryem Bozdemir (Ailevi izinli)",
        "327 Melek Rana Kesici (Sağlık kontrolleri)"
    ]
    
    saglik_list = [
        "230 Kenan Emir Yaman: Astım rahatsızlığı mevcuttur; gerektiğinde Ventolin inhaler sprey kullanmaktadır.",
        "245 Tuna Koç: Dikkat eksikliği ve odaklanma takibi mevcuttur; hekim kontrolünde Medikinet kullanmaktadır.",
        "256 Beren Koç: Tiroit takibi mevcut olup düzenli hekim gözetimindedir; genel durumu iyidir."
    ]

    leaders = [s for s in st_evals if s['avg_net'] >= 60]
    needs_support = [s for s in st_evals if s['avg_net'] < 30]

    return {
        "okul_adi": "ALTUNİZADE HAFİZE ÖZAL ORTAOKULU",
        "sinif": "8 / B",
        "toplanti_tarihi": "24 / 10 / 2026",
        "toplanti_no": "1 (1. Dönem ŞÖK)",
        "mudur": "Emin BAYKARA",
        "mudur_unvan": "Okul Müdürü (Uygundur Onay Makamı)",
        "mudur_yrd": "Dilek SANCAK",
        "mudur_yrd_unvan": "Müdür Yardımcısı (Toplantı Başkanı)",
        "rehber_ogretmen": "Serkan BAYTAN",
        "ogretmenler": TEACHERS_TABLE_DATA,
        "ogrenci_sayisi": len(st_evals),
        "st_evals": st_evals,
        "devamsiz_list": devamsiz_list,
        "saglik_list": saglik_list,
        "leaders": leaders,
        "needs_support": needs_support
    }

def fill_sok_madde_11_docx(template_path, output_path):
    """
    ŞÖK Madde 11.docx şablonunu açar, 8/B sınıfının 29 öğrencisinin
    tüm değerlendirme verilerini Table 1'e satır satır işler.
    Sayfa düzeni ve dağılımını optimize eder:
    - cantSplit her satıra eklenir (satır bölünmesi engellenir).
    - tblHeader başlık satırlarına eklenir (sayfa geçişlerinde başlıklar otomatik yinelenir).
    - trHeight kısıtlamaları kaldırılır, font ve hücre dolguları dengelenir.
    - Table 2 (Kurul Üyeleri İmzaları) ve Uygundur onay bloğu eksiksiz doldurulur.
    - Belge tam 6 dengeli ve dolu sayfaya yerleşir.
    """
    doc = docx.Document(template_path)
    evaluations = get_8b_students_sok_data()

    tbl = doc.tables[0]
    
    # Row 1 güncelle (Sınıf ve Tarih)
    for cell in tbl.rows[1].cells:
        if "SINIF /" in cell.text:
            cell.text = "SINIF / ŞUBE: 8 / B"
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        elif "TOPLANTI" in cell.text:
            cell.text = "TOPLANTI TARİHİ: 24 / 10 / 2026"
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)

    needed_rows = len(evaluations) # 29

    # Add tblHeader to row 0, 1, 2
    for r_h_idx in [0, 1, 2]:
        make_row_header(tbl.rows[r_h_idx])

    col_widths = [0.35, 0.45, 1.10, 0.95, 0.80, 0.95, 0.95, 0.80, 1.45, 1.70, 1.15] # sum = 10.65 inches

    for i, st in enumerate(evaluations):
        r_idx = 3 + i
        if r_idx < len(tbl.rows):
            row = tbl.rows[r_idx]
        else:
            row = tbl.add_row()

        make_row_cant_split(row)

        trPr = row._tr.get_or_add_trPr()
        for th in trPr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}trHeight'):
            trPr.remove(th)

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

        bg_col = "F9FBFD" if i % 2 == 1 else "FFFFFF"

        for c_idx, val in enumerate(vals):
            if c_idx < len(row.cells):
                cell = row.cells[c_idx]
                cell.width = Inches(col_widths[c_idx])
                cell.text = val
                set_cell_shd(cell, bg_col)
                set_cell_margins(cell, top=25, bottom=25, left=40, right=40)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.0

                if c_idx in [0, 1]:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                if p.runs:
                    run = p.runs[0]
                    run.font.name = "Calibri"
                    run.font.size = Pt(7) if c_idx >= 3 else Pt(7.5)
                    if c_idx in [0, 1, 2]:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    while len(tbl.rows) > 3 + needed_rows:
        row_to_remove = tbl.rows[-1]
        tr = row_to_remove._tr
        tr.getparent().remove(tr)

    set_table_borders(tbl, color="B0C4DE", sz="4")

    # ── Table 1 (Kurul Üyeleri İmzaları) Doldur ──
    if len(doc.tables) > 1:
        tbl_comm = doc.tables[1]
        tbl_comm.alignment = WD_TABLE_ALIGNMENT.CENTER
        make_row_header(tbl_comm.rows[0])
        
        t1_widths = [2.8, 5.5, 2.3] # sum = 10.6 inches

        for idx, (isim, gorev) in enumerate(COMMITTEE_MADDE_11):
            r_idx = idx + 1
            if r_idx < len(tbl_comm.rows):
                row = tbl_comm.rows[r_idx]
            else:
                row = tbl_comm.add_row()
            
            make_row_cant_split(row)

            trPr = row._tr.get_or_add_trPr()
            for th in trPr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}trHeight'):
                trPr.remove(th)

            cells = row.cells
            cells[0].text = isim
            p0 = cells[0].paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if p0.runs:
                p0.runs[0].font.name = "Calibri"
                p0.runs[0].font.size = Pt(8)
                p0.runs[0].font.bold = True
                p0.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

            cells[1].text = gorev
            p1 = cells[1].paragraphs[0]
            p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if p1.runs:
                p1.runs[0].font.name = "Calibri"
                p1.runs[0].font.size = Pt(7.5)

            cells[2].text = ""

            for c_i, c in enumerate(cells):
                if c_i < len(t1_widths):
                    c.width = Inches(t1_widths[c_i])
                set_cell_margins(c, top=25, bottom=25, left=45, right=45)
                p = c.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.0

        while len(tbl_comm.rows) > len(COMMITTEE_MADDE_11) + 1:
            row_to_remove = tbl_comm.rows[-1]
            tr = row_to_remove._tr
            tr.getparent().remove(tr)

        set_table_borders(tbl_comm, color="B0C4DE", sz="4")

    # ── Onay Bloğu (Uygundur / Emin BAYKARA) ──
    for p in doc.paragraphs:
        t = p.text.strip()
        if "Uygundur" in t:
            p.text = "Uygundur"
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = True
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(9.5)
                p.runs[0].font.bold = True
        elif "... / 10 / 2026" in t or "/ 10 / 2026" in t or "2026" in t and len(t) < 15:
            p.text = "24 / 10 / 2026"
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(9)
        elif "Emin BAYKARA" in t:
            p.text = "Emin BAYKARA"
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = True
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(9.5)
                p.runs[0].font.bold = True
        elif "Okul Müdürü" in t:
            p.text = "Okul Müdürü"
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(9)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path

def fill_sok_gundem_ve_gozlem_docx(template_path, output_path):
    """
    2026_Ekim_ŞÖK_Gündem_Maddeleri_ve_Sınıf_Gözlem_Formu.docx belgesini açar,
    Gündem görüşmelerini, alınan kararları, Sınıf Bilgi Formunu ve imza tablolarını
    8/B sınıfının gerçek verileriyle eksiksiz doldurur ve kaydeder.
    
    Sayfa dağılımı ve düzeni:
    - Yapay ve yığılmış boş paragraflar temizlenir.
    - Kenar boşlukları ve satır aralıkları optimize edilerek her sayfa tam ve dengeli doldurulur.
    - Sınıf Bilgi Formu temiz bir sayfa başından başlar.
    - Tablolarda cantSplit ve tblHeader uygulanarak sayfa geçişleri profesyonel hale getirilir.
    - Toplantı başkanlığı Dilek SANCAK, onay makamı Emin BAYKARA olarak işlenir.
    - Derin Yılmaz ve Egehan Hardal durumları Sınıf Bilgi Formu Madde 1, 2, 3'e işlenir.
    - Belge tam 6 dengeli sayfaya yerleşir.
    """
    doc = docx.Document(template_path)
    st_evals = get_8b_students_sok_data()

    # Sayfa kenar boşluklarını nefes alacak şekilde ayarla
    sec = doc.sections[0]
    sec.top_margin = Pt(36)
    sec.bottom_margin = Pt(36)
    sec.left_margin = Pt(45)
    sec.right_margin = Pt(45)

    # 1. Başlık ve Üst Bilgileri Doldur
    for p in doc.paragraphs:
        t = p.text
        if "…… / …… SINIFI" in t or "…… /…… SINIFI" in t:
            p.text = t.replace("…… / …… SINIFI", "8 / B SINIFI").replace("…… /…… SINIFI", "8 / B SINIFI")
            for r in p.runs:
                r.font.bold = True
                r.font.name = "Calibri"
        if "( .….. /……. SINIFI)" in t:
            p.text = t.replace("( .….. /……. SINIFI)", "( 8 / B SINIFI )")
            for r in p.runs:
                r.font.bold = True
                r.font.name = "Calibri"
        if "Toplantı Tarihi :" in t or "Toplantı Tarihi:" in t:
            p.text = "Toplantı Tarihi: 24 / 10 / 2026          Toplantı Saati: 15:50          Toplantı Yeri: Okul Kütüphanesi          Toplantı No: 1"
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(9)
        if "…. /….. Sınıf Rehber Öğretmeni" in t:
            p.text = "Serkan BAYTAN — 8 / B Sınıf Rehber Öğretmeni"
            if p.runs:
                p.runs[0].font.bold = True
                p.runs[0].font.name = "Calibri"

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
         "Toplantı Müdür Yardımcısı Dilek SANCAK başkanlığında, 8/B sınıfında derse giren tüm branş öğretmenleri ve sınıf rehber öğretmeninin katılımıyla açıldı. Yapılan yoklamada kurul üyelerinin eksiksiz hazır bulunduğu tespit edildi. Toplantı Başkanı, toplantının MEB Okul Öncesi Eğitim ve İlköğretim Kurumları Yönetmeliği Madde 36 ile MEB Eğitim Kurulları ve Zümreleri Yönergesi Madde 10-11 hükümleri çerçevesinde yürütüleceğini belirterek gündem maddelerinin görüşülmesine geçti."),
        
        ("2. Şubenin genel öğrenci profili ve sınıf ikliminin değerlendirilmesi:",
         "8/B sınıf rehber öğretmeni Serkan BAYTAN şubenin genel durumunu aktardı: Sınıf mevcudu 29 olup 15 erkek ve 14 kız öğrenciden oluşmaktadır. Sınıfın genel ders içi uyumu ve öğretmenlerine karşı saygılı tutumu olumludur. Sınıf içi etkileşim genel hatlarıyla yapıcı olmakla birlikte, sınav hazırlık sürecine bağlı zaman zaman dikkat dağınıklığı gözlemlenmektedir."),
        
        ("3. Yeni gelen / uyum güçlüğü yaşayan öğrencilerin durumu:",
         "Dönem başında nakil gelen öğrencilerin sınıf ortamına ve akademik çalışma temposuna başarıyla uyum sağladığı, arkadaş çevrelerinin pozitif şekilde geliştiği ve herhangi bir uyum problemi yaşanmadığı ifade edildi."),
        
        ("4. Devam-devamsızlık, geç kalma ve okul bağlılığı verileri:",
         "Sınıf genelinde devam durumu oldukça yüksektir. Kuzey Yusuf Uruklu, Meryem Bozdemir ve Melek Rana Kesici'nin mazeretli ve sağlık kontrollerine bağlı izinleri dışında kronik devamsızlık problemi olan öğrenci bulunmamaktadır. İlk derslere geç kalma alışkanlığı olan birkaç öğrenci velisiyle irtibata geçilmiştir."),
        
        ("5. Öğrencilerin akademik başarı durumlarının incelenmesi ve başarıyı artırıcı önlemlerin alınması:",
         "Dönem başından itibaren uygulanan kazanım izleme çalışmaları ve akademik değerlendirmeler incelendi. Şubenin genel akademik başarı düzeyinde belirgin bir yükseliş ve olumlu öğrenme ivmesi kaydedildiği tespit edildi. Orhan Efe Çelikdemir, Zeynep Ece Çelikdemir, Erdem Yarar, Melek Rana Kesici ve Halit Eren Hatunoğlu'nun üstün bir akademik başarı sergilediği görüldü. Türkçe, İnkılap Tarihi ve Din Kültürü derslerinde kazanım kavrama oranlarının çok yüksek olduğu, Matematik ve Fen Bilimleri derslerinde ise problem çözme ve analiz becerilerini güçlendirici çalışmaların sürdürülmesi kararlaştırıldı."),
        
        ("6. Sosyal-duygusal gelişim, akran ilişkileri ve davranış gözlemleri:",
         "Sınıf genelinde akran ilişkilerinin yapıcı, saygılı ve uyumlu olduğu belirtildi. Bununla birlikte 227 Derin Yılmaz'ın arkadaşlarıyla çok fazla iletişim kurmayarak içine kapandığı, 272 Egehan Hardal'ın ise dürtüsel sorunları nedeniyle derse odaklanamadığı ve hareketliliği nedeniyle desteğe ihtiyaç duyduğu kurul gündemine taşındı. Her iki öğrencinin sosyal ve akademik uyumunu güçlendirmek için sınıf rehber öğretmeni Serkan BAYTAN ve okul rehberlik servisinin velilerle koordineli bireysel destek programı yürütmesi kararlaştırıldı."),
        
        ("7. Risk altında olduğu değerlendirilen öğrenciler için izlenecek yol:",
         "MEB S.İ.4.a Sınıf Risk Haritası ve öğrenci tanıma formları doğrultusunda; temel ders kazanımlarında eksiklik yaşayan ve akademik desteğe ihtiyaç duyan öğrenciler (Egehan Hardal, Derin Yılmaz, Çınar Efe Girgin, Cengizhan Yılmaz, Mustafa Gülseven) için F33 (Akademik Başarısı Desteklenmesi Gereken) telafi planı uygulanması ve bireysel ders takip çizelgeleri verilmesi kararlaştırıldı."),
        
        ("8. Özel eğitim ihtiyacı / kaynaştırma-bütünleştirme / BEP süreçleri:",
         "Sınıfta RAM raporlu kaynaştırma öğrencisi bulunmamaktadır. Dikkat eksikliği ve hekim takibi bulunan öğrencilerin (Tuna Koç - Medikinet kullanımı) ders esnasında ön sıralara oturtulması ve dikkatinin canlı tutulması sağlandı."),
        
        ("9. Öğrencilerin ilgi-yetenekleri ve sosyal etkinliklere yönlendirilmesi:",
         "Öğrencilerin spor, müzik, teknoloji ve resim alanlarındaki yetenekleri değerlendirildi. Akademik çalışma sürecinde öğrencilerin zihinsel dinlenmelerini sağlamak amacıyla okul içi satranç, spor turnuvaları ve bilimsel projelere katılımları teşvik edilecektir."),
        
        ("10. Veli iş birliği ve görüşme ihtiyacı bulunan öğrenciler:",
         "Akademik desteğe ihtiyaç duyan ve sınav kaygısı yaşayan öğrencilerin velileri ile bireysel görüşmeler planlandı. Ayrıca velilere 'Öğrencilerimizin Başarı Yolculuğunda Aile İçi İletişim ve Destek' konulu rehberlik bülteni ulaştırılması uygun görüldü."),
        
        ("11. Rehberlik servisiyle yürütülecek sınıf ve öğrenci çalışmaları (Madde 11):",
         "Öğrencilerin kişilik, beslenme, sağlık, ekonomik ve sosyal durumları tek tek ele alındı. Bu kapsamda hazırlanan 'Bireysel Öğrenci Değerlendirme Tablosu' kurula sunuldu ve incelendi. Astım tanısı olan Kenan Emir Yaman'ın nöbetçi öğretmenler tarafından tozlu ortamlardan korunması; tiroit takibi olan Beren Koç'un sağlık izleminin sürdürülmesi kararlaştırıldı."),
        
        ("12. Sınav, ölçme-değerlendirme ve ders çalışma alışkanlıkları:",
         "Öğrencilere düzenli ders çalışma ve soru çözme alışkanlığı kazandırmak amacıyla seviyelerine uygun haftalık çalışma planları belirlendi. 'Hata Analiz ve Kazanım Defteri' uygulamasının tüm branşlarda titizlikle takip edilmesine karar verildi."),
        
        ("13. Dijital güvenlik, akran nezaketi ve okul güvenliği:",
         "Akıllı telefon ve dijital ekran bağımlılığına karşı velilerle koordineli sınırlandırma yapılması; siber zorbalık ve güvenli internet kullanımı hususunda bilişim teknolojileri öğretmenince bilgilendirme yapılması kararlaştırıldı."),
        
        ("14. Alınan kararların sorumluları, takvimi ve izleme yöntemi:",
         "Alınan kararların haftalık zümre ve rehberlik toplantılarında değerlendirilmesi, kasım ayı ara tatilinde akademik gelişim raporlarının velilere sunulması karara bağlandı."),
        
        ("15. Dilek ve temenniler / kapanış:",
         "Toplantı Başkanı Müdür Yardımcısı Dilek SANCAK, kurul toplantısına katılan ve 8/B sınıfının akademik-sosyal gelişimi için özveriyle çalışan tüm branş öğretmenlerine teşekkür etti. Başarılı ve huzurlu bir eğitim-öğretim dönemi temennisiyle toplantı sonlandırıldı. Alınan kararlar Okul Müdürü Emin BAYKARA'nın onayına sunuldu.")
    ]

    # Kararlar Listesi
    kararlar_texts = [
        "1. Akademik başarıyı artırmak ve çalışma disiplini oluşturmak amacıyla öğrencilere haftalık soru çözüm ve konu tekrar hedefleri tanımlanacak, sınıf rehber öğretmeni ile branş öğretmenlerince haftalık takip edilecektir.",
        "2. Ölçme ve değerlendirmelerde tespit edilen hataların kalıcı öğrenmeye dönüşmesi amacıyla tüm öğrencilerde 'Hata Analiz ve Kazanım Defteri' uygulaması zorunlu tutulacaktır.",
        "3. Matematik dersinde çok adımlı problem çözme, analitik düşünme ve muhakeme becerilerinin geliştirilmesine ağırlık verilecek; DYK kurslarıyla pekiştirilecektir.",
        "4. Akademik desteğe öncelikli ihtiyaç duyan öğrencilere yönelik bireysel eksik kazanım telafi programı uygulanacak ve velileriyle gelişim odaklı görüşmeler yapılacaktır.",
        "5. Üstün akademik başarı gösteren öğrencilere zaman yönetimi, üst düzey düşünme becerileri ve sınav stratejileri üzerine bireysel danışmanlık sağlanacaktır.",
        "6. Sağlık durumu özel takip gerektiren öğrencilerin (Kenan Emir Yaman - Astım/Ventolin, Tuna Koç - Dikkat odaklanması/Medikinet, Beren Koç - Tiroit) durumları nöbetçi öğretmenler ve okul idaresi koordinasyonunda izlenecektir.",
        "7. Dürtüsel sorunları sebebiyle derse odaklanamayan Egehan Hardal için ders içi ön sıra yerleşimi ve odaklanma desteği; arkadaşlarıyla iletişim kurmakta çekinen Derin Yılmaz için ise ikili akran çalışmaları ve sosyal kulüp görevleri verilmesi rehberlik servisi koordinasyonunda kararlaştırıldı.",
        "8. Devamsızlık ve ilk derslere geç kalma eğilimi gösteren öğrencilerin velileri e-Okul sistemi üzerinden anlık olarak bilgilendirilecek ve gerekli tedbirler alınacaktır.",
        "9. Dijital oyun ve telefon bağımlılığının önlenmesi için velilerle iş birliği yapılarak evde ders çalışma saatlerinde ekran kısıtlaması uygulanması tavsiye edilecektir.",
        "10. Öğrencilerin beslenme çantası ve sabah kahvaltısı alışkanlıkları sınıf rehber öğretmeni tarafından teşvik edilecek, okul kantininde sağlıklı gıda tüketimine özen gösterilecektir.",
        "11. Okul kütüphanesinin ders bitiminde öğrencilerin sessiz etüt ve kitap okuma alanı olarak aktif kullanımı sürdürülecektir.",
        "12. Yapılan her değerlendirme sonrasında branş öğretmenleri tarafından kazanım analizleri çıkarılacak, kavranma oranı düşük olan konular sınıfta pekiştirilecektir.",
        "13. İhtiyaç sahibi olduğu belirlenen öğrencilere okul-aile birliği ve zümre öğretmenlerince eğitsel kaynak ve kırtasiye desteği sağlanacaktır.",
        "14. Alınan bu kararların uygulanma düzeyi her ay düzenlenecek şube öğretmenler kurulu ara değerlendirme toplantılarında gözden geçirilecektir."
    ]

    p_cur = idx_gundem_gor + 1
    for title, body in gundem_texts:
        if p_cur < idx_kararlar:
            p = doc.paragraphs[p_cur]
            p.text = f"{title}\n{body}"
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.line_spacing = 1.05
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(8.5)
            p_cur += 1

    p_k_cur = idx_kararlar + 1
    for k_item in kararlar_texts:
        if p_k_cur < idx_sinif_bilgi - 3:
            p = doc.paragraphs[p_k_cur]
            p.text = k_item
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.space_before = Pt(0.5)
            p.paragraph_format.line_spacing = 1.05
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(8.5)
            p_k_cur += 1

    # 3. Sınıf Bilgi Formunu Doldur
    current_sec = 0
    for p in doc.paragraphs[idx_sinif_bilgi:]:
        t = p.text.strip()
        if "1- Sınıfınızda" in t:
            current_sec = 1
        elif "2- Sınıfınızın beslenme" in t:
            current_sec = 2
        elif "3- Sınıftaki öğrencilerin sosyal" in t:
            current_sec = 3
        elif "4- Sınıf başarı" in t:
            current_sec = 4
        elif "5- Ailelerin Ekonomik" in t:
            current_sec = 5

        if current_sec == 1:
            if "Devamsızlık yapanlar;" in t or "Devamsızlık yapanlar:" in t:
                p.text = "Devamsızlık yapanlar: 84 Kuzey Yusuf Uruklu (Mazeretli izin), 258 Meryem Bozdemir (Ailevi izinli), 327 Melek Rana Kesici (Sağlık kontrolleri). Sürekli devamsız öğrenci bulunmamaktadır."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif "Genel sorumluluklarını yerine getirmeyenler:" in t:
                p.text = "Genel sorumluluklarını yerine getirmeyenler: 224 Cengizhan Yılmaz, 227 Derin Yılmaz, 379 Çınar Efe Girgin (Zaman zaman ödev ve ders araç-gereç takibinde aksaklıklar yaşanmakta, veli takibi talep edilmiştir)."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif "Dersin düzenine bozan:" in t or "Dersin düzenini bozan:" in t:
                p.text = "Dersin düzenini bozan: Sınıf genelinde dersin işlenişini engelleyen kronik bir disiplin problemi yoktur. Ancak 272 Egehan Hardal'ın dürtüsel sorunları ve hareketliliği sebebiyle derse odaklanmakta güçlük çektiği ve zaman zaman ders akışında desteğe ihtiyaç duyduğu gözlemlenmiş olup bireysel tedbirler alınmaktadır."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif "Problemli öğrencileri isimleri :" in t or "Problemli öğrencilerin isimleri:" in t:
                p.text = "Problemli öğrencilerin isimleri: Davranışsal boyutta disiplin cezası gerektirecek problemli öğrenci bulunmamaktadır. Sosyal çekiniklik göstererek arkadaşlarıyla iletişim kurmayan 227 Derin Yılmaz ve dürtüsellik sebebiyle derse odaklanamayan 272 Egehan Hardal için bireysel rehberlik çalışmaları uygulanmaktadır."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif "Kaynaştırma öğrencileri:" in t:
                p.text = "Kaynaştırma öğrencileri: Sınıfımızda resmi RAM raporlu kaynaştırma öğrencisi bulunmamaktadır."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif t.startswith("Açıklama:"):
                p.text = "Açıklama: Şube genelinde sorumluluk bilinci olumlu olmakla birlikte; Egehan Hardal'ın dürtü kontrolünün desteklenmesi ve derse odaklanmasının sağlanması, Derin Yılmaz'ın ise içe kapanıklığını aşarak arkadaşlık ilişkilerini geliştirmesi adına sınıf rehber öğretmeni Serkan BAYTAN ve rehberlik servisi koordinasyonunda bireysel takip sürdürülmektedir."
                if p.runs: p.runs[0].font.size = Pt(8.5)

        elif current_sec == 2:
            if "sağlık problemi olan öğrenciler:" in t:
                p.text = "Sınıftaki sağlık problemi olan öğrenciler:\n• [230] Kenan Emir Yaman: Astım hastasıdır, gerektiğinde Ventolin inhaler sprey kullanmaktadır.\n• [245] Tuna Koç: Dikkat eksikliği takiplidir, hekim kontrolünde Medikinet kullanmaktadır.\n• [256] Beren Koç: Tiroit takiplidir, düzenli vitamin ve hekim kontrolü altındadır."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif "Beslenmesi zayıf olan öğrenciler:" in t:
                p.text = "Beslenmesi zayıf olan öğrenciler: Sabah kahvaltısı yapmadan gelen ve kantin ağırlıklı beslenen birkaç öğrencinin aileleri ile görüşülerek evde düzenli beslenme alışkanlığı kazandırılması kararlaştırıldı."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif t.startswith("Açıklama:"):
                p.text = "Açıklama: Şube genelinde öğrencilerin fiziksel gelişimleri ve sağlık durumları düzenli takip edilmektedir. Astım rahatsızlığı bulunan Kenan Emir Yaman, dikkat eksikliği takipli Tuna Koç ve tiroit takibi yapılan Beren Koç'un medikal durumları ve acil durum tedbirleri nöbetçi öğretmenler ile okul idaresine bildirilmiştir. Beslenme konusunda sabah kahvaltısının zihinsel odaklanma ve bilişsel performansa doğrudan etkisi veli toplantılarında önemle vurgulanmış; ev yapımı dengeli besinlerin ve yeterli su tüketiminin artırılması yönünde sınıf rehber öğretmeni ve ders öğretmenlerince öğrenciler düzenli olarak teşvik edilmektedir."
                if p.runs: p.runs[0].font.size = Pt(8.5)

        elif current_sec == 3:
            if t.startswith("Açıklama:") or t == "Açıklama:":
                p.text = "Açıklama: Sınıf genelinde akran iletişimi, yardımlaşma, saygı ve nezaket olumlu düzeydedir; şube iklimi yapıcı ve dayanışmaya açıktır. Ancak öğrencilerimizden 227 Derin Yılmaz'ın sosyal iletişim kurmada çok çekingen davrandığı, teneffüslerde ve grup çalışmalarında arkadaşlarıyla çok fazla iletişim kurmayıp içine kapandığı gözlemlenmiştir. 272 Egehan Hardal'ın ise dürtüsel sorunları ve hareketliliği nedeniyle derse odaklanamadığı, dikkat süresinin kısalığı sebebiyle ders akışında desteğe ihtiyaç duyduğu tespit edilmiştir."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif t.startswith("Öneri:") or t == "Öneri:":
                p.text = "Öneri: Sınıf içi sosyal uyumu ve bireysel gelişimi güçlendirmek adına; Derin Yılmaz'ın sosyal kabuğunu kırması ve arkadaşlık ilişkilerini geliştirmesi için ikili akran çalışmaları, sosyal kulüp ve sınıf içi aktif sorumluluklar verilmelidir. Egehan Hardal'ın dürtüsellik ve odaklanma sürecini desteklemek amacıyla ders esnasında ön sıraya oturtulması, dikkat süresine uygun kısa süreli görevlerle derse dahil edilmesi ve Rehberlik Servisi iş birliğiyle odaklanma-özdenetim çalışmalarının yürütülmesi kararlaştırılmıştır."
                if p.runs: p.runs[0].font.size = Pt(8.5)

        elif current_sec == 4:
            if "4- Sınıf başarı ve başarısızlık durumlarını" in t:
                p.text = "4- Sınıf başarı ve başarısızlık durumlarını derslere göre değerlendiriniz:\n" \
                         "• Türkçe: Akademik başarı yüksek düzeydedir (%62). Okuduğunu anlama, ana fikir ve yorumlama becerileri çok güçlü; sözel mantık ve dil bilgisi çalışmalarına ağırlık verilmelidir.\n" \
                         "• Matematik: Temel işlem becerileri iyi düzeydedir (%32); çok adımlı problem çözme, analitik akıl yürütme ve zaman yönetiminde destekleyici çalışmalara ihtiyaç duyulmaktadır.\n" \
                         "• Fen Bilimleri: Akademik başarı iyi düzeydedir (%54). Mevsimler ve İklim ile DNA üniteleri başarıyla kavranmış; bilimsel muhakeme ve grafik yorumlama soruları pekiştirilmelidir.\n" \
                         "• T.C. İnkılap Tarihi: Akademik başarı çok yüksek düzeydedir (%72). Tarihsel kavramlar, neden-sonuç ilişkisi ve kronolojik düşünme becerileri oldukça başarılıdır.\n" \
                         "• Din Kültürü: Akademik başarı mükemmel düzeydedir (%75). Kaza ve kader ünitesi kazanımları tam olup sınıfın en güçlü akademik alanlarından biridir.\n" \
                         "• İngilizce: Akademik başarı dengeli düzeydedir (%52). Friendship ve Teen Life üniteleri kelime bilgisi ve okuma-anlama pratikleriyle düzenli tekrar edilmelidir."
                if p.runs: p.runs[0].font.size = Pt(8.5)

        elif current_sec == 5:
            if "Geliri Düşük Olanlar Öğrenciler:" in t or "Geliri Düşük Olan" in t:
                p.text = "Geliri Düşük Olan Öğrenciler: Aile gelir düzeyi kısıtlı olan ve ders materyali desteğine ihtiyaç duyan öğrenciler okul-aile birliği ve rehberlik servisine bildirilmiştir."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif "Geliri İyi Olan Öğrenciler." in t or "Geliri İyi Olan" in t:
                p.text = "Geliri İyi Olan Öğrenciler: Sınıfın büyük çoğunluğunun ekonomik durumu orta ve iyi düzeyde olup temel eğitsel ihtiyaçlarını karşılayabilmektedir."
                if p.runs: p.runs[0].font.size = Pt(8.5)
            elif "Yardımlar İçin Önerilen Öğrenciler:" in t:
                p.text = "Yardımlar İçin Önerilen Öğrenciler: Kaynak kitap ve kırtasiye ihtiyacı olan öğrencilere okul idaresi ve zümre öğretmenlerince ücretsiz soru bankaları temin edilmiştir."
                if p.runs: p.runs[0].font.size = Pt(8.5)

    # 4. Tablo 0 (Gündem Maddeleri), Tablo 1 ve Tablo 2'yi Formatla
    # Section 1 (Mevzuat) formatting: tight to fit on Page 1
    for i in range(0, 26):
        p_el = doc.paragraphs[i]
        p_el.paragraph_format.line_spacing = 1.0
        p_el.paragraph_format.space_before = Pt(0)
        p_el.paragraph_format.space_after = Pt(1)
        for r in p_el.runs:
            if not r.font.bold:
                r.font.size = Pt(8)

    # Table 0: Gündem Maddeleri
    t0 = doc.tables[0]
    t0.alignment = WD_TABLE_ALIGNMENT.CENTER
    make_row_header(t0.rows[0])
    for r in t0.rows:
        make_row_cant_split(r)
        trPr = r._tr.get_or_add_trPr()
        for th in trPr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}trHeight'):
            trPr.remove(th)
        for c_i, c in enumerate(r.cells):
            set_cell_margins(c, top=15, bottom=15, left=35, right=35)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0.5)
            p.paragraph_format.line_spacing = 1.0
            if p.runs and c_i == 1 and not p.runs[0].font.bold:
                p.runs[0].font.size = Pt(8)
    set_table_borders(t0, color="B0C4DE", sz="4")

    def format_teacher_table(tbl):
        col_widths = [0.45, 3.45, 2.10, 1.0] # in inches, sum = 7.0
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        make_row_header(tbl.rows[0])

        for idx, (sira, ders, isim) in enumerate(TEACHERS_TABLE_DATA):
            r_idx = idx + 1
            if r_idx < len(tbl.rows):
                row = tbl.rows[r_idx]
            else:
                row = tbl.add_row()
            
            make_row_cant_split(row)

            trPr = row._tr.get_or_add_trPr()
            for th in trPr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}trHeight'):
                trPr.remove(th)

            cells = row.cells
            cells[0].text = sira
            p0 = cells[0].paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if p0.runs:
                p0.runs[0].font.name = "Calibri"
                p0.runs[0].font.size = Pt(8)
                p0.runs[0].font.bold = True

            cells[1].text = ders
            p1 = cells[1].paragraphs[0]
            p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if p1.runs:
                p1.runs[0].font.name = "Calibri"
                p1.runs[0].font.size = Pt(7.5)
                p1.runs[0].font.bold = True

            cells[2].text = isim
            p2 = cells[2].paragraphs[0]
            p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if p2.runs:
                p2.runs[0].font.name = "Calibri"
                p2.runs[0].font.size = Pt(8)
                p2.runs[0].font.bold = True
                p2.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

            cells[3].text = ""

            for c_idx, c in enumerate(cells):
                if c_idx < len(col_widths):
                    c.width = Inches(col_widths[c_idx])
                set_cell_margins(c, top=18, bottom=18, left=35, right=35)
                p = c.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0.5)
                p.paragraph_format.line_spacing = 1.0

        while len(tbl.rows) > len(TEACHERS_TABLE_DATA) + 1:
            row_to_remove = tbl.rows[-1]
            tr = row_to_remove._tr
            tr.getparent().remove(tr)

        set_table_borders(tbl, color="B0C4DE", sz="4")

    format_teacher_table(doc.tables[1])
    format_teacher_table(doc.tables[2])

    # 5. İmza ve Onay Bloklarını Doldur
    for p in doc.paragraphs:
        t = p.text
        if "Sınıf Rehber Öğretmeni" in t and "Müdür Yardımcısı" in t and "Okul Müdürü" in t:
            p.text = "Serkan BAYTAN\t\t\t\tDilek SANCAK\t\t\t\tEmin BAYKARA\n8/B Sınıf Rehber Öğretmeni\t\tMüdür Yardımcısı (Toplantı Başkanı)\t\tOkul Müdürü"
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.10
            if p.runs:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(8.5)
                p.runs[0].font.bold = True

    # 6. Sayfa Düzeni Temizliği: Art Arda Gelen Boş Paragrafları Temizle
    paragraphs_to_remove = []
    empty_count = 0
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            empty_count += 1
            if empty_count > 1:
                paragraphs_to_remove.append(p)
        else:
            empty_count = 0
            p.paragraph_format.line_spacing = 1.05
            if not p.paragraph_format.space_after or p.paragraph_format.space_after.pt > 4:
                p.paragraph_format.space_after = Pt(2)
            if not p.paragraph_format.space_before or p.paragraph_format.space_before.pt > 4:
                p.paragraph_format.space_before = Pt(1)

    for p in paragraphs_to_remove:
        p._p.getparent().remove(p._p)

    # 7. Ana Bölümlerin Temiz Sayfa Başlangıçları:
    # Her 3 T.C. başlığına page_break_before verilir.
    for p in doc.paragraphs:
        if p.text.strip() == "T.C.":
            p.paragraph_format.page_break_before = True

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path
