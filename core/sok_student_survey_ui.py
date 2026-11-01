"""
ŞÖK Öğrenci Veri Toplama Anketi UI Bileşeni
Öğrencilerin kendi sayfalarında doldurabileceği, MEB Şube Öğretmenler Kurulu (ŞÖK)
standartlarına ve rehberlik araştırmalarına tam uyumlu anket formu.
Birden fazla seçim yapılabilecek alanlarda '(Birden fazla seçenek işaretleyebilirsiniz)' uyarısı yer alır.
"""

import streamlit as st
import json
import sqlite3
from config import DATABASE_PATH
from core.sok_survey import save_sok_survey, get_sok_survey

def _safe_list(val):
    if isinstance(val, list):
        return val
    if isinstance(val, (tuple, set)):
        return list(val)
    if isinstance(val, str) and val.strip():
        return [val.strip()]
    return []

def _safe_str(val, default=""):
    if val is None:
        return default
    return str(val)

def _safe_radio_idx(options, val, default_idx=None):
    if val is not None and val in options:
        try:
            return options.index(val)
        except Exception:
            return default_idx
    return default_idx

def init_sok_detailed_table():
    """Öğrencinin anket yanıtlarını ham JSON olarak saklayan tabloyu hazırla."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sok_student_survey_detailed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER UNIQUE NOT NULL,
            raw_answers_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)
    conn.commit()
    conn.close()

def get_student_survey_raw(student_id: int) -> dict:
    if not student_id:
        return {}
    init_sok_detailed_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT raw_answers_json FROM sok_student_survey_detailed WHERE student_id = ?", (int(student_id),))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        try:
            res = json.loads(row[0])
            if isinstance(res, dict):
                return res
            return {}
        except Exception:
            return {}
    return {}

def save_student_survey_raw(student_id: int, answers_dict: dict):
    if not student_id:
        return
    init_sok_detailed_table()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sok_student_survey_detailed (student_id, raw_answers_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id) DO UPDATE SET
            raw_answers_json = excluded.raw_answers_json,
            updated_at = CURRENT_TIMESTAMP
    """, (int(student_id), json.dumps(answers_dict, ensure_ascii=False)))
    conn.commit()
    conn.close()

def build_sok_summary_texts(answers: dict) -> dict:
    """
    Öğrencinin anket yanıtlarından ŞÖK Madde 11 ve Gözlem Formuna girecek
    resmi pedagojik özet cümlelerini üretir.
    """
    if not isinstance(answers, dict):
        answers = {}

    # 1. Kişilik
    k_traits = _safe_list(answers.get("kisilik_tanim"))
    k_kaygi = _safe_str(answers.get("kaygi_durumu"))
    k_parts = []
    if k_traits:
        k_parts.append("; ".join(k_traits))
    if k_kaygi and "stres" in k_kaygi.lower():
        k_parts.append("Sınav ve başarı konusunda yoğun kaygı ve stres yaşadığını ifade etmiştir.")
    elif k_kaygi and "heyecan" in k_kaygi.lower():
        k_parts.append("Zaman zaman sınav kaygısı yaşayabiliyor.")
    kisilik_text = ". ".join(k_parts) if k_parts else "Sınıf içi kurallara uyumlu, sakin mizaçlı."

    # Ekran süresi notu kişilik/odaklanmaya eklenebilir
    ekran = _safe_str(answers.get("ekran_suresi"))
    gece_tel = _safe_str(answers.get("gece_telefon"))
    if "5 saat" in ekran or "3 - 4" in ekran:
        kisilik_text += f" (Ders dışı ekran süresi: {ekran})."
    if "Yatağa telefonla" in gece_tel:
        kisilik_text += " Gece geç saatlere kadar telefon/ekran kullanımı dikkat çekmektedir."

    # 2. Sağlık
    s_durum = _safe_list(answers.get("saglik_durumu"))
    s_not = _safe_str(answers.get("saglik_notu")).strip()
    s_parts = []
    if s_durum:
        s_parts.append("; ".join(s_durum))
    if s_not:
        s_parts.append(f"Açıklama: {s_not}")
    saglik_text = ". ".join(s_parts) if s_parts else "Genel sağlık durumu gayet iyi; bilinen bir kronik rahatsızlığı yok."

    # 3. Beslenme & Uyku
    b_kahv = _safe_str(answers.get("kahvalti"))
    b_bes = _safe_list(answers.get("beslenme_sekli"))
    b_uyku = _safe_str(answers.get("uyku_durumu"))
    b_parts = []
    if b_kahv:
        b_parts.append(f"Kahvaltı: {b_kahv}")
    if b_bes:
        b_parts.append(f"Beslenme tercihi: {', '.join(b_bes)}")
    if b_uyku:
        b_parts.append(f"Uyku: {b_uyku}")
    beslenme_text = "; ".join(b_parts) if b_parts else "Genel beslenme alışkanlıkları dengeli."

    # 4. Sosyal İlişkiler
    sos_opts = _safe_list(answers.get("sosyal_iliski"))
    sosyal_text = "; ".join(sos_opts) if sos_opts else "Sınıf içi akran ilişkileri dengeli ve uyumlu."

    # 5. Çalışma Ortamı & Aile
    cal_opts = _safe_list(answers.get("calisma_ortami"))
    aile_tutum = _safe_str(answers.get("aile_yaklasimi"))
    eko_parts = []
    if cal_opts:
        eko_parts.append("; ".join(cal_opts))
    if aile_tutum:
        eko_parts.append(f"Aile Yaklaşımı: {aile_tutum}")
    ekonomik_text = ". ".join(eko_parts) if eko_parts else "Evde temel çalışma şartları mevcut."

    # 6. Akademik Durum & Güçlükler
    engel_opts = _safe_list(answers.get("calisma_engelleri"))
    zor_dersler = _safe_list(answers.get("zorlanilan_dersler"))
    iyi_dersler = _safe_list(answers.get("basarili_dersler"))
    akad_parts = []
    if iyi_dersler and "Hiçbiri" not in iyi_dersler:
        akad_parts.append(f"Kendini başarılı hissettiği alanlar: {', '.join(iyi_dersler)}")
    if zor_dersler and "Zorlandığım ders yok" not in zor_dersler:
        akad_parts.append(f"Kazanım desteğine ihtiyaç duyduğu dersler: {', '.join(zor_dersler)}")
    if engel_opts and "Herhangi bir engelim yok" not in engel_opts:
        akad_parts.append(f"Ders çalışmayı zorlaştıran faktörler: {', '.join(engel_opts)}")
    akademik_text = ". ".join(akad_parts) if akad_parts else "Kazanımları takip edebiliyor, akademik takibi sürmektedir."

    # 7. Kurul Kararı & Önlemler
    destek_opts = _safe_list(answers.get("destek_istekleri"))
    ozel_not = _safe_str(answers.get("ogrenci_ozel_notu")).strip()
    oneri_parts = []
    if destek_opts and "Şu an için özel bir desteğe ihtiyaç duymuyorum" not in destek_opts:
        oneri_parts.append(f"Talep edilen rehberlik ve kurul desteği: {', '.join(destek_opts)}")
    if ozel_not:
        oneri_parts.append(f"Öğrenci Notu: '{ozel_not}'")
    if not oneri_parts:
        oneri_parts.append("Haftalık ders çalışma programı takibi ve DYK kurslarına yönlendirme.")
    oneri_text = ". ".join(oneri_parts)

    return {
        "kisilik_ozellikleri": kisilik_text,
        "saglik_durumu": saglik_text,
        "beslenme_durumu": beslenme_text,
        "sosyal_iliskiler": sosyal_text,
        "calisma_ve_ekonomik": ekonomik_text,
        "akademik_durum": akademik_text,
        "oneri_ve_tedbir": oneri_text
    }


def render_sok_student_survey(student_id=None, student_name="Öğrenci", student_no="", allow_back_button=True, *args, **kwargs):
    """Öğrencinin ekranında ŞÖK Veri Toplama Formunu render eder."""
    student_name = _safe_str(student_name, "Öğrenci")
    student_no = _safe_str(student_no, "")

    # Eğer student_id henüz çözülmediyse isim veya numaradan veritabanından bul
    if not student_id and (student_name or student_no):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute("SELECT id, school_no FROM students WHERE UPPER(name) = UPPER(?) OR school_no = ? LIMIT 1",
                      (student_name.strip(), student_no.strip()))
            r = c.fetchone()
            conn.close()
            if r:
                student_id = int(r[0])
                if not student_no and r[1]:
                    student_no = str(r[1])
        except Exception:
            pass

    student_id = int(student_id) if student_id else 0

    raw_saved = get_student_survey_raw(student_id)
    if not isinstance(raw_saved, dict):
        raw_saved = {}
    has_submitted = bool(raw_saved)

    if allow_back_button:
        c_nav1, c_nav2 = st.columns([1, 4])
        if c_nav1.button("🏠 Ana Sayfaya Dön", key=f"btn_back_home_top_{student_id}", type="secondary"):
            st.session_state.student_view_mode = "dashboard"
            st.rerun()

    no_str = f" (No: {student_no})" if student_no else ""
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 18px 22px; border-radius: 12px; color: white; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0; font-size: 22px;'>📝 8/B Şube Öğretmenler Kurulu (ŞÖK) Öğrenci Veri Toplama Anketi</h2>
            <p style='margin: 8px 0 0 0; font-size: 13.5px; opacity: 0.95;'>
                Sevgili <b>""" + student_name.title() + no_str + """</b>, bu formdaki yanıtların; öğretmenlerinin seni daha yakından tanıması, 
                ihtiyaç duyduğun akademik ve rehberlik desteğinin planlanması ve ŞÖK kararlarının sağlıklı alınması amacıyla kullanılacaktır. 
                Yanıtların gizlidir ve yalnızca öğretmenlerin ile okul idaresi tarafından görülecektir.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if has_submitted:
        st.success("✅ **Bu formu daha önce doldurdunuz.** Dilerseniz aşağıdaki bilgileri güncelleyip tekrar kaydedebilirsiniz.")

    with st.form(key=f"form_sok_survey_student_{student_id}"):
        
        # ── 1. Kişilik, Özgüven ve Mizaç ──
        st.markdown("### 👤 Bölüm 1 — Kişilik, Özgüven ve Mizaç")
        st.caption("Kendini sınıf ortamında ve derslerde nasıl hissettiğini belirt.")
        
        q1_opts = [
            "Kendime güvenirim, derste rahatça söz alır ve kendimi ifade ederim",
            "Sorumluluk sahibiyim, ödev ve görevlerimi aksatmadan yaparım",
            "Sakin ve uyumluyum, dinlemeyi ve izlemeyi tercih ederim",
            "Çekingenim, tahtaya kalkarken veya kalabalıkta konuşurken utanırım",
            "Hareketli ve tez canlıyım, derste uzun süre sabit oturmakta zorlanırım",
            "Ders esnasında zaman zaman dikkatimi toplamakta ve odaklanmakta zorlanırım"
        ]
        q1_def = [x for x in _safe_list(raw_saved.get("kisilik_tanim")) if x in q1_opts]
        ans_kisilik = st.multiselect(
            "1.1. Kendini derslerde ve sınıf ortamında genel olarak nasıl tanımlarsın? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            q1_opts, default=q1_def
        )

        q2_opts = [
            "Rahat ve sakinim, kendime güveniyorum",
            "Zaman zaman heyecanlanırım ve hafif sınav kaygısı yaşarım",
            "Yoğun sınav stresi yaşıyorum, bildiklerimi unutmaktan korkuyorum"
        ]
        q2_idx = _safe_radio_idx(q2_opts, raw_saved.get("kaygi_durumu"), default_idx=None)
        ans_kaygi = st.radio("1.2. Sınavlar ve ders başarısı konusunda genel duygu durumun nedir?", q2_opts, index=q2_idx)

        st.markdown("---")

        # ── 2. Sağlık Durumu ──
        st.markdown("### 🏥 Bölüm 2 — Sağlık Durumu ve Medikal Bilgiler")
        st.caption("Öğretmenlerinin bilmesi gereken fiziksel ve sağlık durumun.")

        q3_opts = [
            "Genel sağlık durumum gayet iyi, bilinen bir rahatsızlığım yok",
            "Astım, alerji veya solunum yolu hassasiyetim var",
            "Görme (gözlük vb.) veya işitme ile ilgili dikkat edilmesi gereken durumum var",
            "Dikkat eksikliği / odaklanma takibim var",
            "Düzenli kullandığım ilaç / doktor takibim var"
        ]
        q3_def = [x for x in _safe_list(raw_saved.get("saglik_durumu")) if x in q3_opts]
        ans_saglik = st.multiselect(
            "2.1. Sağlık durumunla ilgili aşağıdakilerden hangileri geçerlidir? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            q3_opts, default=q3_def
        )

        ans_saglik_not = st.text_input(
            "2.2. Varsa kronik rahatsızlığınızı, alerjinizi veya düzenli kullandığınız ilacın adını yazınız (İsteğe bağlı):",
            value=_safe_str(raw_saved.get("saglik_notu")),
            placeholder="Örn: Astım için Ventolin sprey, Dikkat ilacı vb."
        )

        st.markdown("---")

        # ── 3. Beslenme Alışkanlığı ve Uyku Düzeni ──
        st.markdown("### 🍎 Bölüm 3 — Beslenme Alışkanlığı ve Uyku Düzeni")

        q4_opts = [
            "Her sabah düzenli olarak kahvaltı yaparım",
            "Bazen yaparım, bazen vakit bulamam",
            "Genellikle kahvaltı yapmadan aç gelirim"
        ]
        q4_idx = _safe_radio_idx(q4_opts, raw_saved.get("kahvalti"), default_idx=None)
        ans_kahvalti = st.radio("3.1. Sabahları okula gelmeden önceki kahvaltı düzenin nasıldır?", q4_opts, index=q4_idx)

        q5_opts = [
            "Evden getirdiğim sağlıklı beslenme çantamı tüketirim",
            "Okul kantininden tost, sandviç veya atıştırmalık alırım",
            "Gün içinde bol su tüketmeye dikkat ederim",
            "Bazen öğün atlarım veya abur cuburla geçiştiririm"
        ]
        q5_def = [x for x in _safe_list(raw_saved.get("beslenme_sekli")) if x in q5_opts]
        ans_beslenme = st.multiselect(
            "3.2. Okulda gün içindeki beslenmeni nasıl karşılıyorsun? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            q5_opts, default=q5_def
        )

        q6_opts = [
            "Erken yatarım (22:00 - 23:00 arası), sabahları dinç ve dinlenmiş uyanırım",
            "Geç yatarım (23:30 sonrası), sabahları uyanmakta ve derste dinlemekte zorlanırım",
            "Uykum düzensizdir, gece sık sık uyanırım veya uykuya dalmakta zorlanırım"
        ]
        q6_idx = _safe_radio_idx(q6_opts, raw_saved.get("uyku_durumu"), default_idx=None)
        ans_uyku = st.radio("3.3. Gece uyku düzenin ve sabah uyanma durumun nasıldır?", q6_opts, index=q6_idx)

        st.markdown("---")

        # ── 4. Ekran Süresi ve Dijital Alışkanlıklar ──
        st.markdown("### 📱 Bölüm 4 — Ekran Süresi ve Dijital Alışkanlıklar")
        st.caption("Ders dışı teknoloji kullanım alışkanlıkların.")

        q7_opts = [
            "Günde 1 saatten az (Çok sınırlı / kontrollü)",
            "Günde 1 - 2 saat (Dengeli kullanım)",
            "Günde 3 - 4 saat (Yoğun ekran süresi)",
            "Günde 5 saat ve üzeri (Aşırı yoğun ekran süresi)"
        ]
        q7_idx = _safe_radio_idx(q7_opts, raw_saved.get("ekran_suresi"), default_idx=None)
        ans_ekran = st.radio("4.1. Okul ve ders dışındaki zamanında günde ortalama kaç saatini telefon, tablet veya bilgisayarda (oyun, sosyal medya, video) geçiriyorsun?", q7_opts, index=q7_idx)

        q8_opts = [
            "Telefonu/tableti odamın dışında bırakırım veya yatmadan önce tamamen kapatırım",
            "Yatağa telefonla girerim, uyuyana kadar ekrana bakarım"
        ]
        q8_idx = _safe_radio_idx(q8_opts, raw_saved.get("gece_telefon"), default_idx=None)
        ans_gece_tel = st.radio("4.2. Gece yatarken telefon veya dijital cihaz kullanımın nasıldır?", q8_opts, index=q8_idx)

        st.markdown("---")

        # ── 5. Sosyal İlişkiler ve Sınıf İklimi ──
        st.markdown("### 🤝 Bölüm 5 — Sosyal İlişkiler, Sınıf İklimi ve Akran Uyumu")

        q9_opts = [
            "Arkadaşlarımla çok iyi anlaşırım, sınıf ortamında sevilen biriyim",
            "Grup ve takım çalışmalarında arkadaşlarımla uyumlu ve işbirlikçiyim",
            "Sadece birkaç yakın arkadaşımla vakit geçiririm, diğerleriyle mesafeliyim",
            "Sınıf ortamında bazen yalnız kaldığımı veya dışlandığımı hissederim",
            "Arkadaşlarımın şaka veya sözlerinden bazen alınganlık / huzursuzluk yaşarım",
            "Sınıfta kendimi tamamen güvende ve huzurlu hissederim"
        ]
        q9_def = [x for x in _safe_list(raw_saved.get("sosyal_iliski")) if x in q9_opts]
        ans_sosyal = st.multiselect(
            "5.1. Sınıftaki arkadaşlarınla ilişkilerini ve sınıf ortamını nasıl değerlendirirsin? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            q9_opts, default=q9_def
        )

        st.markdown("---")

        # ── 6. Evde Çalışma Ortamı ve Aile Yaklaşımı ──
        st.markdown("### 🏠 Bölüm 6 — Evde Çalışma Ortamı ve Aile Yaklaşımı")

        q10_opts = [
            "Evde kendime ait sessiz bir çalışma odam ve çalışma masam var",
            "Kardeşlerim veya ailemle ortak alanda çalışmak zorunda kalıyorum",
            "Ders araç-gereçlerim ve kaynak kitaplarım yeterlidir",
            "Ek soru bankasına veya yardımcı kaynak kitaba ihtiyacım var",
            "İnternet ve ders çalışabileceğim bilgisayar/tabletim var"
        ]
        q10_def = [x for x in _safe_list(raw_saved.get("calisma_ortami")) if x in q10_opts]
        ans_calisma = st.multiselect(
            "6.1. Evdeki ders çalışma ortamın ve kaynak durumun nasıldır? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            q10_opts, default=q10_def
        )

        q11_opts = [
            "Destekleyici, anlayışlı ve motive edici buluyorum",
            "Üzerimde yoğun bir beklenti, stres ve başarı baskısı hissediyorum",
            "Kendi halime bırakıyorlar, derslerimle pek ilgilenmiyorlar"
        ]
        q11_idx = _safe_radio_idx(q11_opts, raw_saved.get("aile_yaklasimi"), default_idx=None)
        ans_aile = st.radio("6.2. Ailenizin derslerinize, ödevlerinize ve sınavlarınıza olan yaklaşımı nasıldır?", q11_opts, index=q11_idx)

        st.markdown("---")

        # ── 7. Akademik Güçlük ve Ders Çalışmayı Engelleyen Faktörler ──
        st.markdown("### 📚 Bölüm 7 — Akademik Güçlük ve Ders Çalışmayı Engelleyen Faktörler")

        q12_opts = [
            "Telefon, bilgisayar, oyunlar veya sosyal medya",
            "Nereden başlayacağımı ve nasıl verimli ders çalışacağımı tam bilememek",
            "Çabuk sıkılmak, isteksizlik veya dikkatimin çabuk dağılması",
            "Konuların bana zor veya karmaşık gelmesi",
            "Evdeki gürültü, kardeşler veya ortam yetersizliği",
            "Herhangi bir engelim yok, düzenli çalışabiliyorum"
        ]
        q12_def = [x for x in _safe_list(raw_saved.get("calisma_engelleri")) if x in q12_opts]
        ans_engeller = st.multiselect(
            "7.1. Bu yıl derslerine çalışırken seni en çok ne engelliyor veya dikkatini dağıtıyor? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            q12_opts, default=q12_def
        )

        ders_list = ["Matematik", "Fen Bilimleri", "Türkçe", "T.C. İnkılap Tarihi", "İngilizce", "Din Kültürü", "Zorlandığım ders yok"]
        q13_def = [x for x in _safe_list(raw_saved.get("zorlanilan_dersler")) if x in ders_list]
        ans_zor_dersler = st.multiselect(
            "7.2. Kavramakta veya takip etmekte en çok zorlandığın ders(ler) hangileridir? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            ders_list, default=q13_def
        )

        basari_list = ["Türkçe", "Matematik", "Fen Bilimleri", "T.C. İnkılap Tarihi", "İngilizce", "Din Kültürü", "Beden Eğitimi / Spor", "Müzik / Görsel Sanatlar / Bilişim"]
        q14_def = [x for x in _safe_list(raw_saved.get("basarili_dersler")) if x in basari_list]
        ans_iyi_dersler = st.multiselect(
            "7.3. Kendini en başarılı ve istekli hissettiğin ders(ler) hangileridir? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            basari_list, default=q14_def
        )

        st.markdown("---")

        # ── 8. Okuldan ve Rehberlik Servisinden Beklentiler ──
        st.markdown("### 🎯 Bölüm 8 — Okuldan, Öğretmenlerinden ve Rehberlik Servisinden Beklentiler")

        q15_opts = [
            "Haftalık verimli ders çalışma ve zaman yönetimi programı hazırlanması",
            "Zorlandığım derslerde DYK (kurs) ve etüt takviyesi yapılması",
            "Sınav kaygısı ve stres yönetimi için okul rehberlik servisiyle bireysel görüşme",
            "Ders içi odaklanma ve dikkat toplama yöntemleri konusunda destek",
            "Ailemle okulun görüşerek çalışma ortamımı desteklemesi",
            "Şu an için özel bir desteğe ihtiyaç duymuyorum"
        ]
        q15_def = [x for x in _safe_list(raw_saved.get("destek_istekleri")) if x in q15_opts]
        ans_destek = st.multiselect(
            "8.1. Başarını artırmak ve kendini daha iyi hissetmek için sana nasıl destek olunmasını istersin? 💡 (Birden fazla seçenek işaretleyebilirsiniz)",
            q15_opts, default=q15_def
        )

        ans_not = st.text_area(
            "8.2. Öğretmenlerine veya rehberlik servisine iletmek istediğin özel bir düşüncen veya notun var mı? (İsteğe bağlı):",
            value=_safe_str(raw_saved.get("ogrenci_ozel_notu")),
            placeholder="Öğretmenlerinizle paylaşmak istediğiniz bir öneri, talep veya kişisel durum..."
        )

        st.markdown("---")
        btn_submit = st.form_submit_button("✅ ŞÖK Veri Toplama Anketini Gönder ve Kaydet", use_container_width=True, type="primary")

        if btn_submit:
            all_answers = {
                "kisilik_tanim": ans_kisilik,
                "kaygi_durumu": ans_kaygi,
                "saglik_durumu": ans_saglik,
                "saglik_notu": ans_saglik_not,
                "kahvalti": ans_kahvalti,
                "beslenme_sekli": ans_beslenme,
                "uyku_durumu": ans_uyku,
                "ekran_suresi": ans_ekran,
                "gece_telefon": ans_gece_tel,
                "sosyal_iliski": ans_sosyal,
                "calisma_ortami": ans_calisma,
                "aile_yaklasimi": ans_aile,
                "calisma_engelleri": ans_engeller,
                "zorlanilan_dersler": ans_zor_dersler,
                "basarili_dersler": ans_iyi_dersler,
                "destek_istekleri": ans_destek,
                "ogrenci_ozel_notu": ans_not
            }
            # 1. Ham yanıtları kaydet
            save_student_survey_raw(student_id, all_answers)

            # 2. ŞÖK resmi tablosu için özet üret ve kaydet
            summary_data = build_sok_summary_texts(all_answers)
            save_sok_survey(student_id, summary_data)

            st.session_state.student_view_mode = "dashboard"
            st.success("🎉 ŞÖK Öğrenci Veri Toplama Anketi başarıyla kaydedildi! Yanıtlarınız Şube Öğretmenler Kurulu evraklarına işlendi.")
            st.balloons()
            st.rerun()

    if allow_back_button:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        c_b1, c_b2 = st.columns([1, 4])
        if c_b1.button("🏠 İptal / Ana Sayfaya Dön", key=f"btn_back_home_bot_{student_id}", type="secondary"):
            st.session_state.student_view_mode = "dashboard"
            st.rerun()
