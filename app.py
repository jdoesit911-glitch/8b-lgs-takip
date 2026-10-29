import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

from core.database import init_db, list_exams, get_exam_results, get_student_history, get_student_kazanims, get_class_comparison, save_exam
from core.parser import parse_lgs_workbook
from core.analyzer import analyze_class_performance, calculate_pareto, diagnose_student, generate_support_groups
from core.word_generator import generate_word_report
from core.excel_generator import generate_excel_tracker
from core.student_card_gen import generate_all_student_cards, generate_single_student_card, get_subject_prescriptions, norm_text
from core.branch_report_gen import generate_branch_word_report, generate_all_branch_reports, analyze_branch_data
from config import EXPORTS_DIR, SUBJECTS
from core.youtube_recommender import render_lgs_youtube_table_html, render_yt_buttons_html
from core.risk_mapper import (RISK_FACTORS, STUDENT_SURVEY_QUESTIONS, STUDENT_VISIBLE_IDS,
                               FACTOR_DICT, init_risk_table, set_risk_factor,
                               get_student_risk_factors, get_all_risk_data, get_risk_summary,
                               save_student_survey)

st.set_page_config(
    page_title="LGS Akademik Başarı ve Takip Otomasyonu",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    .main-title { font-size: 26px; font-weight: bold; color: #1F497D; margin-bottom: 2px; }
    .sub-title { font-size: 14px; color: #595959; margin-bottom: 20px; }
    .metric-card { background-color: #F2F5F8; border-radius: 8px; padding: 12px; border-left: 4px solid #1F497D; }
    .alert-card { background-color: #FDEDEC; border-radius: 8px; padding: 12px; border-left: 4px solid #900C3F; }
    .success-card { background-color: #E8F8F5; border-radius: 8px; padding: 12px; border-left: 4px solid #0E6655; }
    .role-badge-admin   { background:#1B4F72; color:white; padding:3px 10px; border-radius:12px; font-size:13px; }
    .role-badge-teacher { background:#117864; color:white; padding:3px 10px; border-radius:12px; font-size:13px; }
    .role-badge-student { background:#6C3483; color:white; padding:3px 10px; border-radius:12px; font-size:13px; }
    
    /* Belirgin Parlak Kırmızı Çıkış Butonları (Sidebar ve Header) */
    div[data-testid="stSidebar"] div.stButton > button,
    section[data-testid="stSidebar"] div.stButton > button,
    .main-logout-wrapper div.stButton > button,
    .logout-btn-box button {
        background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%) !important;
        background-color: #C0392B !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
        border: 2px solid #900C3F !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 10px rgba(192, 57, 43, 0.45) !important;
        transition: all 0.25s ease-in-out !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    div[data-testid="stSidebar"] div.stButton > button p,
    div[data-testid="stSidebar"] div.stButton > button span,
    section[data-testid="stSidebar"] div.stButton > button p,
    section[data-testid="stSidebar"] div.stButton > button span,
    .main-logout-wrapper div.stButton > button p,
    .main-logout-wrapper div.stButton > button span,
    .logout-btn-box button p,
    .logout-btn-box button span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
    }
    div[data-testid="stSidebar"] div.stButton > button:hover,
    section[data-testid="stSidebar"] div.stButton > button:hover,
    .main-logout-wrapper div.stButton > button:hover,
    .logout-btn-box button:hover {
        background: linear-gradient(135deg, #C0392B 0%, #900C3F 100%) !important;
        background-color: #900C3F !important;
        border-color: #641E16 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 14px rgba(144, 12, 63, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

init_db()

# ===================== ROL TANIMLARI =====================
ADMIN_PIN   = os.environ.get("ADMIN_PIN",   "ADMIN8B2026")
TEACHER_PIN = os.environ.get("TEACHER_PIN", "8B2026")

# Öğrenci şifresi = okul numarası (her öğrenci kendi numarasıyla giriş yapar)
# Okul numarası <-> isim eşleşmesi veri tabanından alınır

ROLE_INFO = {
    "admin":   {"icon": "🔑", "label": "Admin",     "badge": "role-badge-admin"},
    "teacher": {"icon": "👩‍🏫", "label": "Öğretmen", "badge": "role-badge-teacher"},
    "student": {"icon": "🎒", "label": "Öğrenci",   "badge": "role-badge-student"},
}

# ===================== GİRİŞ EKRANI =====================
if "role" not in st.session_state:
    st.session_state.role = None
    st.session_state.student_name = None
    st.session_state.student_no = None

if st.session_state.role is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("""
        <div style='text-align:center; margin-bottom:20px;'>
            <h2>🎓 8/B LGS Akademik Takip Sistemi</h2>
            <p style='color:#666;'>Lütfen rolünüzü seçerek sisteme giriş yapınız.</p>
        </div>
        """, unsafe_allow_html=True)

        role_choice = st.radio(
            "Rolünüzü seçin:",
            options=["Öğrenci", "Öğretmen", "Admin"],
            horizontal=True
        )
        st.markdown("---")

        if role_choice == "Öğrenci":
            st.info("🎒 **Öğrenci Girişi:** Size verilen **4 haneli giriş kodunuzu** (büyük harf + rakam) girerek sisteme erişebilirsiniz.\n"
                    "Yalnızca **kendi karnenizi** ve **sınıf ortalamalarını** görebilirsiniz.")
            with st.form("form_student_login"):
                pin_input = st.text_input("Öğrenci Giriş Kodunuz (4 hane):", placeholder="Örn: AB1C",
                                          help="Öğretmeninizden aldığınız 4 karakterli kodu giriniz.")
                submit_student = st.form_submit_button("🎒 Öğrenci Olarak Giriş Yap", use_container_width=True)
                if submit_student:
                    import sqlite3
                    from config import DATABASE_PATH
                    conn = sqlite3.connect(DATABASE_PATH)
                    c = conn.cursor()
                    # PIN büyük/küçük harf duyarsız karşılaştırma
                    row = c.execute(
                        "SELECT name, school_no FROM students WHERE UPPER(pin) = UPPER(?)",
                        (pin_input.strip(),)
                    ).fetchone()
                    conn.close()
                    if row:
                        st.session_state.role = "student"
                        st.session_state.student_name = row[0]
                        st.session_state.student_no = row[1]
                        # student_id'yi de kaydet (risk haritasi icin)
                        conn2 = sqlite3.connect(DATABASE_PATH)
                        row2 = conn2.execute("SELECT id FROM students WHERE UPPER(pin) = UPPER(?)", (pin_input.strip(),)).fetchone()
                        conn2.close()
                        if row2:
                            st.session_state.student_id = row2[0]
                        st.rerun()
                    else:
                        st.error("❌ Hatalı giriş kodu! Lütfen öğretmeninizden aldığınız 4 haneli kodu kontrol edin.")

        elif role_choice == "Öğretmen":
            st.info("👩‍🏫 **Öğretmen Girişi:** Tüm öğrenci verilerini ve raporları görüntüleyebilirsiniz.")
            with st.form("form_teacher_login"):
                pin_input = st.text_input("Öğretmen Erişim Şifresi:", type="password")
                submit_teacher = st.form_submit_button("👩‍🏫 Öğretmen Olarak Giriş Yap", use_container_width=True)
                if submit_teacher:
                    if pin_input == TEACHER_PIN:
                        st.session_state.role = "teacher"
                        st.rerun()
                    else:
                        st.error("❌ Hatalı şifre!")

        elif role_choice == "Admin":
            st.info("🔑 **Admin Girişi:** Tüm yetkilere sahipsiniz. Yeni deneme sınavı yükleyebilirsiniz.")
            with st.form("form_admin_login"):
                pin_input = st.text_input("Admin Şifresi:", type="password")
                submit_admin = st.form_submit_button("🔑 Admin Olarak Giriş Yap", use_container_width=True)
                if submit_admin:
                    if pin_input == ADMIN_PIN:
                        st.session_state.role = "admin"
                        st.rerun()
                    else:
                        st.error("❌ Hatalı admin şifresi!")

        st.markdown("---")
        st.caption("🔒 Bu sistem öğrenci kişisel verilerini korumak için şifre korumalıdır. "
                   "Giriş bilgilerinizi lütfen paylaşmayın.")
    st.stop()

# ===================== GİRİŞ YAPILDI - ORTAK SETUP =====================
current_role = st.session_state.role
role_info = ROLE_INFO[current_role]

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/graduation-cap.png", width=64)
st.sidebar.title("LGS Takip Sistemi")
st.sidebar.caption("Yıl Boyu Deneme & Başarı Otomasyonu")
st.sidebar.markdown(f"**Aktif Oturum:** <span class='{role_info['badge']}'>"
                    f"{role_info['icon']} {role_info['label']}"
                    + (f" — {st.session_state.student_name}" if current_role == "student" else "")
                    + "</span>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Oturumu Kapat / Çıkış Yap", key="btn_logout_top", use_container_width=True):
    st.session_state.role = None
    st.session_state.student_name = None
    st.session_state.student_no = None
    st.rerun()
st.sidebar.markdown("---")

# Sınav listesi
exams = list_exams()
if not exams:
    sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_exam.xlsx")
    if not os.path.exists(sample_file):
        sample_file = r"C:\Users\ELRA\Downloads\PARAF LGS 1 Sonuç ve Analiz Raporları.xlsx"
    if os.path.exists(sample_file):
        parsed = parse_lgs_workbook(sample_file, "8/B")
        save_exam(parsed['exam_name'], parsed['exam_date'], parsed['publisher'],
                  parsed['students'], parsed['kazanim_data'], parsed['comparison_data'])
        exams = list_exams()

exam_names = [e['name'] for e in exams] if exams else ["Kayıtlı Sınav Yok"]
selected_exam_name = st.sidebar.selectbox("📅 Aktif Deneme Sınavı:", exam_names, index=len(exam_names)-1 if exam_names else 0)

selected_exam_id = 1
for e in exams:
    if e['name'] == selected_exam_name:
        selected_exam_id = e['id']
        break

# Yükleme: Sadece Admin
if current_role == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Yeni Deneme Sınavı Yükle")
    uploaded_file = st.sidebar.file_uploader("Excel Dosyası Seç (.xlsx)", type=["xlsx"])
    target_class = st.sidebar.text_input("Şube:", value="8/B")
    if uploaded_file and st.sidebar.button("⚡ Sınavı Yükle ve Tüm Raporları Oluştur"):
        # ─── ADIM 1: Dosyayı kaydet ve parse et ───
        temp_path = os.path.join(EXPORTS_DIR, "temp_uploaded.xlsx")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Ana ekranda canlı ilerleme göster
        prog_container = st.empty()
        with prog_container.container():
            st.info("⏳ **Otomatik İşlem Hattı Başladı** — lütfen bekleyin...")
            prog_bar = st.progress(0)
            prog_status = st.empty()

            # 1/6 – Veri ayrıştırma
            prog_status.markdown("**1/6** 📂 Excel dosyası okunuyor ve veriler ayrıştırılıyor...")
            prog_bar.progress(10)
            parsed = parse_lgs_workbook(temp_path, target_class)
            exam_name_new = parsed['exam_name']

            # 2/6 – Veri tabanına kayıt
            prog_status.markdown(f"**2/6** 💾 '{exam_name_new}' veri tabanına kaydediliyor...")
            prog_bar.progress(25)
            new_exam_id = save_exam(
                parsed['exam_name'], parsed['exam_date'], parsed['publisher'],
                parsed['students'], parsed['kazanim_data'], parsed['comparison_data']
            )

            # Güncel veriyi çek
            new_results = get_exam_results(new_exam_id)
            new_comps   = get_class_comparison(new_exam_id)
            new_kaz_map = {r['name']: get_student_kazanims(new_exam_id, r['name']) for r in new_results}

            # 3/6 – 27 öğrenci karnesi
            prog_status.markdown(f"**3/6** 🖨️ {len(new_results)} öğrenci karnesi oluşturuluyor (.docx)...")
            prog_bar.progress(45)
            import zipfile as _zipfile
            karne_dir = os.path.join(EXPORTS_DIR, "karneler")
            created_cards = generate_all_student_cards(new_results, exam_name_new, new_kaz_map, karne_dir)

            # 4/6 – ZIP paketi
            prog_status.markdown("**4/6** 📦 Karneler ZIP paketine dönüştürülüyor...")
            prog_bar.progress(60)
            zip_path = os.path.join(EXPORTS_DIR, "8B_Tum_Karneler.zip")
            with _zipfile.ZipFile(zip_path, 'w', _zipfile.ZIP_DEFLATED) as zf:
                for cfile in created_cards:
                    zf.write(cfile, os.path.basename(cfile))

            # 5/6 – Word raporu
            prog_status.markdown("**5/6** 📑 Kapsamlı Word Raporu oluşturuluyor...")
            prog_bar.progress(75)
            w_out = os.path.join(EXPORTS_DIR, "8B_LGS_Akademik_Basari_ve_Strateji_Raporu.docx")
            try:
                generate_word_report(exam_name_new, new_results, new_kaz_map, new_comps, w_out)
            except Exception as _e:
                st.warning(f"Word raporu oluşturulurken uyarı: {_e}")

            # 6/6 – Excel takip dosyası ve Branş Raporları
            prog_status.markdown("**6/6** 📗 Excel ve Branş Raporları oluşturuluyor...")
            prog_bar.progress(90)
            x_out = os.path.join(EXPORTS_DIR, "8B_LGS_Takip_Sistemi.xlsx")
            try:
                generate_excel_tracker(exam_name_new, new_results, new_kaz_map, new_comps, x_out)
            except Exception as _e:
                st.warning(f"Excel dosyası oluşturulurken uyarı: {_e}")
            try:
                generate_all_branch_reports(exam_name_new, new_results, new_kaz_map, new_comps)
            except Exception as _e:
                pass

            prog_bar.progress(100)
            prog_status.markdown("✅ **Tüm işlemler tamamlandı!**")


        # Özet
        st.success(
            f"🎉 **'{exam_name_new}' başarıyla sisteme eklendi!**\n\n"
            f"✔ {len(created_cards)} öğrenci karnesi oluşturuldu\n"
            f"✔ ZIP paketi hazırlandı\n"
            f"✔ Word raporu güncellendi\n"
            f"✔ Excel takip dosyası güncellendi\n\n"
            f"Rapor & Karne sekmesinden tüm dosyaları indirebilirsiniz."
        )

        # Hızlı indirme butonları
        dc1, dc2, dc3 = st.columns(3)
        if os.path.exists(zip_path):
            with open(zip_path, "rb") as _fz:
                dc1.download_button("📥 Karneler (ZIP)", data=_fz.read(),
                                    file_name="8B_Tum_Karneler.zip", mime="application/zip",
                                    use_container_width=True)
        if os.path.exists(w_out):
            with open(w_out, "rb") as _fw:
                dc2.download_button("📥 Word Raporu", data=_fw.read(),
                                    file_name="8B_LGS_Akademik_Basari_ve_Strateji_Raporu.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True)
        if os.path.exists(x_out):
            with open(x_out, "rb") as _fx:
                dc3.download_button("📥 Excel Takip", data=_fx.read(),
                                    file_name="8B_LGS_Takip_Sistemi.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True)

        import time as _time
        _time.sleep(2)
        st.rerun()
elif current_role == "teacher":
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Öğretmen Notu:** Yeni sınav yüklemek için Admin girişi gereklidir.")

st.sidebar.markdown("---")
if current_role in ("admin", "teacher"):
    st.sidebar.info("💡 **Yıl Boyu Kullanım Rehberi:**\nHer deneme sınavından sonra Excel çıktısını (Admin ile) yükleyin.")

# Ogrenci Tanima Formu butonu (sinav secicinin altinda)
if current_role == 'student':
    st.sidebar.markdown('---')
    _form_open = st.session_state.get('show_student_form', False)
    _btn_label = '📋 Tanıma Formunu Kapat ✖' if _form_open else '📋 Öğrenci Tanıma Formunu Doldur'
    if st.sidebar.button(_btn_label, use_container_width=True, type='primary'):
        st.session_state['show_student_form'] = not _form_open
        st.rerun()


# ===================== VERİ YOK KONTROLÜ =====================
if not exams or selected_exam_name == "Kayıtlı Sınav Yok":
    st.warning("Henüz sistemde kayıtlı deneme sınavı bulunmuyor.")
    st.stop()

results = get_exam_results(selected_exam_id)
comps = get_class_comparison(selected_exam_id)

# ===================== BAŞLIK =====================
st.markdown(f"<div class='main-title'>🎓 8/B SINIFI AKADEMİK BAŞARI VE LGS TAKİP SİSTEMİ</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>Aktif Sınav: <b>{selected_exam_name}</b> | "
            f"Örneklem: <b>{len(results)} Öğrenci</b> | "
            f"Rol: <b>{role_info['icon']} {role_info['label']}</b></div>", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║              ÖĞRENCİ GÖRÜNÜMÜ (Sadece Kendi Verisi)     ║
# ╚══════════════════════════════════════════════════════════╝
if current_role == "student":
    student_name = st.session_state.student_name
    st_data = next((r for r in results if r['name'] == student_name), None)

    if not st_data:
        st.error(f"'{student_name}' adına ait bu sınav sonucu bulunamadı.")
        st.stop()

    st_kaz = get_student_kazanims(selected_exam_id, student_name)
    diag = diagnose_student(st_data, st_kaz)
    stats = analyze_class_performance(results)

    if not st.session_state.get("show_student_form", False):
        # --- Öğrenci KPI ---
        st.markdown(f"## 🎒 Hoş Geldiniz, {student_name.title()}!")
        st.markdown("---")

        # İki Deneme Arası Karşılaştırmalı Gelişim Kartı
        try:
            from core.comparative_analyzer import get_multi_exam_comparison
            all_comps = get_multi_exam_comparison()
            my_comp = all_comps.get(student_name)
            if my_comp and my_comp.get('has_both'):
                my_d_net = my_comp.get('delta_net', my_comp.get('d_net', 0.0))
                my_d_puan = my_comp.get('delta_puan', my_comp.get('d_puan', 0.0))
                my_d_rank = my_comp.get('delta_cls_rank', my_comp.get('d_cls_rank', 0))
                my_best = my_comp.get('best_sub', ('-', 0.0))
                my_worst = my_comp.get('worst_sub', ('-', 0.0))
                my_trend = my_comp.get('trend', 'Dengeli')
                my_icon = my_comp.get('trend_icon', '📊')

                st.markdown(
                    f"<div style='background-color:#EBF5FB; border-left:5px solid #2980B9; border-radius:8px; padding:14px; margin-bottom:15px;'>"
                    f"<h4 style='margin:0 0 8px 0; color:#1B4F72;'>📈 Denemeler Arası Gelişim Özeti ({my_comp.get('exam1_name', '1. Deneme')} ➔ {my_comp.get('exam2_name', '2. Deneme')})</h4>"
                    f"<div style='display:flex; gap:20px; flex-wrap:wrap;'>"
                    f"<div><b>Net Değişimi:</b> <span style='color:{'#27AE60' if my_d_net >= 0 else '#C0392B'}; font-weight:bold;'>{my_d_net:+.2f} Net</span></div>"
                    f"<div><b>LGS Puan Değişimi:</b> <span style='color:{'#27AE60' if my_d_puan >= 0 else '#C0392B'}; font-weight:bold;'>{my_d_puan:+.2f} Puan</span></div>"
                    f"<div><b>Sınıf Sırası Değişimi:</b> <span style='color:{'#27AE60' if my_d_rank >= 0 else '#C0392B'}; font-weight:bold;'>{my_d_rank:+d} Sıra</span></div>"
                    f"<div><b>Gelişim Durumu:</b> {my_icon} {my_trend}</div>"
                    f"</div>"
                    f"<div style='margin-top:8px; font-size:13px; color:#2C3E50;'>"
                    f"🚀 <b>En Çok Geliştiğin Branş:</b> {my_best[0]} ({my_best[1]:+.2f} Net) &nbsp;|&nbsp; "
                    f"🎯 <b>Destek Gereken Branş:</b> {my_worst[0]} ({my_worst[1]:+.2f} Net)"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            elif my_comp and not my_comp.get('has_both') and my_comp.get('r2'):
                st.info("🌱 **8/B Sınıfına Hoş Geldin!** Bu senin sınıfımızdaki ilk deneme sınavın. Başlangıç performansın başarıyla kaydedildi.")
            elif my_comp and not my_comp.get('has_both') and my_comp.get('r1'):
                st.warning("ℹ️ **Bu Sınava Katılamadın (Mazeretli).** Bir önceki deneme verilerin ve telafi çalışma programın sistemde korunmaktadır.")
        except Exception as _e_comp:
            pass

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("📝 Toplam Net", f"{st_data['top_net']:.2f}")
        k2.metric("🏆 LGS Puanı", f"{st_data['score']:.2f}")
        k3.metric("📊 Sınıf Sırası", f"{st_data['class_rank']}. / {len(results)}")
        k4.metric("🎯 14. Gün Hedefi", f"{diag['target_14d']} Net")
        k5.metric("📈 28. Gün Hedefi", f"{diag['target_28d']} Net")

        st.markdown("---")

        # --- Sınıf karşılaştırma ---
        col_mine, col_class = st.columns(2)

        with col_mine:
            st.subheader("📊 Ders Bazında Kendi Netlerim")
            subj_map = {
                "Türkçe": st_data.get("tur_net", 0),
                "İnkılap": st_data.get("ink_net", 0),
                "Din Kültürü": st_data.get("din_net", 0),
                "İngilizce": st_data.get("ing_net", 0),
                "Matematik": st_data.get("mat_net", 0),
                "Fen Bilimleri": st_data.get("fen_net", 0),
            }
            fig_me, ax_me = plt.subplots(figsize=(5, 3))
            ax_me.barh(list(subj_map.keys()), list(subj_map.values()), color="#1F497D")
            ax_me.set_xlabel("Net")
            ax_me.grid(axis="x", linestyle="--", alpha=0.4)
            st.pyplot(fig_me)

        with col_class:
            st.subheader("📊 Sınıf Ortalamaları (Karşılaştırma)")
            comp_df = pd.DataFrame(comps)
            if not comp_df.empty:
                fig_c, ax_c = plt.subplots(figsize=(5, 3))
                ax_c.barh(comp_df['subject'], comp_df['class_8b'], color="#117864")
                ax_c.set_xlabel("Sınıf Ort. Net")
                ax_c.grid(axis="x", linestyle="--", alpha=0.4)
                st.pyplot(fig_c)

        st.markdown("---")

        # --- Kazanımlar ---
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.markdown("### 🔴 Sıfır Çekilen Kazanımlar (%0)")
            if diag['zero_kaz']:
                for zk in diag['zero_kaz']:
                    st.error(f"❌ {zk}")
            else:
                st.success("Tebrikler! Sıfır çektiğin kazanım bulunmuyor.")

            st.markdown("### 🟡 Kritik Açıklar (<%50 Başarı)")
            if diag['low_kaz']:
                for lk in diag['low_kaz']:
                    st.warning(f"⚠️ {lk}")
            else:
                st.info("Kritik seviyede düşük kazanım bulunmuyor.")

        with col_k2:
            st.markdown("### 🎯 Gelişim Hedefleri & Strateji")
            st.info(f"**Önerilen Strateji:** {diag['strategy']}")
            st.success(f"**14. Gün Ara Kontrol Hedefi:** {diag['target_14d']} Net")
            st.success(f"**28. Gün (2. Deneme) Hedefi:** {diag['target_28d']} Net")
            st.warning(f"**Haftalık Soru Çözüm Kotası:** {diag['weekly_quota']} Soru + Yanlış Defteri")

            # Karne indirme — Türkçe karakterleri ASCII'ye dönüştür (generate_all_student_cards ile tutarlı)
            def _tr_safe(s):
                return s.replace(' ','_').replace('ç','c').replace('Ç','C').replace('ğ','g').replace('Ğ','G').replace('ı','i').replace('İ','I').replace('ö','o').replace('Ö','O').replace('ş','s').replace('Ş','S').replace('ü','u').replace('Ü','U')
            safe_name = _tr_safe(student_name)
            single_card_path = os.path.join(EXPORTS_DIR, "karneler",
                                             f"{st_data.get('school_no', '000')}_{safe_name}_Karne.docx")
            if not os.path.exists(single_card_path):
                fb_c = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "karneler",
                                    f"{st_data.get('school_no', '000')}_{safe_name}_Karne.docx")
                if os.path.exists(fb_c):
                    single_card_path = fb_c
                else:
                    generate_single_student_card(st_data, selected_exam_name, st_kaz, single_card_path)
            if os.path.exists(single_card_path):
                with open(single_card_path, "rb") as f_card:
                    c_bytes = f_card.read()
                st.download_button(
                    label=f"📥 Karnemi İndir (.docx)",
                    data=c_bytes,
                    file_name=f"{st_data.get('school_no', '000')}_{safe_name}_Karne.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

            # Karnemi İndir Butonunun Altındaki Boş Alana LGS YouTube Öğretmen Listesi Tablosu
            st.markdown(render_lgs_youtube_table_html(), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("---")
        st.markdown("### 🔬 6 Branş İçin Kişiselleştirilmiş Gelişim Reçeteleri")
        sub_recs = get_subject_prescriptions(st_data, st_kaz)

        # 1. DOĞRUDAN GÖRÜNÜR YOUTUBE DERS VİTRİNİ
        st.markdown("#### 📺 Seviyene Özel Önerilen YouTube Dersleri")
        yt_cols = st.columns(3)
        c_idx = 0
        for s_title in ["Türkçe", "Matematik", "Fen Bilimleri", "İnkılap Tarihi", "Din Kültürü", "İngilizce"]:
            if s_title in sub_recs and sub_recs[s_title].get("youtube"):
                s_item = sub_recs[s_title]
                yt = s_item["youtube"]
                with yt_cols[c_idx % 3]:
                    _btns_html = render_yt_buttons_html(yt.get('buttons', []))
                    _badge_color = yt['badge_color']
                    _level_name  = yt['level_name']
                    _channel     = yt['channel']
                    _net_val     = s_item['net']
                    _card_top = (
                        "<div style=\"background-color:#FDF2E9; border-radius:8px; padding:12px;"
                        " border-left:4px solid #E67E22; margin-bottom:12px; box-shadow:0 2px 5px rgba(0,0,0,0.05);\">"
                        "<div style=\"display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;\">"
                        f"<b style=\"color:#78281F; font-size:14px;\">{s_title}</b>"
                        f"<span style=\"background-color:{_badge_color}; color:white; padding:2px 7px; border-radius:8px; font-size:10px; font-weight:bold;\">{_level_name}</span>"
                        "</div>"
                        f"<small style=\"color:#555;\"><b>Netin:</b> {_net_val:.2f} | <b>Kanal:</b> {_channel}</small>"
                    )
                    st.markdown(_card_top + _btns_html + "</div>", unsafe_allow_html=True)
                c_idx += 1

        st.markdown("#### 📋 Ayrıntılı Branş Kazanım Analizi ve Reçeteler")
        sub_cols = st.columns(2)
        idx_c = 0
        for s_title in ["Fen Bilimleri", "Matematik", "Türkçe", "İnkılap Tarihi", "Din Kültürü", "İngilizce"]:
            if s_title in sub_recs:
                s_info = sub_recs[s_title]
                yt = s_info.get('youtube', {})
                yt_tag = f" 📺 {yt.get('channel', '')}" if yt else ""
                with sub_cols[idx_c % 2]:
                    with st.expander(f"{s_info['title']} (Net: {s_info['net']:.2f}){yt_tag}", expanded=False):
                        st.markdown(f"**📊 Kazanım Başarı Dökümü:** {s_info['summary']}")
                        if s_info.get('zero'):
                            st.error(f"**🔴 Sıfır Çekilenler (%0):** {', '.join(s_info['zero'])}")
                        if s_info.get('low'):
                            st.warning(f"**🟡 Pekiştirilecekler (<% 100):** {', '.join(s_info['low'])}")
                        if s_info.get('mast'):
                            st.success(f"**🟢 Tam Hakim Olunanlar:** {len(s_info['mast'])} kazanım")
                        st.info(f"**💡 Çalışma Reçetesi:** {s_info['advice']}")
                        if yt:
                            _btns_html2 = render_yt_buttons_html(yt.get('buttons', []))
                            _yt_ch      = yt['channel']
                            _yt_bc      = yt['badge_color']
                            _yt_ln      = yt['level_name']
                            _yt_focus   = yt['focus']
                            _yt_tip     = yt['study_tip']
                            _yt_box_top = (
                                "<div style=\"background-color:#FDEDEC; border-left:4px solid #C0392B;"
                                " padding:10px; border-radius:6px; margin-top:8px;\">"
                                "<div style=\"display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;\">"
                                f"<span style=\"color:#900C3F; font-weight:bold;\">📺 Önerilen YouTube Desteği: <b>{_yt_ch}</b></span>"
                                f"<span style=\"background-color:{_yt_bc}; color:white; padding:2px 7px; border-radius:10px; font-size:11px; font-weight:bold;\">{_yt_ln}</span>"
                                "</div>"
                                f"<small>🎯 <b>Odak:</b> {_yt_focus}<br>"
                                f"💡 <b>Çalışma Taktiği:</b> {_yt_tip}</small>"
                            )
                            st.markdown(_yt_box_top + _btns_html2 + "</div>", unsafe_allow_html=True)
                idx_c += 1

        # Gelişim Geçmişi
        st_hist = get_student_history(student_name)
        if len(st_hist) > 1:
            st.markdown("---")
            st.markdown("### 📈 Deneme Sınavlarındaki Gelişim Grafiğim")
            df_hist = pd.DataFrame(st_hist)
            fig_h, ax_h = plt.subplots(figsize=(8, 3))
            ax_h.plot(df_hist['exam_name'], df_hist['top_net'], marker='o', linewidth=2, color='#1F497D')
            ax_h.set_ylabel("Net")
            ax_h.grid(True, linestyle='--', alpha=0.5)
            st.pyplot(fig_h)

        # ─────────────────────────────────────────────────────────────────────────
    if st.session_state.get("show_student_form", False):
        # ÖĞRENCİ TANIMA FORMU — Tab yerine doğrudan öğrenci sayfasında göster
        # ─────────────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 📋 Öğrenci Tanıma Formu")
        st.info("📝 Aşağıdaki formu eksiksiz doldurmanı istiyoruz. Yanıtların gizlidir ve yalnızca sınıf öğretmenin görebilir.")

        from core.student_profile import (init_profile_table, save_profile, get_profile,
                                          profile_exists, profile_to_risk_factors)
        init_profile_table()

        stu_id_form = st.session_state.get("student_id")
        # Fallback: student_name üzerinden ID bul
        if not stu_id_form and st.session_state.get("student_name"):
            import sqlite3 as _sq_fb
            from config import DATABASE_PATH as _DB_FB
            _conn_fb = _sq_fb.connect(_DB_FB)
            _row_fb = _conn_fb.execute(
                "SELECT id FROM students WHERE name = ?",
                (st.session_state.student_name,)
            ).fetchone()
            _conn_fb.close()
            if _row_fb:
                st.session_state.student_id = _row_fb[0]
                stu_id_form = _row_fb[0]

        if not stu_id_form:
            st.warning("⚠️ Oturum bilgisi eksik. Lütfen çıkış yapıp tekrar giriş yapın.")
        else:
            profile_done = profile_exists(stu_id_form)
            existing = get_profile(stu_id_form) if profile_done else {}

            if profile_done:
                st.success("✅ Öğrenci Tanıma Formunu doldurdunuz. Teşekkürler!")
                if st.button("📝 Bilgilerimi Güncelle", key="btn_edit_profile_main"):
                    st.session_state["edit_profile"] = True
                    st.rerun()

            if not profile_done or st.session_state.get("edit_profile", False):
                st.info("📋 Lütfen aşağıdaki formu eksiksiz ve doğru doldurun. Bilgileriniz yalnızca öğretmeniniz tarafından görülecektir.")

                import json as _json_form

                with st.container():

                    # ── BÖLÜM 1: Öğrenci Bilgileri ──────────────────────────────────
                    st.markdown("### 👤 Bölüm 1 — Öğrenci Bilgileri")
                    b1c1, b1c2 = st.columns(2)
                    cinsiyet    = b1c1.radio("Cinsiyetiniz", ["Kız", "Erkek"], horizontal=True,
                                             index=0 if existing.get("cinsiyet") == "Kız" else 1 if existing.get("cinsiyet") == "Erkek" else 0)
                    cep_tel     = b1c2.text_input("Cep Telefonu Numaranız", value=existing.get("cep_telefon", ""),
                                                  placeholder="05XX XXX XX XX")
                    dogum_yeri  = b1c1.text_input("Doğum Yeriniz", value=existing.get("dogum_yeri", ""))
                    dogum_tarihi= b1c2.text_input("Doğum Tarihiniz (GG.AA.YYYY)", value=existing.get("dogum_tarihi", ""),
                                                  placeholder="01.01.2010")
                    okul_adi    = b1c1.text_input("Okulunuz", value=existing.get("okul_adi", ""))
                    adres       = b1c2.text_input("Adresiniz", value=existing.get("adres", ""))

                    st.markdown("---")
                    # ── BÖLÜM 2: Aile ve Ev Hayatı ──────────────────────────────────
                    st.markdown("### 🏠 Bölüm 2 — Aile ve Ev Hayatı")

                    kimler_opts = ["Annem ve babam", "Yalnızca annem", "Yalnızca babam",
                                   "Büyükanne / büyükbabam", "Diğer akrabalarım (hala, amca, dayı vb.)",
                                   "Abim / ablam / kardeşlerim", "Diğer"]
                    _ev_default = _json_form.loads(existing.get("evde_kimseler", "[]") or "[]") if existing else []
                    evde_kimseler = st.multiselect("2.1 Evde kimlerle yaşıyorsunuz? (Birden fazla seçebilirsiniz)",
                                                   kimler_opts, default=_ev_default)

                    st.markdown("**2.2 Anneniz hakkında:**")
                    b2a1, b2a2 = st.columns(2)
                    anne_adi    = b2a1.text_input("Annenizin Adı Soyadı", value=existing.get("anne_adi", ""))
                    anne_sag    = b2a2.radio("Anneniz sağ mı?", ["Evet", "Hayır"], horizontal=True,
                                             index=0 if existing.get("anne_sag", "Evet") == "Evet" else 1)
                    anne_egitim = b2a1.selectbox("Annenizin en son bitirdiği okul",
                                                 ["Okuryazar değil", "İlkokul", "Ortaokul", "Lise", "Üniversite"],
                                                 index=["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"].index(existing.get("anne_egitim","Ortaokul")) if existing.get("anne_egitim") in ["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"] else 2)
                    anne_meslek = b2a2.text_input("Annenizin Mesleği", value=existing.get("anne_meslek", ""),
                                                  placeholder="Çalışmıyor / Öğretmen / vb.")

                    st.markdown("**2.3 Babanız hakkında:**")
                    b2b1, b2b2 = st.columns(2)
                    baba_adi    = b2b1.text_input("Babanızın Adı Soyadı", value=existing.get("baba_adi", ""))
                    baba_sag    = b2b2.radio("Babanız sağ mı?", ["Evet", "Hayır"], horizontal=True,
                                             index=0 if existing.get("baba_sag", "Evet") == "Evet" else 1)
                    baba_egitim = b2b1.selectbox("Babanızın en son bitirdiği okul",
                                                 ["Okuryazar değil", "İlkokul", "Ortaokul", "Lise", "Üniversite"],
                                                 index=["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"].index(existing.get("baba_egitim","Ortaokul")) if existing.get("baba_egitim") in ["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"] else 2)
                    baba_meslek = b2b2.text_input("Babanızın Mesleği", value=existing.get("baba_meslek", ""),
                                                  placeholder="Çalışmıyor / Müteahhit / vb.")

                    ebeveyn_opts = ["Evet, birlikte yaşıyorlar", "Hayır, ayrı yaşıyorlar"]
                    ebeveyn_birlikte = st.radio("2.4 Anne ve babanız birlikte mi yaşıyor?",
                                                ebeveyn_opts, horizontal=True,
                                                index=0 if existing.get("ebeveyn_birlikte","Evet, birlikte yaşıyorlar") == "Evet, birlikte yaşıyorlar" else 1)

                    mevsimlik_opts = ["Hayır", "Evet", "Bazen"]
                    mevsimlik_isci = st.radio("2.5 Aile olarak son 1 yılda mevsimlik/geçici bir işte başka şehirlere gittiniz mi?",
                                              mevsimlik_opts, horizontal=True,
                                              index=mevsimlik_opts.index(existing.get("mevsimlik_isci","Hayır")) if existing.get("mevsimlik_isci") in mevsimlik_opts else 0)

                    st.markdown("---")
                    # ── BÖLÜM 3: Kardeşler ──────────────────────────────────────────
                    st.markdown("### 👨‍👩‍👧‍👦 Bölüm 3 — Kardeşler")
                    b3c1, b3c2, b3c3 = st.columns(3)
                    kardes_sayisi       = b3c1.number_input("Kaç kardeşiniz var?", min_value=0, max_value=20,
                                                            value=int(existing.get("kardes_sayisi") or 0))
                    kacinci_cocuk       = b3c2.number_input("Ailenizin kaçıncı çocuğusunuz?", min_value=1, max_value=20,
                                                            value=int(existing.get("kacinci_cocuk") or 1))
                    okula_giden_kardes  = b3c3.number_input("Okula giden kardeş sayınız", min_value=0, max_value=20,
                                                            value=int(existing.get("okula_giden_kardes") or 0))

                    st.markdown("---")
                    # ── BÖLÜM 4: Sağlık ─────────────────────────────────────────────
                    st.markdown("### 🏥 Bölüm 4 — Sağlık Bilgileri")
                    _ilac_c1, _ilac_c2 = st.columns([1, 2])
                    ilac_kullaniyor = _ilac_c1.radio("4.1 Sürekli kullandığınız bir ilaç veya tıbbi cihazınız var mı?",
                                                    ["Hayır", "Evet"], horizontal=True,
                                                    index=0 if existing.get("ilac_kullaniyor","Hayır") == "Hayır" else 1)
                    ilac_adi = _ilac_c2.text_input("İlaç / cihaz adı",
                                                   value=existing.get("ilac_adi","") if ilac_kullaniyor == "Evet" else "",
                                                   disabled=(ilac_kullaniyor != "Evet"),
                                                   placeholder="İlaç veya cihaz adını yazınız..." if ilac_kullaniyor == "Evet" else "('Evet' seçilince aktif olur)")

                    _tani_c1, _tani_c2 = st.columns([1, 2])
                    tani_var = _tani_c1.radio("4.2 Tanısı konulmuş bir hastalığınız ya da engel durumunuz var mı?",
                                             ["Hayır", "Evet"], horizontal=True,
                                             index=0 if existing.get("tani_var","Hayır") == "Hayır" else 1)
                    tani_aciklama = _tani_c2.text_input("Tanısı nedir?",
                                                        value=existing.get("tani_aciklama","") if tani_var == "Evet" else "",
                                                        disabled=(tani_var != "Evet"),
                                                        placeholder="Örn: DEHB, Astım, Görme engeli..." if tani_var == "Evet" else "('Evet' seçilince aktif olur)")

                    ozel_egitim_opts = ["Hayır", "Evet, özel eğitim alıyorum",
                                        "Evet, kaynaştırma öğrencisiyim", "Evet, destek eğitimi alıyorum"]
                    ozel_egitim = st.radio("4.3 Özel eğitim, kaynaştırma veya destek eğitimi alıyor musunuz?",
                                           ozel_egitim_opts,
                                           index=ozel_egitim_opts.index(existing.get("ozel_egitim","Hayır")) if existing.get("ozel_egitim") in ozel_egitim_opts else 0)

                    _aile_c1, _aile_c2 = st.columns([1, 2])
                    ailede_hastalik = _aile_c1.radio("4.4 Ailenizde uzun süreli bir hastalığı ya da engel durumu olan biri var mı?",
                                                     ["Hayır", "Evet"], horizontal=True,
                                                     index=0 if existing.get("ailede_hastalik","Hayır") == "Hayır" else 1)
                    ailede_aciklama = _aile_c2.text_input("Kim, ne hastalığı?",
                                                          value=existing.get("ailede_aciklama","") if ailede_hastalik == "Evet" else "",
                                                          disabled=(ailede_hastalik != "Evet"),
                                                          placeholder="Örn: Annem - şeker hastalığı / Babam - kalp..." if ailede_hastalik == "Evet" else "('Evet' seçilince aktif olur)")

                    st.markdown("---")
                    # ── BÖLÜM 5: Okul Hayatı ────────────────────────────────────────
                    st.markdown("### 🏫 Bölüm 5 — Okul Hayatı")
                    devamsizlik_opts = ["Hiç gitmedim (0 gün)", "1–3 gün", "4–9 gün", "10 gün ve üzeri"]
                    devamsizlik_gun  = st.radio("5.1 Bu dönem yaklaşık kaç gün okula gidemediniz?",
                                                devamsizlik_opts,
                                                index=devamsizlik_opts.index(existing.get("devamsizlik_gun","Hiç gitmedim (0 gün)")) if existing.get("devamsizlik_gun") in devamsizlik_opts else 0)

                    zorluk_opts = ["Hayır, genellikle takip edebiliyorum",
                                   "Bazı derslerde zorlanıyorum",
                                   "Evet, çoğu derste ciddi zorluk çekiyorum"]
                    ders_zorluk = st.radio("5.2 Dersleri takip etmekte zorlanıyor musunuz?",
                                           zorluk_opts,
                                           index=zorluk_opts.index(existing.get("ders_zorluk","Hayır, genellikle takip edebiliyorum")) if existing.get("ders_zorluk") in zorluk_opts else 0)

                    ders_opts = ["Türkçe","Matematik","Fen Bilimleri","İngilizce",
                                 "Sosyal Bilgiler / İnkılap Tarihi","Din Kültürü"]
                    _zor_default = _json_form.loads(existing.get("zor_dersler","[]") or "[]") if existing else []
                    zor_dersler  = st.multiselect("5.3 Hangi dersler en zor geliyor? (Birden fazla seçebilirsiniz)",
                                                  ders_opts, default=_zor_default)

                    degistirdi_opts = ["Hayır, bu okulda sürekliyim",
                                       "Evet, bu yıl okul değiştirdim",
                                       "Evet, geçen yıl değiştirdim"]
                    okul_degistirdi = st.radio("5.4 Okula yakın zamanda yeni mi başladınız ya da okul değiştirdiniz mi?",
                                               degistirdi_opts,
                                               index=degistirdi_opts.index(existing.get("okul_degistirdi","Hayır, bu okulda sürekliyim")) if existing.get("okul_degistirdi") in degistirdi_opts else 0)

                    arkadas_opts = ["Kolaylıkla arkadaş edinebiliyorum",
                                    "Bazen zorluk çekiyorum",
                                    "Genellikle yalnız kalıyorum"]
                    arkadas_edinme = st.radio("5.5 Okulda arkadaş edinmekte nasıl buluyorsunuz kendinizi?",
                                              arkadas_opts,
                                              index=arkadas_opts.index(existing.get("arkadas_edinme","Kolaylıkla arkadaş edinebiliyorum")) if existing.get("arkadas_edinme") in arkadas_opts else 0)

                    st.markdown("---")
                    # ── BÖLÜM 6: Günlük Hayat ───────────────────────────────────────
                    st.markdown("### 🌇 Bölüm 6 — Günlük Hayat")
                    calisma_opts = ["Hayır", "Evet, hafta sonları yardım ediyorum",
                                    "Evet, hafta içi düzenli çalışıyorum"]
                    calisma_durumu = st.radio("6.1 Okul dışında bir işte ya da tezgâhta çalışıyor musunuz?",
                                              calisma_opts,
                                              index=calisma_opts.index(existing.get("calisma_durumu","Hayır")) if existing.get("calisma_durumu") in calisma_opts else 0)

                    ortam_opts = ["Evet, rahat bir çalışma yerim var",
                                  "Bazen olmuyor",
                                  "Hayır, genellikle çalışacak ortam bulamıyorum"]
                    ders_ortami = st.radio("6.2 Ders çalışmak için evde sessiz bir ortamınız var mı?",
                                           ortam_opts,
                                           index=ortam_opts.index(existing.get("ders_ortami","Evet, rahat bir çalışma yerim var")) if existing.get("ders_ortami") in ortam_opts else 0)

                    internet_opts = ["Evet, evde var", "Yalnızca telefonum var",
                                     "Hayır, çoğu zaman erişemiyorum"]
                    internet_erisim = st.radio("6.3 İnternete ve bilgisayara erişiminiz var mı?",
                                               internet_opts,
                                               index=internet_opts.index(existing.get("internet_erisim","Evet, evde var")) if existing.get("internet_erisim") in internet_opts else 0)

                    tekno_opts = ["Tablet / Bilgisayar", "Akıllı telefon", "Akıllı saat / tablet", "Hiçbiri"]
                    _tekno_default = _json_form.loads(existing.get("teknoloji_aleti","[]") or "[]") if existing and isinstance(existing.get("teknoloji_aleti",""), str) and existing.get("teknoloji_aleti","").startswith("[") else ([existing.get("teknoloji_aleti")] if existing.get("teknoloji_aleti") and existing.get("teknoloji_aleti") in tekno_opts else [])
                    teknoloji_aleti = st.multiselect("6.4 Kendinize ait teknolojik aletleriniz neler? (Birden fazla seçebilirsiniz)",
                                                     tekno_opts, default=_tekno_default)

                    st.markdown("---")
                    # ── BÖLÜM 7: İlgi ve Hobiler ───────────────────────────────────
                    st.markdown("### 🎨 Bölüm 7 — İlgi ve Hobiler")
                    hobi_opts = ["Spor / Hareket", "Müzik / Sanat / Resim",
                                 "Kitap okumak", "Teknoloji / Oyun", "Doğa / Gezi", "Diğer"]
                    _hobi_default = _json_form.loads(existing.get("hobiler","[]") or "[]") if existing else []
                    hobiler = st.multiselect("7.1 Ne yapmaktan hoşlanırsınız? (Birden fazla seçebilirsiniz)",
                                             hobi_opts, default=_hobi_default)

                    _kurs_c1, _kurs_c2 = st.columns([1, 2])
                    kurs_kulup = _kurs_c1.radio("7.2 Okul dışında katıldığınız bir spor, sanat veya hobi kulübü var mı?",
                                                ["Hayır", "Evet"], horizontal=True,
                                                index=0 if existing.get("kurs_kulup","Hayır") == "Hayır" else 1)
                    kurs_brans = _kurs_c2.text_input("Hangi branş(lar)? (Birden fazlaysa araya tire '-' koyun)",
                                                     value=existing.get("kurs_brans","") if kurs_kulup == "Evet" else "",
                                                     disabled=(kurs_kulup != "Evet"),
                                                     placeholder="Örn: Yüzme - Basketbol (Tire ile ayırınız)" if kurs_kulup == "Evet" else "('Evet' seçilince aktif olur)")
                    kurs_adi = kurs_brans

                    akademik_destek_opts = ["Hayır, almıyorum", "Okul kursu (ücretsiz)", "Dershane / Etüt merkezi",
                                            "Özel ders (bireysel)", "Online kurs / platform (Eba, YouTube vb.)"]
                    _akad_default = _json_form.loads(existing.get("akademik_destek","[]") or "[]") if existing and isinstance(existing.get("akademik_destek",""), str) and existing.get("akademik_destek","").startswith("[") else ([existing.get("akademik_destek")] if existing.get("akademik_destek") and existing.get("akademik_destek") in akademik_destek_opts else [])
                    akademik_destek = st.multiselect(
                        "7.3 Okul dışında akademik destek alıyor musunuz? (Birden fazla seçebilirsiniz)",
                        akademik_destek_opts, default=_akad_default)

                    st.markdown("---")
                    # ── BÖLÜM 8: Kendini Anlat ─────────────────────────────────────
                    st.markdown("### 💬 Bölüm 8 — Kendini Anlat")
                    his_opts = ["😊 İyi, mutluyum", "😐 Fena değil, idare ediyorum",
                                "😟 Son zamanlarda biraz zorlanıyorum",
                                "😔 Çok zorlanıyorum, destek istiyorum"]
                    genel_his = st.radio("8.1 Kendinizi genel olarak nasıl hissediyorsunuz? (Okul hayatı açısından)",
                                         his_opts,
                                         index=his_opts.index(existing.get("genel_his","😊 İyi, mutluyum")) if existing.get("genel_his") in his_opts else 0)

                    zorlastiran_sey = st.text_area("8.2 Okul hayatında sizi en çok zorlaştıran şey nedir? (İsteğe bağlı)",
                                                   value=existing.get("zorlastiran_sey",""),
                                                   placeholder="Örn: ulaşım, ders çalışma ortamı, sosyal ilişkiler...")

                    destek_opts = ["Hayır, şu an gerek duymuyorum",
                                   "Evet, ders konularında destek istiyorum",
                                   "Evet, kişisel bir şeyi paylaşmak istiyorum"]
                    destek_istek = st.radio("8.3 Öğretmenlerinizden ya da okul rehberinden özel destek almak ister misiniz?",
                                            destek_opts,
                                            index=destek_opts.index(existing.get("destek_istek","Hayır, şu an gerek duymuyorum")) if existing.get("destek_istek") in destek_opts else 0)

                    onemli_olay = st.radio("8.4 Hala etkisi altında olduğunuz önemli bir olay ya da değişiklik yaşadınız mı?",
                                           ["Hayır", "Evet (detay vermek zorunda değilsiniz)"],
                                           horizontal=True,
                                           index=0 if existing.get("onemli_olay","Hayır") == "Hayır" else 1)

                    st.markdown("---")
                    # ── BÖLÜM 9: Veli Bilgileri ────────────────────────────────────
                    st.markdown("### 👨‍👩‍👧 Bölüm 9 — Veli Bilgileri")
                    st.caption("Bu bölümü mümkünse veliye doldurun ya da sonradan güncelleyin.")
                    b9c1, b9c2 = st.columns(2)
                    veli_adi       = b9c1.text_input("Veli Adı Soyadı", value=existing.get("veli_adi",""))
                    veli_yakin_opts = ["Anne", "Baba", "Büyükanne / Büyükbaba", "Diğer"]
                    veli_yakinligi = b9c2.selectbox("Yakınlığı",
                                                    veli_yakin_opts,
                                                    index=veli_yakin_opts.index(existing.get("veli_yakinligi","Anne")) if existing.get("veli_yakinligi") in veli_yakin_opts else 0)
                    veli_telefon   = b9c1.text_input("Telefon Numarası", value=existing.get("veli_telefon",""),
                                                     placeholder="05XX XXX XX XX")
                    veli_egitim_opts = ["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"]
                    veli_egitim    = b9c2.selectbox("Eğitim Durumu", veli_egitim_opts,
                                                    index=veli_egitim_opts.index(existing.get("veli_egitim","Ortaokul")) if existing.get("veli_egitim") in veli_egitim_opts else 2)
                    veli_meslek    = b9c1.text_input("Mesleği", value=existing.get("veli_meslek",""))

                    st.markdown("---")
                    submitted_profile = st.button("✅ Formu Kaydet", use_container_width=True, type="primary", key="btn_submit_prof_main")

                if submitted_profile:
                    profile_data = {
                        "cinsiyet": cinsiyet, "dogum_yeri": dogum_yeri,
                        "dogum_tarihi": dogum_tarihi, "okul_adi": okul_adi,
                        "adres": adres, "cep_telefon": cep_tel,
                        "evde_kimseler": _json_form.dumps(evde_kimseler, ensure_ascii=False),
                        "anne_adi": anne_adi, "anne_sag": anne_sag,
                        "anne_egitim": anne_egitim, "anne_meslek": anne_meslek,
                        "baba_adi": baba_adi, "baba_sag": baba_sag,
                        "baba_egitim": baba_egitim, "baba_meslek": baba_meslek,
                        "ebeveyn_birlikte": ebeveyn_birlikte,
                        "mevsimlik_isci": mevsimlik_isci,
                        "kardes_sayisi": kardes_sayisi, "kacinci_cocuk": kacinci_cocuk,
                        "okula_giden_kardes": okula_giden_kardes,
                        "ilac_kullaniyor": ilac_kullaniyor, "ilac_adi": ilac_adi,
                        "tani_var": tani_var, "tani_aciklama": tani_aciklama,
                        "ozel_egitim": ozel_egitim, "ailede_hastalik": ailede_hastalik, "ailede_aciklama": ailede_aciklama,
                        "devamsizlik_gun": devamsizlik_gun, "ders_zorluk": ders_zorluk,
                        "zor_dersler": _json_form.dumps(zor_dersler, ensure_ascii=False),
                        "okul_degistirdi": okul_degistirdi,
                        "arkadas_edinme": arkadas_edinme,
                        "calisma_durumu": calisma_durumu, "ders_ortami": ders_ortami,
                        "internet_erisim": internet_erisim, "teknoloji_aleti": _json_form.dumps(teknoloji_aleti, ensure_ascii=False),
                        "hobiler": _json_form.dumps(hobiler, ensure_ascii=False),
                        "kurs_kulup": kurs_kulup, "kurs_adi": kurs_adi,
                        "kurs_brans": kurs_brans,
                        "akademik_destek": _json_form.dumps(akademik_destek, ensure_ascii=False),
                        "genel_his": genel_his, "zorlastiran_sey": zorlastiran_sey,
                        "destek_istek": destek_istek, "onemli_olay": onemli_olay,
                        "veli_adi": veli_adi, "veli_yakinligi": veli_yakinligi,
                        "veli_telefon": veli_telefon, "veli_egitim": veli_egitim,
                        "veli_meslek": veli_meslek,
                    }
                    save_profile(stu_id_form, profile_data)
                    profile_to_risk_factors(stu_id_form, profile_data)
                    st.session_state["edit_profile"] = False
                    st.success("✅ Bilgileriniz başarıyla kaydedildi!")
                    st.balloons()
                    st.rerun()

    st.stop()  # Öğrenci görünümü burada biter


# ╔══════════════════════════════════════════════════════════╗
# ║       ÖĞRETMEN & ADMİN GÖRÜNÜMÜ (Tam Dashboard)         ║
# ╚══════════════════════════════════════════════════════════╝

tabs_list = [
    "📊 Sınıf Genel Görünümü",
    "🎯 Kazanım & Pareto Analizi",
    "👤 Bireysel Öğrenci Karneleri",
    "📚 Branş Öğretmen Raporları",
    "📈 Çoklu Deneme Gelişim Takibi",
    "🗺️ Risk Haritası",
    "⚡ Otomatik Rapor & Karne Üretici"
]
tab1, tab2, tab3, tab_branch, tab4, tab_risk, tab5 = st.tabs(tabs_list)

# ----------------- TAB 1: Sınıf Genel Görünümü -----------------
with tab1:
    stats = analyze_class_performance(results)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Öğrenci Sayısı", f"{stats.get('count', 0)}")
    c1.caption("8/B Şubesi Aktif Katılım")
    c2.metric("Sınıf Net Ortalaması", f"{stats.get('mean_net', 0.0):.2f}", delta="+0.93 Okul Üstü")
    c2.caption("Okul Ort: 36.50 Net")
    c3.metric("Sınıf Medyan Neti", f"{stats.get('median_net', 0.0):.2f}")
    c3.caption("Merkezi Eğilim")
    c4.metric("LGS Puan Ortalaması", f"{stats.get('mean_score', 0.0):.2f}", delta="+0.48 Okul Üstü")
    c4.caption("Okul Ort: 303.52")
    c5.metric("Zirve - Taban Makası", f"{stats.get('max_net', 0.0):.1f} / {stats.get('min_net', 0.0):.1f}")
    c5.caption(f"Sapma: {stats.get('std_net', 0.0):.2f} Net")

    st.markdown("---")
    col_chart, col_tiers = st.columns([3.2, 1.8])
    with col_chart:
        st.subheader("📌 Ders Bazında 8/B, Diğer Şubeler ve Okul Karşılaştırması")
        comp_df = pd.DataFrame(comps)
        if not comp_df.empty:
            potential_series = [
                {'col': 'class_8a', 'label': '8/A Sınıfı', 'color': '#2980B9'},
                {'col': 'class_8b', 'label': '8/B Sınıfı (Biz)', 'color': '#1A365D'},
                {'col': 'class_8c', 'label': '8/C Sınıfı', 'color': '#E67E22'},
                {'col': 'class_8d', 'label': '8/D Sınıfı', 'color': '#8E44AD'},
                {'col': 'school_avg', 'label': 'Okul Ortalaması', 'color': '#7F8C8D'}
            ]
            active_series = [s for s in potential_series if s['col'] in comp_df.columns and (comp_df[s['col']] > 0).any()]

            # Toplam Net karşılaştırma kartları
            toplam_row = comp_df[comp_df['subject'] == 'Toplam Net']
            if not toplam_row.empty:
                toplam_dict = toplam_row.iloc[0].to_dict()
                m_cols = st.columns(len(active_series))
                for m_idx, s in enumerate(active_series):
                    val_net = toplam_dict.get(s['col'], 0.0)
                    is_8b = '8/B' in s['label']
                    with m_cols[m_idx]:
                        diff_val = val_net - toplam_dict.get('school_avg', 0.0)
                        st.metric(
                            label=f"{'⭐ ' if is_8b else ''}{s['label']}",
                            value=f"{val_net:.2f} Net",
                            delta=f"{diff_val:+.2f} Okul Farkı" if s['col'] != 'school_avg' else None
                        )

            # Branşlar için çoklu sütun grafiği
            comp_df_subj = comp_df[comp_df['subject'] != 'Toplam Net'].copy()
            if not comp_df_subj.empty:
                K = len(active_series)
                bar_width = 0.82 / K
                x = np.arange(len(comp_df_subj))

                fig, ax = plt.subplots(figsize=(9, 4.5))

                for i, s in enumerate(active_series):
                    offset = (i - (K - 1) / 2) * bar_width
                    is_our = '8/B' in s['label']
                    bars = ax.bar(
                        x + offset, comp_df_subj[s['col']], bar_width,
                        label=s['label'], color=s['color'],
                        edgecolor='#0E2F44' if is_our else 'white',
                        linewidth=1.5 if is_our else 0.5,
                        zorder=3 if is_our else 2
                    )
                    for bar in bars:
                        h = bar.get_height()
                        if h > 0:
                            ax.annotate(
                                f'{h:.1f}',
                                xy=(bar.get_x() + bar.get_width() / 2, h),
                                xytext=(0, 3),
                                textcoords='offset points',
                                ha='center', va='bottom',
                                fontsize=7.5 if K > 3 else 8.5,
                                fontweight='bold' if is_our else 'normal',
                                color='#1A365D' if is_our else '#444444'
                            )

                ax.set_xticks(x)
                ax.set_xticklabels(comp_df_subj['subject'], rotation=15, ha='right', fontsize=9, fontweight='500')
                ax.set_ylabel("Ortalama Net", fontsize=10)
                max_val = comp_df_subj[[s['col'] for s in active_series]].max().max() if not comp_df_subj.empty else 10
                ax.set_ylim(0, max(max_val * 1.18, 5))
                ax.legend(frameon=True, facecolor='white', edgecolor='#D5D8DC', fontsize=8.5)
                ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
                plt.tight_layout()
                st.pyplot(fig)

            # Ayrıntılı Karşılaştırma Tablosu
            table_cols = {'subject': 'Ders / Alan'}
            for s in active_series:
                table_cols[s['col']] = f"{s['label']} Net"
            comp_display = comp_df.copy()
            if 'class_8b' in comp_display.columns and 'school_avg' in comp_display.columns:
                comp_display['fark_str'] = (comp_display['class_8b'] - comp_display['school_avg']).apply(lambda v: f"{v:+.2f}")
                table_cols['fark_str'] = "8/B Okul Farkı (Δ)"
            df_show = comp_display[list(table_cols.keys())].rename(columns=table_cols)
            with st.expander("📋 Tüm Şubeler ve Okul Net Karşılaştırma Tablosu", expanded=True):
                st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("Karşılaştırma verisi bulunmuyor.")

    with col_tiers:
        st.subheader("🏅 Başarı Kademeleri (Tiers)")
        tiers = stats.get('tiers', {})
        for tname, members in tiers.items():
            st.markdown(f"**{tname}:** `{len(members)} Öğrenci` (%{len(members)/stats.get('count', 1)*100:.1f})")
            st.caption(", ".join(members[:5]) + ("..." if len(members) > 5 else ""))

    st.subheader("📋 8/B Sınıf Sıralama Listesi")
    df_res = pd.DataFrame(results)[['class_rank', 'school_no', 'name', 'tur_net', 'ink_net', 'din_net',
                                     'ing_net', 'mat_net', 'fen_net', 'top_net', 'score', 'school_rank',
                                     'tg_rank', 'tg_percentile']]
    df_res.columns = ['S.Sıra', 'No', 'Adı Soyadı', 'Türkçe', 'İnkılap', 'Din', 'İngilizce',
                      'Matematik', 'Fen', 'Toplam Net', 'LGS Puanı', 'Okul Sıra', 'TG Sıra', 'TG % Dilim']
    st.dataframe(df_res.style.highlight_max(axis=0, subset=['Toplam Net'], color='#D4EFDF'), use_container_width=True)

# ----------------- TAB 2: Kazanım & Pareto -----------------
with tab2:
    st.subheader("📊 Pareto Net Kaybı Analizi (80/20 Kuralı)")
    pareto_data = calculate_pareto(results)
    df_p = pd.DataFrame(pareto_data)

    c_p1, c_p2 = st.columns([3, 2])
    with c_p1:
        fig_p, ax_p = plt.subplots(figsize=(8, 4))
        ax_p.bar(df_p['subject'], df_p['lost_net'], color='#C0392B', alpha=0.85, label='Kaybedilen Net')
        ax_p.set_ylabel("Kaybedilen Net", color='#C0392B')
        ax_p.set_xticklabels(df_p['subject'], rotation=15, ha='right')
        ax_p2 = ax_p.twinx()
        ax_p2.plot(df_p['subject'], df_p['cum_pct'], color='#1F497D', marker='o', linewidth=2)
        ax_p2.set_ylabel("Kümülatif Kayıp %", color='#1F497D')
        ax_p2.set_ylim(0, 110)
        ax_p.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig_p)

    with c_p2:
        st.dataframe(df_p[['rank', 'subject', 'lost_net', 'total_y', 'total_b', 'share_pct', 'cum_pct']].rename(
            columns={'rank': 'Sıra', 'subject': 'Ders', 'lost_net': 'Kayıp Net',
                     'total_y': 'Yanlış', 'total_b': 'Boş', 'share_pct': 'Pay %', 'cum_pct': 'Küm %'}
        ), use_container_width=True)
        st.warning("⚠️ **Önemli:** Matematik, Türkçe ve Fen toplam net kaybının **%71.61'ini** oluşturmaktadır.")

# ----------------- TAB 3: Bireysel Öğrenci Karneleri -----------------
with tab3:
    st.subheader("👤 Bireysel Öğrenci Başarı Karnesi ve Gelişim Kartı")

    with st.expander("📺 8/B Branş ve Seviye Bazlı YouTube Destek Kataloğu (Öğretmen & Veli Rehberi)", expanded=False):
        st.markdown(render_lgs_youtube_table_html(), unsafe_allow_html=True)

    st_names = [r['name'] for r in results]
    selected_student = st.selectbox("Öğrenci Seçin:", st_names)

    st_data = next((r for r in results if r['name'] == selected_student), None)
    st_kaz = get_student_kazanims(selected_exam_id, selected_student)

    if st_data:
        diag = diagnose_student(st_data, st_kaz)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Toplam Net", f"{st_data['top_net']:.2f}")
        k2.metric("LGS Puanı", f"{st_data['score']:.2f}")
        k3.metric("Sınıf / Okul Sırası", f"{st_data['class_rank']}. / {st_data['school_rank'] or '-'} (110 kişi)")
        k4.metric("Türkiye Geneli Sıra / Dilim", f"{st_data['tg_rank'] or '-'} / %{st_data['tg_percentile'] or '-'}")

        st.markdown("---")
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.markdown("### 🔴 Sıfır Çekilen Kazanımlar (%0 Başarı)")
            if diag['zero_kaz']:
                for zk in diag['zero_kaz']:
                    st.error(f"❌ {zk}")
            else:
                st.success("Tebrikler! Öğrencinin sıfır çektiği kazanım bulunmuyor.")

            st.markdown("### 🟡 Kritik Açıklar (<%50 Başarı)")
            if diag['low_kaz']:
                for lk in diag['low_kaz']:
                    st.warning(f"⚠️ {lk}")
            else:
                st.info("Kritik seviyede düşük kazanım bulunmuyor.")

        with col_k2:
            st.markdown("### 🎯 Bireysel Gelişim Hedefleri & Strateji")
            st.info(f"**Önerilen Strateji:** {diag['strategy']}")
            st.success(f"**14. Gün Ara Kontrol Hedefi:** {diag['target_14d']} Net")
            st.success(f"**28. Gün (2. Deneme) Hedefi:** {diag['target_28d']} Net")
            st.warning(f"**Haftalık Soru Çözüm Kotası:** {diag['weekly_quota']} Soru + Yanlış Defteri")

            # Download — Türkçe karakterleri ASCII'ye dönüştür (generate_all_student_cards ile tutarlı)
            def _tr_safe2(s):
                return s.replace(' ','_').replace('ç','c').replace('Ç','C').replace('ğ','g').replace('Ğ','G').replace('ı','i').replace('İ','I').replace('ö','o').replace('Ö','O').replace('ş','s').replace('Ş','S').replace('ü','u').replace('Ü','U')
            safe_name = _tr_safe2(selected_student)
            single_card_path = os.path.join(EXPORTS_DIR, "karneler",
                                             f"{st_data.get('school_no', '000')}_{safe_name}_Karne.docx")
            if not os.path.exists(single_card_path):
                fb_c = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "karneler",
                                    f"{st_data.get('school_no', '000')}_{safe_name}_Karne.docx")
                if os.path.exists(fb_c):
                    single_card_path = fb_c
                else:
                    generate_single_student_card(st_data, selected_exam_name, st_kaz, single_card_path)
            if os.path.exists(single_card_path):
                with open(single_card_path, "rb") as f_card:
                    c_bytes = f_card.read()
                st.download_button(
                    label=f"📥 {selected_student} Karnesini İndir (.docx)",
                    data=c_bytes,
                    file_name=f"{st_data.get('school_no', '000')}_{safe_name}_Karne.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

            # Karnemi İndir Butonunun Altındaki Boş Alana LGS YouTube Öğretmen Listesi Tablosu
            st.markdown(render_lgs_youtube_table_html(), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🔬 6 Branş İçin Kişiselleştirilmiş Gelişim Reçeteleri")
        sub_recs = get_subject_prescriptions(st_data, st_kaz)

        # 1. DOĞRUDAN GÖRÜNÜR YOUTUBE DERS VİTRİNİ
        st.markdown("#### 📺 Öğrenciye Özel Önerilen YouTube Dersleri")
        yt_cols3 = st.columns(3)
        c_idx3 = 0
        for s_title in ["Türkçe", "Matematik", "Fen Bilimleri", "İnkılap Tarihi", "Din Kültürü", "İngilizce"]:
            if s_title in sub_recs and sub_recs[s_title].get("youtube"):
                s_item = sub_recs[s_title]
                yt = s_item["youtube"]
                with yt_cols3[c_idx3 % 3]:
                    _btns3 = render_yt_buttons_html(yt.get('buttons', []))
                    _bc3   = yt['badge_color']
                    _ln3   = yt['level_name']
                    _ch3   = yt['channel']
                    _nv3   = s_item['net']
                    _card3_top = (
                        "<div style=\"background-color:#FDF2E9; border-radius:8px; padding:12px;"
                        " border-left:4px solid #E67E22; margin-bottom:12px; box-shadow:0 2px 5px rgba(0,0,0,0.05);\">"
                        "<div style=\"display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;\">"
                        f"<b style=\"color:#78281F; font-size:14px;\">{s_title}</b>"
                        f"<span style=\"background-color:{_bc3}; color:white; padding:2px 7px; border-radius:8px; font-size:10px; font-weight:bold;\">{_ln3}</span>"
                        "</div>"
                        f"<small style=\"color:#555;\"><b>Net:</b> {_nv3:.2f} | <b>Kanal:</b> {_ch3}</small>"
                    )
                    st.markdown(_card3_top + _btns3 + "</div>", unsafe_allow_html=True)
                c_idx3 += 1

        st.markdown("#### 📋 Ayrıntılı Branş Kazanım Analizi ve Reçeteler")
        sub_cols = st.columns(2)
        idx_c = 0
        for s_title in ["Fen Bilimleri", "Matematik", "Türkçe", "İnkılap Tarihi", "Din Kültürü", "İngilizce"]:
            if s_title in sub_recs:
                s_info = sub_recs[s_title]
                yt = s_info.get('youtube', {})
                yt_tag = f" 📺 {yt.get('channel', '')}" if yt else ""
                with sub_cols[idx_c % 2]:
                    with st.expander(f"{s_info['title']} (Net: {s_info['net']:.2f}){yt_tag}", expanded=False):
                        st.markdown(f"**📊 Kazanım Başarı Dökümü:** {s_info['summary']}")
                        if s_info.get('zero'):
                            st.error(f"**🔴 Sıfır Çekilenler:** {', '.join(s_info['zero'])}")
                        if s_info.get('low'):
                            st.warning(f"**🟡 Pekiştirilecekler:** {', '.join(s_info['low'])}")
                        if s_info.get('mast'):
                            st.success(f"**🟢 Tam Hakim Olunanlar:** {len(s_info['mast'])} kazanım")
                        st.info(f"**💡 Çalışma Reçetesi:** {s_info['advice']}")
                        if yt:
                            _btns3b  = render_yt_buttons_html(yt.get('buttons', []))
                            _yt3_ch  = yt['channel']
                            _yt3_bc  = yt['badge_color']
                            _yt3_ln  = yt['level_name']
                            _yt3_foc = yt['focus']
                            _yt3_tip = yt['study_tip']
                            _yt3_top = (
                                "<div style=\"background-color:#FDEDEC; border-left:4px solid #C0392B;"
                                " padding:10px; border-radius:6px; margin-top:8px;\">"
                                "<div style=\"display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;\">"
                                f"<span style=\"color:#900C3F; font-weight:bold;\">📺 Önerilen YouTube Desteği: <b>{_yt3_ch}</b></span>"
                                f"<span style=\"background-color:{_yt3_bc}; color:white; padding:2px 7px; border-radius:10px; font-size:11px; font-weight:bold;\">{_yt3_ln}</span>"
                                "</div>"
                                f"<small>🎯 <b>Odak:</b> {_yt3_foc}<br>"
                                f"💡 <b>Çalışma Taktiği:</b> {_yt3_tip}</small>"
                            )
                            st.markdown(_yt3_top + _btns3b + "</div>", unsafe_allow_html=True)
                idx_c += 1

# ----------------- TAB BRANŞ: Branş Öğretmen Raporları -----------------
with tab_branch:
    st.subheader("📚 Branş Öğretmenleri — Sınıf Akademik Teşhis Merkezi")
    st.caption("Her branş öğretmeni kendi dersine ait sınıf geneli istatistikleri, kazanım başarı oranlarını ve bireysel öğrenci performanslarını bu ekrandan inceler.")

    col_bsel1, col_bsel2, col_bsel3 = st.columns([2.5, 1.8, 1.8])
    with col_bsel1:
        chosen_branch = st.selectbox(
            "🔎 İncelemek İstediğiniz Branşı Seçin:",
            options=list(SUBJECTS.keys()),
            key="select_branch_view"
        )

    # Kazanım verisi haritası
    all_kaz_data = {r['name']: get_student_kazanims(selected_exam_id, r['name']) for r in results}
    b_data = analyze_branch_data(chosen_branch, results, all_kaz_data, comps)

    with col_bsel2:
        # Tek branş Word raporu — her seferinde taze üret
        tr_safe_sub = norm_text(chosen_branch).replace(" ", "_").upper()
        br_dir = os.path.join(EXPORTS_DIR, "brans_raporlari")
        os.makedirs(br_dir, exist_ok=True)
        single_br_path = os.path.join(br_dir, f"8B_{tr_safe_sub}_Brans_Raporu.docx")
        try:
            generate_branch_word_report(chosen_branch, selected_exam_name, results, all_kaz_data, comps, single_br_path)
            if os.path.exists(single_br_path):
                with open(single_br_path, "rb") as f_br:
                    br_bytes = f_br.read()
                st.download_button(
                    f"📥 {chosen_branch} Raporunu İndir (.docx)",
                    data=br_bytes,
                    file_name=f"8B_{tr_safe_sub}_Brans_Raporu.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key=f"btn_down_{tr_safe_sub}"
                )
        except Exception as _e_br:
            st.error(f"Rapor oluşturulurken hata: {_e_br}")

    with col_bsel3:
        # Tüm branşlar ZIP — her zaman taze üret
        all_br_zip = os.path.join(EXPORTS_DIR, "8B_Tum_Brans_Ogretmen_Raporlari.zip")
        try:
            generate_all_branch_reports(selected_exam_name, results, all_kaz_data, comps)
            if os.path.exists(all_br_zip):
                with open(all_br_zip, "rb") as f_zbr:
                    zbr_bytes = f_zbr.read()
                st.download_button(
                    "📦 6 Branş Raporunu İndir (ZIP)",
                    data=zbr_bytes,
                    file_name="8B_Tum_Brans_Ogretmen_Raporlari.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key=f"btn_down_all_branch_zip_{chosen_branch}"
                )
        except Exception as _e_zip:
            st.error(f"ZIP oluşturulurken hata: {_e_zip}")

    st.markdown("---")

    # ── 1. KPI Metrikleri ──────────────────────────────────────────────────
    diff_prefix = "+" if b_data['diff_from_school'] >= 0 else ""
    diff_label = f"{diff_prefix}{b_data['diff_from_school']:.2f} Okul Farkı"

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Sınıf Net Ort.", f"{b_data['mean_net']:.2f} / {b_data['questions']}", delta=diff_label)
    k2.metric("Medyan Net", f"{b_data['median_net']:.2f}", help="Tam ortadaki öğrencinin neti")
    k3.metric("Doğru %", f"%{b_data['d_pct']:.1f}", f"{b_data['total_d']} toplam")
    k4.metric("Yanlış %", f"%{b_data['y_pct']:.1f}", f"{b_data['total_y']} toplam")
    k5.metric("Boş %", f"%{b_data['b_pct']:.1f}", f"{b_data['total_b']} toplam")
    k6.metric("Zirve / Taban", f"{b_data['max_net']:.1f} / {b_data['min_net']:.1f}", help="En yüksek ve en düşük net")

    # ── Sınav Davranış Teşhisi ─────────────────────────────────────────────
    high_y_ui = [s for s in b_data['students'] if s['y'] >= b_data['questions'] * 0.35]
    high_b_ui = [s for s in b_data['students'] if s['b'] >= b_data['questions'] * 0.35]
    diag_c1, diag_c2 = st.columns(2)
    with diag_c1:
        if high_y_ui:
            st.error(
                f"🔴 **Negatif Net Riski ({len(high_y_ui)} Öğrenci):** "
                + ", ".join([f"{s['name'].title()} ({s['y']}Y)" for s in high_y_ui[:12]])
                + (" ..." if len(high_y_ui) > 12 else "")
            )
        else:
            st.success("✅ Aşırı yanlış yapan öğrenci tespit edilmedi.")
    with diag_c2:
        if high_b_ui:
            st.warning(
                f"🟡 **Süre / Çekinme Sorunu ({len(high_b_ui)} Öğrenci):** "
                + ", ".join([f"{s['name'].title()} ({s['b']}B)" for s in high_b_ui[:12]])
                + (" ..." if len(high_b_ui) > 12 else "")
            )
        else:
            st.success("✅ Aşırı boş bırakan öğrenci tespit edilmedi.")

    st.markdown("---")

    # ── 2. Kazanım Başarı Grafiği + Risk Tablosu ──────────────────────────
    col_chart, col_ktable = st.columns([2, 3])
    with col_chart:
        st.subheader(f"📊 {chosen_branch} Kazanım Başarı Oranları (%)")
        if b_data["kazanims"]:
            df_kz = pd.DataFrame(b_data["kazanims"])
            fig_kz, ax_kz = plt.subplots(figsize=(6, max(3, len(df_kz) * 0.45)))
            bar_colors = []
            for r in df_kz["avg_rate"]:
                if r < 40:
                    bar_colors.append("#E74C3C")
                elif r < 60:
                    bar_colors.append("#F39C12")
                elif r < 80:
                    bar_colors.append("#27AE60")
                else:
                    bar_colors.append("#117864")
            y_pos = np.arange(len(df_kz))
            ax_kz.barh(y_pos, df_kz["avg_rate"], color=bar_colors, height=0.6)
            ax_kz.set_yticks(y_pos)
            clean_labels = [k[:30] + ("..." if len(k) > 30 else "") for k in df_kz["kazanim"]]
            ax_kz.set_yticklabels(clean_labels, fontsize=7.5)
            ax_kz.set_xlim(0, 105)
            ax_kz.set_xlabel("Sınıf Başarı Oranı (%)")
            ax_kz.axvline(40, color="#E74C3C", linestyle="--", alpha=0.5, linewidth=0.8, label="%40 Acil")
            ax_kz.axvline(60, color="#F39C12", linestyle="--", alpha=0.5, linewidth=0.8, label="%60 Risk")
            ax_kz.legend(fontsize=7)
            ax_kz.grid(axis='x', linestyle='--', alpha=0.4)
            for i, v in enumerate(df_kz["avg_rate"]):
                ax_kz.text(v + 1.5, i, f"%{v:.1f}", va='center', fontsize=7, fontweight='bold', color='#333')
            plt.tight_layout()
            st.pyplot(fig_kz)
        else:
            st.info("Bu branşa ait kazanım verisi bulunmuyor.")

    with col_ktable:
        st.subheader("📋 Kazanım Risk Tablosu")
        if b_data["kazanims"]:
            df_ktable = pd.DataFrame([
                {
                    "Kazanım": k["kazanim"],
                    "Başarı %": f"%{k['avg_rate']:.1f}",
                    "Durum": k["level_code"],
                    "Kritik (<40%)": f"{k['crit_count']} Öğr.",
                    "Güçlü (≥75%)": f"{k['high_count']} Öğr.",
                }
                for k in b_data["kazanims"]
            ])
            st.dataframe(df_ktable, use_container_width=True, height=350)
            with st.expander("🔍 <%40 Başarılı Öğrencilerin İsim Listesi", expanded=False):
                crit_any = False
                for k in b_data["kazanims"]:
                    if k["crit_count"] > 0 and k["avg_rate"] < 65.0:
                        crit_any = True
                        st.markdown(
                            f"**🔴 {k['kazanim']} (%{k['avg_rate']:.1f}):** "
                            f"{', '.join(k['crit_students'])}"
                        )
                if not crit_any:
                    st.success("Kritik eşikte (<40%) desteğe muhtaç öğrenci yok.")

    st.markdown("---")

    # ── 3. Öğrenci Performans Listesi ─────────────────────────────────────
    st.subheader(f"👥 8/B {chosen_branch} Öğrenci Performans Listesi")
    df_st_branch = pd.DataFrame([
        {
            "Sıra": s["branch_rank"],
            "No": s["school_no"],
            "Öğrenci": s["name"],
            "Doğru": s["d"],
            "Yanlış": s["y"],
            "Boş": s["b"],
            "Net": f"{s['net']:.2f}",
            "Başarı %": f"%{s['succ_pct']:.1f}",
            "Durum": s["behavior_code"],
        }
        for s in b_data["students"]
    ])
    st.dataframe(df_st_branch, use_container_width=True, height=500)

# ----------------- TAB 4: Çoklu Deneme Gelişim Takibi -----------------
with tab4:
    st.subheader("📈 Çoklu Deneme Sınavı ve Zaman Serisi Gelişim Takibi")
    st.markdown("Yıl boyunca uygulanan tüm deneme sınavlarının karşılaştırmalı analizi, sınıf ve birey düzeyindeki net ve puan değişimleri burada izlenir.")

    try:
        from core.comparative_analyzer import get_multi_exam_comparison
        comp_data = get_multi_exam_comparison()
    except Exception as _e:
        comp_data = {}

    if comp_data:
        valid_comps = [c for c in comp_data.values() if c.get('has_both')]
        
        if valid_comps:
            # Sınıf Özet Metrikleri
            total_d_net = sum(c.get('delta_net', c.get('d_net', 0.0)) for c in valid_comps)
            avg_d_net = total_d_net / len(valid_comps)
            total_d_puan = sum(c.get('delta_puan', c.get('d_puan', 0.0)) for c in valid_comps)
            avg_d_puan = total_d_puan / len(valid_comps)
            improved_count = sum(1 for c in valid_comps if c.get('delta_net', c.get('d_net', 0.0)) > 0)
            
            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            c_m1.metric("Sınıf Net Değişimi (Ort.)", f"{avg_d_net:+.2f} Net", delta=f"{avg_d_net:+.2f}")
            c_m1.caption("Paraf 1 (37.43) ➔ NARTEST 1 (44.80)")
            c_m2.metric("Sınıf Puan Değişimi (Ort.)", f"{avg_d_puan:+.2f} Puan", delta=f"{avg_d_puan:+.2f}")
            c_m2.caption("Paraf 1 (304.00) ➔ NARTEST 1 (335.31)")
            c_m3.metric("Netini Artıran Öğrenci", f"{improved_count} / {len(valid_comps)}", f"%{improved_count/len(valid_comps)*100:.0f} Başarı")
            c_m3.caption("26 öğrencinin 20'si netini artırdı")
            c_m4.metric("Aktif Şube Mevcudu", f"{len(comp_data)} Öğrenci")
            c_m4.caption("28 Katılan, 2 Yeni, 1 Mazeretli")
            
            st.markdown("---")
            
            # En Çok Gelişim Gösteren İlk 5
            st.markdown("### 🚀 En Çok Gelişim Gösteren Öğrenciler (Top 5)")
            top_improvers = sorted(valid_comps, key=lambda x: x.get('delta_net', x.get('d_net', 0.0)), reverse=True)[:5]
            imp_cols = st.columns(5)
            for idx, imp in enumerate(top_improvers):
                with imp_cols[idx]:
                    val_net = imp.get('delta_net', imp.get('d_net', 0.0))
                    val_puan = imp.get('delta_puan', imp.get('d_puan', 0.0))
                    val_rank = imp.get('delta_cls_rank', imp.get('d_cls_rank', 0))
                    st.metric(
                        label=f"{idx+1}. {imp.get('name', '')}",
                        value=f"{val_net:+.2f} Net",
                        delta=f"{val_puan:+.1f} Puan ({val_rank:+d} Sıra)"
                    )
            
            st.markdown("---")
            
            # Ders Bazında Sınıf Net Değişimi
            st.markdown("### 📊 Ders Bazında Sınıf Net Ortalamaları Değişimi")
            sub_names = ["Türkçe", "Matematik", "Fen Bilimleri", "İnkılap Tarihi", "Din Kültürü", "İngilizce"]
            sub_p1_keys = ["tur_net", "mat_net", "fen_net", "ink_net", "din_net", "ing_net"]
            
            p1_means = [sum(c['r1'].get(k, 0.0) for c in valid_comps) / len(valid_comps) for k in sub_p1_keys]
            p2_means = [sum(c['r2'].get(k, 0.0) for c in valid_comps) / len(valid_comps) for k in sub_p1_keys]
            
            df_sub_comp = pd.DataFrame({
                "Branş": sub_names,
                "Paraf 1 (Ekim)": [round(x, 2) for x in p1_means],
                "NARTEST 1 (Kasım)": [round(x, 2) for x in p2_means],
                "Fark (Δ)": [round(b - a, 2) for a, b in zip(p1_means, p2_means)]
            })
            
            col_g1, col_g2 = st.columns([3, 2])
            with col_g1:
                fig_bar, ax_bar = plt.subplots(figsize=(7, 3.5))
                x_idx = np.arange(len(sub_names))
                width = 0.35
                ax_bar.bar(x_idx - width/2, df_sub_comp["Paraf 1 (Ekim)"], width, label="Paraf LGS 1", color="#5D6D7E")
                ax_bar.bar(x_idx + width/2, df_sub_comp["NARTEST 1 (Kasım)"], width, label="NARTEST LGS 1", color="#1F497D")
                ax_bar.set_xticks(x_idx)
                ax_bar.set_xticklabels(sub_names, rotation=15, ha='right')
                ax_bar.set_ylabel("Sınıf Ort. Net")
                ax_bar.legend()
                ax_bar.grid(axis='y', linestyle='--', alpha=0.5)
                st.pyplot(fig_bar)
            
            with col_g2:
                st.dataframe(df_sub_comp, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Tüm Öğrencilerin Gelişim Tablosu
            st.markdown("### 📋 Tüm Öğrencilerin Karşılaştırmalı Gelişim Tablosu")
            table_rows = []
            for c in sorted(comp_data.values(), key=lambda x: int(x.get('school_no') or 0)):
                if c.get('has_both'):
                    b_sub = c.get('best_sub')
                    w_sub = c.get('worst_sub')
                    table_rows.append({
                        "No": c.get('school_no', ''),
                        "Öğrenci": c.get('name', ''),
                        "Paraf Net": f"{c['r1']['top_net']:.2f}",
                        "NARTEST Net": f"{c['r2']['top_net']:.2f}",
                        "Δ Net": f"{c.get('delta_net', c.get('d_net', 0.0)):+.2f}",
                        "Paraf Puan": f"{c['r1']['puan']:.2f}",
                        "NARTEST Puan": f"{c['r2']['puan']:.2f}",
                        "Δ Puan": f"{c.get('delta_puan', c.get('d_puan', 0.0)):+.2f}",
                        "Paraf Sıra": c['r1']['class_rank'],
                        "NARTEST Sıra": c['r2']['class_rank'],
                        "Δ Sıra": f"{c.get('delta_cls_rank', c.get('d_cls_rank', 0)):+d}",
                        "En Çok Gelişen": f"{b_sub[0]} ({b_sub[1]:+.2f})" if b_sub else "-",
                        "Takviye Branş": f"{w_sub[0]} ({w_sub[1]:+.2f})" if w_sub else "-",
                        "Durum": f"{c.get('trend_icon', '')} {c.get('trend', 'Belirsiz')}"
                    })
                elif c.get('r2'):
                    table_rows.append({
                        "No": c.get('school_no', ''),
                        "Öğrenci": c.get('name', ''),
                        "Paraf Net": "-",
                        "NARTEST Net": f"{c['r2']['top_net']:.2f}",
                        "Δ Net": "Yeni Kayıt",
                        "Paraf Puan": "-",
                        "NARTEST Puan": f"{c['r2']['puan']:.2f}",
                        "Δ Puan": "Yeni Kayıt",
                        "Paraf Sıra": "-",
                        "NARTEST Sıra": c['r2']['class_rank'],
                        "Δ Sıra": "-",
                        "En Çok Gelişen": "-",
                        "Takviye Branş": "-",
                        "Durum": "🌱 Yeni Öğrenci"
                    })
                elif c.get('r1'):
                    table_rows.append({
                        "No": c.get('school_no', ''),
                        "Öğrenci": c.get('name', ''),
                        "Paraf Net": f"{c['r1']['top_net']:.2f}",
                        "NARTEST Net": "Giremedi",
                        "Δ Net": "Mazeretli",
                        "Paraf Puan": f"{c['r1']['puan']:.2f}",
                        "NARTEST Puan": "-",
                        "Δ Puan": "-",
                        "Paraf Sıra": c['r1']['class_rank'],
                        "NARTEST Sıra": "-",
                        "Δ Sıra": "-",
                        "En Çok Gelişen": "-",
                        "Takviye Branş": "-",
                        "Durum": "ℹ️ Mazeretli"
                    })
            df_all_comp = pd.DataFrame(table_rows)
            st.dataframe(df_all_comp, use_container_width=True, hide_index=True)
            
            st.markdown("---")

    # Bireysel Zaman Serisi Grafiği
    st.markdown("### 👤 Bireysel Öğrenci Zaman Serisi Grafiği")
    all_st_names = [r['name'] for r in results]
    sel_student_trend = st.selectbox("İncelemek istediğiniz öğrenciyi seçin:", all_st_names, key="sel_trend_student")
    st_hist = get_student_history(sel_student_trend)
    if len(st_hist) > 1:
        df_h = pd.DataFrame(st_hist)
        fig_h, ax_h = plt.subplots(figsize=(8, 3))
        ax_h.plot(df_h['exam_name'], df_h['top_net'], marker='o', linewidth=2, color='#1F497D', label='Toplam Net')
        for _, row_h in df_h.iterrows():
            ax_h.annotate(f"{row_h['top_net']:.2f} Net",
                          (row_h['exam_name'], row_h['top_net']),
                          textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')
        ax_h.set_ylabel("Net")
        ax_h.set_ylim(bottom=max(0, df_h['top_net'].min() - 5))
        ax_h.grid(True, linestyle='--', alpha=0.5)
        ax_h.legend()
        st.pyplot(fig_h)
    else:
        st.info(f"{sel_student_trend} adlı öğrencinin yalnızca 1 sınav kaydı var.")


# ----------------- TAB RISK: Sinif Risk Haritasi -----------------
with tab_risk:
    init_risk_table()
    st.subheader("🗺️ Sınıf Risk Haritası — S.İ.4.a")
    st.caption("Kaynaktan alindı: Özel Eğitim ve Rehberlik Hizmetleri Genel Müdurlugu")

    if current_role is None:
        st.warning("🔐 Bu bölümü görmek için giriş yapmanız gerekiyor. Sol panelden PIN kodunuzla giriş yapın.")
    elif current_role == "student":
        # ─── Öğrenci Tanıma Formu ─────────────────────────────────────────────────
        st.info("📋 Bu bolumde sana birkaç soru sorulacak. Yanıtların gizlidir ve yalnızca sınıf öğretmenin gorebilir.")


        # ─── Öğrenci Tanıma Formu ────────────────────────────────────────────────────
        from core.student_profile import (init_profile_table, save_profile, get_profile,
                                          profile_exists, profile_to_risk_factors)
        init_profile_table()

        stu_id_form = st.session_state.get("student_id")
        # Fallback: student_name üzerinden ID bul
        if not stu_id_form and st.session_state.get("student_name"):
            import sqlite3 as _sq_fb
            from config import DATABASE_PATH as _DB_FB
            _row_fb = _sq_fb.connect(_DB_FB).execute(
                "SELECT id FROM students WHERE name = ?",
                (st.session_state.student_name,)
            ).fetchone()
            if _row_fb:
                st.session_state.student_id = _row_fb[0]
                stu_id_form = _row_fb[0]
        if not stu_id_form:
            st.warning("⚠️ Oturum bilgisi eksik. Lütfen çıkış yapıp tekrar giriş yapın.")
        else:
            profile_done = profile_exists(stu_id_form)
            existing = get_profile(stu_id_form) if profile_done else {}

            if profile_done:
                st.success("✅ Öğrenci Tanıma Formunu doldurdunuz. Teşekkürler!")
                if st.button("📝 Bilgilerimi Güncelle", key="btn_edit_profile"):
                    st.session_state["edit_profile"] = True
                    st.rerun()

            if not profile_done or st.session_state.get("edit_profile", False):
                st.info("📋 Lütfen aşağıdaki formu eksiksiz ve doğru doldurun. Bilgileriniz yalnızca öğretmeniniz tarafından görülecektir.")

                with st.container():

                    # ── BÖLÜM 1: Öğrenci Bilgileri ──────────────────────────────────
                    st.markdown("### 👤 Bölüm 1 — Öğrenci Bilgileri")
                    b1c1, b1c2 = st.columns(2)
                    cinsiyet    = b1c1.radio("Cinsiyetiniz", ["Kız", "Erkek"], horizontal=True,
                                             index=0 if existing.get("cinsiyet") == "Kız" else 1 if existing.get("cinsiyet") == "Erkek" else 0)
                    cep_tel     = b1c2.text_input("Cep Telefonu Numaranız", value=existing.get("cep_telefon", ""),
                                                  placeholder="05XX XXX XX XX")
                    dogum_yeri  = b1c1.text_input("Doğum Yeriniz", value=existing.get("dogum_yeri", ""))
                    dogum_tarihi= b1c2.text_input("Doğum Tarihiniz (GG.AA.YYYY)", value=existing.get("dogum_tarihi", ""),
                                                  placeholder="01.01.2010")
                    okul_adi    = b1c1.text_input("Okulunuz", value=existing.get("okul_adi", ""))
                    adres       = b1c2.text_input("Adresiniz", value=existing.get("adres", ""))

                    st.markdown("---")
                    # ── BÖLÜM 2: Aile ve Ev Hayatı ──────────────────────────────────
                    st.markdown("### 🏠 Bölüm 2 — Aile ve Ev Hayatı")

                    kimler_opts = ["Annem ve babam", "Yalnızca annem", "Yalnızca babam",
                                   "Büyükanne / büyükbabam", "Diğer akrabalarım (hala, amca, dayı vb.)",
                                   "Abim / ablam / kardeşlerim", "Diğer"]
                    import json as _json
                    _ev_default = _json.loads(existing.get("evde_kimseler", "[]") or "[]") if existing else []
                    evde_kimseler = st.multiselect("2.1 Evde kimlerle yaşıyorsunuz? (Birden fazla seçebilirsiniz)",
                                                   kimler_opts, default=_ev_default)

                    st.markdown("**2.2 Anneniz hakkında:**")
                    b2a1, b2a2 = st.columns(2)
                    anne_adi    = b2a1.text_input("Annenizin Adı Soyadı", value=existing.get("anne_adi", ""))
                    anne_sag    = b2a2.radio("Anneniz sağ mı?", ["Evet", "Hayır"], horizontal=True,
                                             index=0 if existing.get("anne_sag", "Evet") == "Evet" else 1)
                    anne_egitim = b2a1.selectbox("Annenizin en son bitirdiği okul",
                                                 ["Okuryazar değil", "İlkokul", "Ortaokul", "Lise", "Üniversite"],
                                                 index=["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"].index(existing.get("anne_egitim","Ortaokul")) if existing.get("anne_egitim") in ["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"] else 2)
                    anne_meslek = b2a2.text_input("Annenizin Mesleği", value=existing.get("anne_meslek", ""),
                                                  placeholder="Çalışmıyor / Öğretmen / vb.")

                    st.markdown("**2.3 Babanız hakkında:**")
                    b2b1, b2b2 = st.columns(2)
                    baba_adi    = b2b1.text_input("Babanızın Adı Soyadı", value=existing.get("baba_adi", ""))
                    baba_sag    = b2b2.radio("Babanız sağ mı?", ["Evet", "Hayır"], horizontal=True,
                                             index=0 if existing.get("baba_sag", "Evet") == "Evet" else 1)
                    baba_egitim = b2b1.selectbox("Babanızın en son bitirdiği okul",
                                                 ["Okuryazar değil", "İlkokul", "Ortaokul", "Lise", "Üniversite"],
                                                 index=["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"].index(existing.get("baba_egitim","Ortaokul")) if existing.get("baba_egitim") in ["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"] else 2)
                    baba_meslek = b2b2.text_input("Babanızın Mesleği", value=existing.get("baba_meslek", ""),
                                                  placeholder="Çalışmıyor / Müteahhit / vb.")

                    ebeveyn_opts = ["Evet, birlikte yaşıyorlar", "Hayır, ayrı yaşıyorlar"]
                    ebeveyn_birlikte = st.radio("2.4 Anne ve babanız birlikte mi yaşıyor?",
                                                ebeveyn_opts, horizontal=True,
                                                index=0 if existing.get("ebeveyn_birlikte","Evet, birlikte yaşıyorlar") == "Evet, birlikte yaşıyorlar" else 1)

                    mevsimlik_opts = ["Hayır", "Evet", "Bazen"]
                    mevsimlik_isci = st.radio("2.5 Aile olarak son 1 yılda mevsimlik/geçici bir işte başka şehirlere gittiniz mi?",
                                              mevsimlik_opts, horizontal=True,
                                              index=mevsimlik_opts.index(existing.get("mevsimlik_isci","Hayır")) if existing.get("mevsimlik_isci") in mevsimlik_opts else 0)

                    st.markdown("---")
                    # ── BÖLÜM 3: Kardeşler ──────────────────────────────────────────
                    st.markdown("### 👨‍👩‍👧‍👦 Bölüm 3 — Kardeşler")
                    b3c1, b3c2, b3c3 = st.columns(3)
                    kardes_sayisi       = b3c1.number_input("Kaç kardeşiniz var?", min_value=0, max_value=20,
                                                            value=int(existing.get("kardes_sayisi") or 0))
                    kacinci_cocuk       = b3c2.number_input("Ailenizin kaçıncı çocuğusunuz?", min_value=1, max_value=20,
                                                            value=int(existing.get("kacinci_cocuk") or 1))
                    okula_giden_kardes  = b3c3.number_input("Okula giden kardeş sayınız", min_value=0, max_value=20,
                                                            value=int(existing.get("okula_giden_kardes") or 0))

                    st.markdown("---")
                    # ── BÖLÜM 4: Sağlık ─────────────────────────────────────────────
                    st.markdown("### 🏥 Bölüm 4 — Sağlık Bilgileri")
                    _ilac_c1, _ilac_c2 = st.columns([1, 2])
                    ilac_kullaniyor = _ilac_c1.radio("4.1 Sürekli kullandığınız bir ilaç veya tıbbi cihazınız var mı?",
                                                    ["Hayır", "Evet"], horizontal=True,
                                                    index=0 if existing.get("ilac_kullaniyor","Hayır") == "Hayır" else 1)
                    ilac_adi = _ilac_c2.text_input("İlaç / cihaz adı",
                                                   value=existing.get("ilac_adi","") if ilac_kullaniyor == "Evet" else "",
                                                   disabled=(ilac_kullaniyor != "Evet"),
                                                   placeholder="İlaç veya cihaz adını yazınız..." if ilac_kullaniyor == "Evet" else "('Evet' seçilince aktif olur)")

                    _tani_c1, _tani_c2 = st.columns([1, 2])
                    tani_var = _tani_c1.radio("4.2 Tanısı konulmuş bir hastalığınız ya da engel durumunuz var mı?",
                                             ["Hayır", "Evet"], horizontal=True,
                                             index=0 if existing.get("tani_var","Hayır") == "Hayır" else 1)
                    tani_aciklama = _tani_c2.text_input("Tanısı nedir?",
                                                        value=existing.get("tani_aciklama","") if tani_var == "Evet" else "",
                                                        disabled=(tani_var != "Evet"),
                                                        placeholder="Örn: DEHB, Astım, Görme engeli..." if tani_var == "Evet" else "('Evet' seçilince aktif olur)")

                    ozel_egitim_opts = ["Hayır", "Evet, özel eğitim alıyorum",
                                        "Evet, kaynaştırma öğrencisiyim", "Evet, destek eğitimi alıyorum"]
                    ozel_egitim = st.radio("4.3 Özel eğitim, kaynaştırma veya destek eğitimi alıyor musunuz?",
                                           ozel_egitim_opts,
                                           index=ozel_egitim_opts.index(existing.get("ozel_egitim","Hayır")) if existing.get("ozel_egitim") in ozel_egitim_opts else 0)

                    _aile_c1, _aile_c2 = st.columns([1, 2])
                    ailede_hastalik = _aile_c1.radio("4.4 Ailenizde uzun süreli bir hastalığı ya da engel durumu olan biri var mı?",
                                                     ["Hayır", "Evet"], horizontal=True,
                                                     index=0 if existing.get("ailede_hastalik","Hayır") == "Hayır" else 1)
                    ailede_aciklama = _aile_c2.text_input("Kim, ne hastalığı?",
                                                          value=existing.get("ailede_aciklama","") if ailede_hastalik == "Evet" else "",
                                                          disabled=(ailede_hastalik != "Evet"),
                                                          placeholder="Örn: Annem - şeker hastalığı / Babam - kalp..." if ailede_hastalik == "Evet" else "('Evet' seçilince aktif olur)")

                    st.markdown("---")
                    # ── BÖLÜM 5: Okul Hayatı ────────────────────────────────────────
                    st.markdown("### 🏫 Bölüm 5 — Okul Hayatı")
                    devamsizlik_opts = ["Hiç gitmedim (0 gün)", "1–3 gün", "4–9 gün", "10 gün ve üzeri"]
                    devamsizlik_gun  = st.radio("5.1 Bu dönem yaklaşık kaç gün okula gidemediniz?",
                                                devamsizlik_opts,
                                                index=devamsizlik_opts.index(existing.get("devamsizlik_gun","Hiç gitmedim (0 gün)")) if existing.get("devamsizlik_gun") in devamsizlik_opts else 0)

                    zorluk_opts = ["Hayır, genellikle takip edebiliyorum",
                                   "Bazı derslerde zorlanıyorum",
                                   "Evet, çoğu derste ciddi zorluk çekiyorum"]
                    ders_zorluk = st.radio("5.2 Dersleri takip etmekte zorlanıyor musunuz?",
                                           zorluk_opts,
                                           index=zorluk_opts.index(existing.get("ders_zorluk","Hayır, genellikle takip edebiliyorum")) if existing.get("ders_zorluk") in zorluk_opts else 0)

                    ders_opts = ["Türkçe","Matematik","Fen Bilimleri","İngilizce",
                                 "Sosyal Bilgiler / İnkılap Tarihi","Din Kültürü"]
                    _zor_default = _json.loads(existing.get("zor_dersler","[]") or "[]") if existing else []
                    zor_dersler  = st.multiselect("5.3 Hangi dersler en zor geliyor? (Birden fazla seçebilirsiniz)",
                                                  ders_opts, default=_zor_default)

                    degistirdi_opts = ["Hayır, bu okulda sürekliyim",
                                       "Evet, bu yıl okul değiştirdim",
                                       "Evet, geçen yıl değiştirdim"]
                    okul_degistirdi = st.radio("5.4 Okula yakın zamanda yeni mi başladınız ya da okul değiştirdiniz mi?",
                                               degistirdi_opts,
                                               index=degistirdi_opts.index(existing.get("okul_degistirdi","Hayır, bu okulda sürekliyim")) if existing.get("okul_degistirdi") in degistirdi_opts else 0)

                    arkadas_opts = ["Kolaylıkla arkadaş edinebiliyorum",
                                    "Bazen zorluk çekiyorum",
                                    "Genellikle yalnız kalıyorum"]
                    arkadas_edinme = st.radio("5.5 Okulda arkadaş edinmekte nasıl buluyorsunuz kendinizi?",
                                              arkadas_opts,
                                              index=arkadas_opts.index(existing.get("arkadas_edinme","Kolaylıkla arkadaş edinebiliyorum")) if existing.get("arkadas_edinme") in arkadas_opts else 0)

                    st.markdown("---")
                    # ── BÖLÜM 6: Günlük Hayat ───────────────────────────────────────
                    st.markdown("### 🌇 Bölüm 6 — Günlük Hayat")
                    calisma_opts = ["Hayır", "Evet, hafta sonları yardım ediyorum",
                                    "Evet, hafta içi düzenli çalışıyorum"]
                    calisma_durumu = st.radio("6.1 Okul dışında bir işte ya da tezgâhta çalışıyor musunuz?",
                                              calisma_opts,
                                              index=calisma_opts.index(existing.get("calisma_durumu","Hayır")) if existing.get("calisma_durumu") in calisma_opts else 0)

                    ortam_opts = ["Evet, rahat bir çalışma yerim var",
                                  "Bazen olmuyor",
                                  "Hayır, genellikle çalışacak ortam bulamıyorum"]
                    ders_ortami = st.radio("6.2 Ders çalışmak için evde sessiz bir ortamınız var mı?",
                                           ortam_opts,
                                           index=ortam_opts.index(existing.get("ders_ortami","Evet, rahat bir çalışma yerim var")) if existing.get("ders_ortami") in ortam_opts else 0)

                    internet_opts = ["Evet, evde var", "Yalnızca telefonum var",
                                     "Hayır, çoğu zaman erişemiyorum"]
                    internet_erisim = st.radio("6.3 İnternete ve bilgisayara erişiminiz var mı?",
                                               internet_opts,
                                               index=internet_opts.index(existing.get("internet_erisim","Evet, evde var")) if existing.get("internet_erisim") in internet_opts else 0)

                    tekno_opts = ["Tablet / Bilgisayar", "Akıllı telefon", "Akıllı saat / tablet", "Hiçbiri"]
                    _tekno_default = _json_form.loads(existing.get("teknoloji_aleti","[]") or "[]") if existing and isinstance(existing.get("teknoloji_aleti",""), str) and existing.get("teknoloji_aleti","").startswith("[") else ([existing.get("teknoloji_aleti")] if existing.get("teknoloji_aleti") and existing.get("teknoloji_aleti") in tekno_opts else [])
                    teknoloji_aleti = st.multiselect("6.4 Kendinize ait teknolojik aletleriniz neler? (Birden fazla seçebilirsiniz)",
                                                     tekno_opts, default=_tekno_default)

                    st.markdown("---")
                    # ── BÖLÜM 7: İlgi ve Hobiler ───────────────────────────────────
                    st.markdown("### 🎨 Bölüm 7 — İlgi ve Hobiler")
                    hobi_opts = ["Spor / Hareket", "Müzik / Sanat / Resim",
                                 "Kitap okumak", "Teknoloji / Oyun", "Doğa / Gezi", "Diğer"]
                    _hobi_default = _json.loads(existing.get("hobiler","[]") or "[]") if existing else []
                    hobiler = st.multiselect("7.1 Ne yapmaktan hoşlanırsınız? (Birden fazla seçebilirsiniz)",
                                             hobi_opts, default=_hobi_default)

                    _kurs_c1, _kurs_c2 = st.columns([1, 2])
                    kurs_kulup = _kurs_c1.radio("7.2 Okul dışında katıldığınız bir spor, sanat veya hobi kulübü var mı?",
                                                ["Hayır", "Evet"], horizontal=True,
                                                index=0 if existing.get("kurs_kulup","Hayır") == "Hayır" else 1)
                    kurs_brans = _kurs_c2.text_input("Hangi branş(lar)? (Birden fazlaysa araya tire '-' koyun)",
                                                     value=existing.get("kurs_brans","") if kurs_kulup == "Evet" else "",
                                                     disabled=(kurs_kulup != "Evet"),
                                                     placeholder="Örn: Yüzme - Basketbol (Tire ile ayırınız)" if kurs_kulup == "Evet" else "('Evet' seçilince aktif olur)")
                    kurs_adi = kurs_brans

                    akademik_destek_opts = ["Hayır, almıyorum", "Okul kursu (ücretsiz)", "Dershane / Etüt merkezi",
                                            "Özel ders (bireysel)", "Online kurs / platform (Eba, YouTube vb.)"]
                    _akad_default = _json_form.loads(existing.get("akademik_destek","[]") or "[]") if existing and isinstance(existing.get("akademik_destek",""), str) and existing.get("akademik_destek","").startswith("[") else ([existing.get("akademik_destek")] if existing.get("akademik_destek") and existing.get("akademik_destek") in akademik_destek_opts else [])
                    akademik_destek = st.multiselect(
                        "7.3 Okul dışında akademik destek alıyor musunuz? (Birden fazla seçebilirsiniz)",
                        akademik_destek_opts, default=_akad_default)

                    st.markdown("---")
                    # ── BÖLÜM 8: Kendini Anlat ─────────────────────────────────────
                    st.markdown("### 💬 Bölüm 8 — Kendini Anlat")
                    his_opts = ["😊 İyi, mutluyum", "😐 Fena değil, idare ediyorum",
                                "😟 Son zamanlarda biraz zorlanıyorum",
                                "😔 Çok zorlanıyorum, destek istiyorum"]
                    genel_his = st.radio("8.1 Kendinizi genel olarak nasıl hissediyorsunuz? (Okul hayatı açısından)",
                                         his_opts,
                                         index=his_opts.index(existing.get("genel_his","😊 İyi, mutluyum")) if existing.get("genel_his") in his_opts else 0)

                    zorlastiran_sey = st.text_area("8.2 Okul hayatında sizi en çok zorlaştıran şey nedir? (İsteğe bağlı)",
                                                   value=existing.get("zorlastiran_sey",""),
                                                   placeholder="Örn: ulaşım, ders çalışma ortamı, sosyal ilişkiler...")

                    destek_opts = ["Hayır, şu an gerek duymuyorum",
                                   "Evet, ders konularında destek istiyorum",
                                   "Evet, kişisel bir şeyi paylaşmak istiyorum"]
                    destek_istek = st.radio("8.3 Öğretmenlerinizden ya da okul rehberinden özel destek almak ister misiniz?",
                                            destek_opts,
                                            index=destek_opts.index(existing.get("destek_istek","Hayır, şu an gerek duymuyorum")) if existing.get("destek_istek") in destek_opts else 0)

                    onemli_olay = st.radio("8.4 Hala etkisi altında olduğunuz önemli bir olay ya da değişiklik yaşadınız mı?",
                                           ["Hayır", "Evet (detay vermek zorunda değilsiniz)"],
                                           horizontal=True,
                                           index=0 if existing.get("onemli_olay","Hayır") == "Hayır" else 1)

                    st.markdown("---")
                    # ── BÖLÜM 9: Veli Bilgileri ────────────────────────────────────
                    st.markdown("### 👨‍👩‍👧 Bölüm 9 — Veli Bilgileri")
                    st.caption("Bu bölümü mümkünse veliye doldurun ya da sonradan güncelleyin.")
                    b9c1, b9c2 = st.columns(2)
                    veli_adi       = b9c1.text_input("Veli Adı Soyadı", value=existing.get("veli_adi",""))
                    veli_yakin_opts = ["Anne", "Baba", "Büyükanne / Büyükbaba", "Diğer"]
                    veli_yakinligi = b9c2.selectbox("Yakınlığı",
                                                    veli_yakin_opts,
                                                    index=veli_yakin_opts.index(existing.get("veli_yakinligi","Anne")) if existing.get("veli_yakinligi") in veli_yakin_opts else 0)
                    veli_telefon   = b9c1.text_input("Telefon Numarası", value=existing.get("veli_telefon",""),
                                                     placeholder="05XX XXX XX XX")
                    veli_egitim_opts = ["Okuryazar değil","İlkokul","Ortaokul","Lise","Üniversite"]
                    veli_egitim    = b9c2.selectbox("Eğitim Durumu", veli_egitim_opts,
                                                    index=veli_egitim_opts.index(existing.get("veli_egitim","Ortaokul")) if existing.get("veli_egitim") in veli_egitim_opts else 2)
                    veli_meslek    = b9c1.text_input("Mesleği", value=existing.get("veli_meslek",""))

                    st.markdown("---")
                    submitted_profile = st.button("✅ Formu Kaydet", use_container_width=True, type="primary", key="btn_submit_prof_tab")

                if submitted_profile:
                    profile_data = {
                        "cinsiyet": cinsiyet, "dogum_yeri": dogum_yeri,
                        "dogum_tarihi": dogum_tarihi, "okul_adi": okul_adi,
                        "adres": adres, "cep_telefon": cep_tel,
                        "evde_kimseler": evde_kimseler,
                        "anne_adi": anne_adi, "anne_sag": anne_sag,
                        "anne_egitim": anne_egitim, "anne_meslek": anne_meslek,
                        "baba_adi": baba_adi, "baba_sag": baba_sag,
                        "baba_egitim": baba_egitim, "baba_meslek": baba_meslek,
                        "ebeveyn_birlikte": ebeveyn_birlikte,
                        "mevsimlik_isci": mevsimlik_isci,
                        "kardes_sayisi": kardes_sayisi, "kacinci_cocuk": kacinci_cocuk,
                        "okula_giden_kardes": okula_giden_kardes,
                        "ilac_kullaniyor": ilac_kullaniyor, "ilac_adi": ilac_adi,
                        "tani_var": tani_var, "tani_aciklama": tani_aciklama,
                        "ozel_egitim": ozel_egitim, "ailede_hastalik": ailede_hastalik, "ailede_aciklama": ailede_aciklama,
                        "devamsizlik_gun": devamsizlik_gun, "ders_zorluk": ders_zorluk,
                        "zor_dersler": zor_dersler, "okul_degistirdi": okul_degistirdi,
                        "arkadas_edinme": arkadas_edinme,
                        "calisma_durumu": calisma_durumu, "ders_ortami": ders_ortami,
                        "internet_erisim": internet_erisim, "teknoloji_aleti": _json_form.dumps(teknoloji_aleti, ensure_ascii=False),
                        "kurs_kulup": kurs_kulup, "kurs_adi": kurs_adi,
                        "kurs_brans": kurs_brans,
                        "akademik_destek": _json_form.dumps(akademik_destek, ensure_ascii=False),
                        "genel_his": genel_his, "zorlastiran_sey": zorlastiran_sey,
                        "destek_istek": destek_istek, "onemli_olay": onemli_olay,
                        "veli_adi": veli_adi, "veli_yakinligi": veli_yakinligi,
                        "veli_telefon": veli_telefon, "veli_egitim": veli_egitim,
                        "veli_meslek": veli_meslek,
                    }
                    save_profile(stu_id_form, profile_data)
                    profile_to_risk_factors(stu_id_form, profile_data)
                    st.session_state["edit_profile"] = False
                    st.success("✅ Bilgileriniz başarıyla kaydedildi!")
                    st.balloons()
                    st.rerun()


    elif current_role in ("admin", "teacher"):
        # ─── Öğretmen / Admin Risk Haritası Paneli ─────────────────────────────────
        import sqlite3 as _sq
        from config import DATABASE_PATH as _DBP

        _conn_r = _sq.connect(_DBP)
        _students_r = _conn_r.execute(
            "SELECT id, school_no, name FROM students ORDER BY CAST(school_no AS INTEGER) ASC, id ASC"
        ).fetchall()
        _conn_r.close()

        all_risk = get_all_risk_data()

        # --- Özet Metrik Kutuları ---
        total_students = len(_students_r)
        total_at_risk = sum(1 for s in _students_r if all_risk.get(s[0]))
        risk_summary = get_risk_summary()

        rm1, rm2, rm3 = st.columns(3)
        rm1.metric("📌 Toplam Öğrenci", total_students)
        rm2.metric("⚠️ Risk Faktoru Olan", total_at_risk,
                   help="En az 1 risk faktörü işaretlenmiş öğrenci sayısı")
        top_factor = max(risk_summary, key=risk_summary.get) if risk_summary else None
        rm3.metric("🔥 En Yaygın Faktör",
                   FACTOR_DICT[top_factor]["label"][:30] + "..." if top_factor else "—",
                   f"{risk_summary.get(top_factor, 0)} öğrenci" if top_factor else "")

        st.markdown("---")

        # --- Risk Faktoru Giris Ekrani ---
        tab_grid, tab_summary, tab_export, tab_profiles = st.tabs([
            "📝 Risk Faktörü Girişi",
            "📊 Özet & Analiz",
            "📥 Resmi PDF İndir",
            "📋 Öğrenci Profilleri"
        ])

        with tab_grid:
            st.markdown("**Öğrenci seçin ve risk faktörlerini işaretleyin:**")

            # Öğrenci seçimi
            student_names_r = [f"{s[1]} — {s[2]}" for s in _students_r]
            sel_student_risk = st.selectbox("Öğrenci Seç", student_names_r, key="risk_stu_sel")
            sel_idx_r = student_names_r.index(sel_student_risk)
            sel_stu_id_r = _students_r[sel_idx_r][0]
            sel_stu_name_r = _students_r[sel_idx_r][2]

            cur_factors = get_student_risk_factors(sel_stu_id_r)

            st.markdown(f"**{sel_stu_name_r}** — Mevcut risk faktörleri: {len(cur_factors)}")

            # Kategori gruplarına gore göster
            categories = {}
            for f in RISK_FACTORS:
                categories.setdefault(f["category"], []).append(f)

            cat_icons = {
                "Aile Yapısı":    "🏠",
                "Özel Durum":     "🚨",
                "Aile Sağlığı":   "❤️",
                "Öğrenci Durumu": "🎓",
            }

            updated_factors = set(cur_factors)

            with st.form(f"risk_form_{sel_stu_id_r}"):
                for cat, factors in categories.items():
                    icon = cat_icons.get(cat, "•")
                    st.markdown(f"**{icon} {cat}**")
                    cols_f = st.columns(2)
                    for i, f in enumerate(factors):
                        default_val = f["id"] in cur_factors
                        label = f["label"]
                        if f["teacher_only"]:
                            label += " 🔒"
                        checked = cols_f[i % 2].checkbox(label, value=default_val, key=f"rf_{sel_stu_id_r}_{f['id']}")
                        if checked:
                            updated_factors.add(f["id"])
                        else:
                            updated_factors.discard(f["id"])

                note_r = st.text_area("Not (isteğe bağlı)", placeholder="Bu öğrenci için ek açıklama...")
                save_btn = st.form_submit_button("💾 Risk Faktörlerini Kaydet", use_container_width=True, type="primary")

                if save_btn:
                    # Tum mevcut faktorleri sil ve yeniden kaydet
                    import sqlite3 as _sq2
                    conn_save = _sq2.connect(_DBP)
                    conn_save.execute("DELETE FROM student_risk_factors WHERE student_id = ?", (sel_stu_id_r,))
                    conn_save.commit()
                    conn_save.close()
                    for fid in updated_factors:
                        set_risk_factor(sel_stu_id_r, fid, True, source="teacher", note=note_r if note_r else "")
                    st.success(f"✅ {sel_stu_name_r} için {len(updated_factors)} risk faktörü kaydedildi!")
                    st.rerun()

        with tab_summary:
            st.markdown("### 📊 Sınıf Risk Özet Tablosu")

            if not risk_summary:
                st.info("Henüz hiç risk faktörü girilmemiş. Risk Faktörü Girişi sekmesinden başlayın.")
            else:
                # En yaygın faktörler grafiği
                top_factors = sorted(risk_summary.items(), key=lambda x: x[1], reverse=True)[:15]
                labels_g = [FACTOR_DICT[fid]["label"][:35] for fid, _ in top_factors]
                counts_g = [cnt for _, cnt in top_factors]

                fig_r, ax_r = plt.subplots(figsize=(10, 5))
                bars = ax_r.barh(labels_g[::-1], counts_g[::-1], color="#C00000")
                ax_r.set_xlabel("Öğrenci Sayısı")
                ax_r.set_title("En Yaygın 15 Risk Faktörü")
                for bar, cnt in zip(bars, counts_g[::-1]):
                    ax_r.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                              str(cnt), va="center", fontsize=9)
                plt.tight_layout()
                st.pyplot(fig_r)
                plt.close(fig_r)

            # Öğrenci bazlı risk tablosu
            st.markdown("### 👥 Öğrenci Bazlı Risk Durumu")
            risk_rows = []
            for sid, sno, sname in _students_r:
                fids = all_risk.get(sid, set())
                risk_rows.append({
                    "Okul No": sno,
                    "Adı Soyadı": sname,
                    "Risk Sayısı": len(fids),
                    "Risk Faktörleri": ", ".join(FACTOR_DICT[fid]["label"] for fid in sorted(fids)) if fids else "—"
                })
            df_risk = pd.DataFrame(risk_rows)
            df_risk_sorted = df_risk.sort_values("Risk Sayısı", ascending=False)
            st.dataframe(df_risk_sorted, use_container_width=True, height=500)


        with tab_export:
            st.markdown("### 📄 Resmi Risk Haritası — Tek Sayfa Çıktı")

            ex1, ex2 = st.columns(2)
            school_inp = ex1.text_input("Okul Adı", value="", key="risk_school_inp")
            class_inp  = ex2.text_input("Sınıf Adı", value="8/B", key="risk_class_inp")

            students_list = [{"id": s[0], "school_no": s[1], "name": s[2]} for s in _students_r]

            col_dl1, col_dl2, col_dl3 = st.columns(3)

            # ── Excel İndir ───────────────────────────────────────────────────
            with col_dl1:
                st.markdown("#### 📊 Resmi Excel Tablosu (.xlsx)")
                st.caption("MEB S.İ.4.a şablonu, dikey başlıklar, 'X' işaretleri")
                if st.button("⚙️ Excel Dosyasını Oluştur", key="btn_risk_excel", use_container_width=True, type="primary"):
                    try:
                        from core.risk_pdf_exporter import export_risk_excel
                        risk_excel_out = os.path.join(EXPORTS_DIR, "8B_Sinif_Risk_Haritasi.xlsx")
                        os.makedirs(EXPORTS_DIR, exist_ok=True)
                        export_risk_excel(
                            students=students_list,
                            risk_data=all_risk,
                            output_path=risk_excel_out,
                            school_name=school_inp or "……",
                            class_name=class_inp or "8/B"
                        )
                        st.session_state["risk_excel_path"] = risk_excel_out
                        st.success("✅ Excel dosyası hazır!")
                    except Exception as e_rx:
                        st.error(f"Hata: {e_rx}")

                risk_excel_path = st.session_state.get("risk_excel_path",
                                  os.path.join(EXPORTS_DIR, "8B_Sinif_Risk_Haritasi.xlsx"))
                if os.path.exists(risk_excel_path):
                    with open(risk_excel_path, "rb") as f_re:
                        re_bytes = f_re.read()
                    st.download_button(
                        "📥 Risk Haritasını İndir (.xlsx)",
                        data=re_bytes,
                        file_name="8B_Sinif_Risk_Haritasi.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="btn_dl_risk_excel"
                    )

            # ── Word İndir ────────────────────────────────────────────────────
            with col_dl2:
                st.markdown("#### 📝 Word Belgesi (.docx)")
                st.caption("Yatay A4, tek sayfa, renkli kategoriler, ✓ işaretleri")
                if st.button("⚙️ Word Dosyasını Oluştur", key="btn_risk_word", use_container_width=True, type="secondary"):
                    try:
                        from core.risk_pdf_exporter import export_risk_pdf
                        risk_out = os.path.join(EXPORTS_DIR, "8B_Sinif_Risk_Haritasi.docx")
                        os.makedirs(EXPORTS_DIR, exist_ok=True)
                        export_risk_pdf(
                            students=students_list,
                            risk_data=all_risk,
                            output_path=risk_out,
                            school_name=school_inp or "……",
                            class_name=class_inp or "8/B"
                        )
                        st.session_state["risk_doc_path"] = risk_out
                        st.success("✅ Word dosyası hazır!")
                    except Exception as e_rp:
                        st.error(f"Hata: {e_rp}")

                risk_doc_path = st.session_state.get("risk_doc_path",
                                os.path.join(EXPORTS_DIR, "8B_Sinif_Risk_Haritasi.docx"))
                if os.path.exists(risk_doc_path):
                    with open(risk_doc_path, "rb") as f_rd:
                        rd_bytes = f_rd.read()
                    st.download_button(
                        "📥 Risk Haritasını İndir (.docx)",
                        data=rd_bytes,
                        file_name="8B_Sinif_Risk_Haritasi.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="btn_dl_risk_word"
                    )

            # ── Tarayıcıda Yazdır ─────────────────────────────────────────────
            with col_dl3:
                st.markdown("#### 🖨️ Tarayıcıda Yazdır / PDF")
                st.caption("Önizleme → Ctrl+P → 'Yatay' seçin → PDF olarak kaydedin")
                if st.button("🔍 Yazdır Önizlemesini Aç", key="btn_risk_html", use_container_width=True, type="secondary"):
                    st.session_state["show_risk_html"] = True

            if st.session_state.get("show_risk_html", False):
                from core.risk_pdf_exporter import build_risk_html
                html_content = build_risk_html(
                    students=students_list,
                    risk_data=all_risk,
                    school_name=school_inp or "……",
                    class_name=class_inp or "8/B"
                )

                st.markdown("---")
                st.markdown("""
> 💡 **Nasıl PDF'e çevirirsiniz?**
> Aşağıdaki HTML çıktısı açıldıktan sonra:
> **Ctrl+P** → Yazıcı: **PDF olarak kaydet** → Sayfa yönü: **Yatay** → Kenar boşlukları: **Minimum** → Yazdır
""")

                # HTML içeriğini HTML dosyasına indir
                import io as _io_r
                html_bytes = html_content.encode("utf-8")
                st.download_button(
                    "📥 HTML Dosyasını İndir (Tarayıcıda Aç → Ctrl+P)",
                    data=html_bytes,
                    file_name="8B_Risk_Haritasi_Yazdir.html",
                    mime="text/html",
                    use_container_width=True,
                    key="btn_dl_risk_html"
                )

                # Streamlit içinde önizleme
                st.markdown("#### 👁️ Önizleme (yakınlaştırmak için sağ tıklayın)")
                st.components.v1.html(html_content, height=520, scrolling=True)

                if st.button("❌ Önizlemeyi Kapat", key="btn_close_html"):
                    st.session_state["show_risk_html"] = False
                    st.rerun()


        with tab_profiles:
            st.markdown("### 📋 Öğrenci Tanıma Formu Verileri")
            from core.student_profile import get_all_profiles, profile_exists, get_profile
            import json as _pjson

            all_profiles = get_all_profiles()
            filled_count = len(all_profiles)
            st.info(f"📊 **{filled_count} / {total_students}** öğrenci formunu doldurdu.")

            if not all_profiles:
                st.warning("Henüz hiçbir öğrenci formu doldurmadı. Öğrenciler PIN ile girip 🗺️ Risk Haritası sekmesinden doldurabilir.")
            else:
                # Özet tablo
                summary_rows = []
                for p in all_profiles:
                    akad_str = ", ".join(_pjson.loads(p.get("akademik_destek","[]") or "[]")) if p.get("akademik_destek") else "-"
                    tek_raw = p.get("teknoloji_aleti", "")
                    tek_str = ", ".join(_pjson.loads(tek_raw or "[]")) if tek_raw.startswith("[") else (tek_raw or "-")
                    summary_rows.append({
                        "Okul No":          p.get("school_no", ""),
                        "Adı Soyadı":       p.get("name", ""),
                        "Cinsiyet":         p.get("cinsiyet", ""),
                        "Cep Tel":          p.get("cep_telefon", ""),
                        "İlaç / Cihaz":     p.get("ilac_adi") if p.get("ilac_kullaniyor") == "Evet" else ("Evet" if p.get("ilac_kullaniyor") == "Evet" else "-"),
                        "Tanı / Engel":     p.get("tani_aciklama") if p.get("tani_var") == "Evet" else ("Evet" if p.get("tani_var") == "Evet" else "-"),
                        "Ailede Hastalık":  p.get("ailede_aciklama") if p.get("ailede_hastalik") == "Evet" else ("Evet" if p.get("ailede_hastalik") == "Evet" else "-"),
                        "Kulüp / Branş":    p.get("kurs_brans") or (p.get("kurs_adi") if p.get("kurs_kulup") == "Evet" else "-"),
                        "Akademik Destek":  akad_str,
                        "Teknoloji":        tek_str,
                        "Devamsızlık":      p.get("devamsizlik_gun", ""),
                        "Ders Zorluk":      p.get("ders_zorluk", ""),
                        "Genel His":        p.get("genel_his", ""),
                        "Destek İstek":     p.get("destek_istek", ""),
                    })
                df_profiles = pd.DataFrame(summary_rows)
                st.dataframe(df_profiles, use_container_width=True, height=420)

                # Destek isteyen öğrenciler
                destek_list = [p for p in all_profiles
                               if p.get("destek_istek","") in
                               ("Evet, ders konularında destek istiyorum",
                                "Evet, kişisel bir şeyi paylaşmak istiyorum")]
                if destek_list:
                    st.markdown("#### 🚨 Destek İsteyen Öğrenciler")
                    for p in destek_list:
                        st.warning(f"**{p.get('name','')}** — {p.get('destek_istek','')}"
                                   + (f" | Not: _{p.get('zorlastiran_sey','')}_"
                                      if p.get('zorlastiran_sey') else ""))

                # Öğrenci detay görüntüle
                st.markdown("---")
                st.markdown("#### 🔍 Öğrenci Detay Görüntüle")
                profile_names = [f"{p.get('school_no','')} — {p.get('name','')}" for p in all_profiles]
                sel_prof = st.selectbox("Öğrenci Seç", profile_names, key="profile_detail_sel")
                sel_prof_data = all_profiles[profile_names.index(sel_prof)]

                with st.expander("📄 Tam Form Verileri", expanded=True):
                    dc1, dc2 = st.columns(2)
                    dc1.markdown(f"""
**👤 Öğrenci Bilgileri**
- Cinsiyet: {sel_prof_data.get('cinsiyet','-')}
- Doğum Yeri: {sel_prof_data.get('dogum_yeri','-')}
- Doğum Tarihi: {sel_prof_data.get('dogum_tarihi','-')}
- Adres: {sel_prof_data.get('adres','-')}
- Cep Telefonu: {sel_prof_data.get('cep_telefon','-')}

**🏠 Aile Yapısı**
- Evde kimseler: {', '.join(_pjson.loads(sel_prof_data.get('evde_kimseler','[]') or '[]'))}
- Anne: {sel_prof_data.get('anne_adi','-')} | Sağ: {sel_prof_data.get('anne_sag','-')} | Eğitim: {sel_prof_data.get('anne_egitim','-')} | Meslek: {sel_prof_data.get('anne_meslek','-')}
- Baba: {sel_prof_data.get('baba_adi','-')} | Sağ: {sel_prof_data.get('baba_sag','-')} | Eğitim: {sel_prof_data.get('baba_egitim','-')} | Meslek: {sel_prof_data.get('baba_meslek','-')}
- Ebeveyn birlikte: {sel_prof_data.get('ebeveyn_birlikte','-')}
- Mevsimlik işçi: {sel_prof_data.get('mevsimlik_isci','-')}

**👨‍👩‍👧‍👦 Kardeşler**
- Kardeş sayısı: {sel_prof_data.get('kardes_sayisi','-')} | Kaçıncı çocuk: {sel_prof_data.get('kacinci_cocuk','-')} | Okula giden: {sel_prof_data.get('okula_giden_kardes','-')}
""")
                    dc2.markdown(f"""
**🏥 Sağlık**
- İlaç / Cihaz kullanımı: {sel_prof_data.get('ilac_kullaniyor','-')} {('— ' + sel_prof_data.get('ilac_adi','')) if sel_prof_data.get('ilac_adi') else ''}
- Tanısı konmuş hastalık / engel: {sel_prof_data.get('tani_var','-')} {('— ' + sel_prof_data.get('tani_aciklama','')) if sel_prof_data.get('tani_aciklama') else ''}
- Özel eğitim / kaynaştırma: {sel_prof_data.get('ozel_egitim','-')}
- Ailede süreğen hastalık / engel: {sel_prof_data.get('ailede_hastalik','-')} {('— ' + sel_prof_data.get('ailede_aciklama','')) if sel_prof_data.get('ailede_aciklama') else ''}

**🎨 Kulüp & Akademik Destek**
- Kulüp / Spor / Sanat: {sel_prof_data.get('kurs_kulup','-')} {('— Branş: ' + sel_prof_data.get('kurs_brans','')) if sel_prof_data.get('kurs_brans') else ''}
- Akademik destek: {', '.join(_pjson.loads(sel_prof_data.get('akademik_destek','[]') or '[]')) if sel_prof_data.get('akademik_destek') else '-'}
- Hobiler: {', '.join(_pjson.loads(sel_prof_data.get('hobiler','[]') or '[]')) if sel_prof_data.get('hobiler') else '-'}

**🏫 Okul Hayatı**
- Devamsızlık: {sel_prof_data.get('devamsizlik_gun','-')}
- Ders zorluğu: {sel_prof_data.get('ders_zorluk','-')}
- Zor dersler: {', '.join(_pjson.loads(sel_prof_data.get('zor_dersler','[]') or '[]'))}
- Okul değiştirdi: {sel_prof_data.get('okul_degistirdi','-')}
- Arkadaş edinme: {sel_prof_data.get('arkadas_edinme','-')}

**🌇 Günlük Hayat**
- Çalışma durumu: {sel_prof_data.get('calisma_durumu','-')}
- Ders ortamı: {sel_prof_data.get('ders_ortami','-')}
- İnternet erişimi: {sel_prof_data.get('internet_erisim','-')}
- Teknolojik aletler: {', '.join(_pjson.loads(sel_prof_data.get('teknoloji_aleti','[]') or '[]')) if sel_prof_data.get('teknoloji_aleti','').startswith('[') else (sel_prof_data.get('teknoloji_aleti') or '-') }

**💬 Kendini Anlat**
- Genel his: {sel_prof_data.get('genel_his','-')}
- Zorlayan şey: {sel_prof_data.get('zorlastiran_sey','-') or '(boş)'}
- Destek isteği: {sel_prof_data.get('destek_istek','-')}
- Önemli olay: {sel_prof_data.get('onemli_olay','-')}

**👨‍👩‍👧 Veli**
- Ad: {sel_prof_data.get('veli_adi','-')} | Yakınlık: {sel_prof_data.get('veli_yakinligi','-')}
- Tel: {sel_prof_data.get('veli_telefon','-')} | Meslek: {sel_prof_data.get('veli_meslek','-')}
""")

                # Tüm profilleri Excel olarak indir
                st.markdown("---")
                if st.button("📥 Tüm Profilleri Excel Olarak İndir", key="btn_profiles_excel"):
                    import io as _io
                    buf_p = _io.BytesIO()
                    # JSON listelerini temiz metne dönüştür
                    clean_profiles = []
                    for pr in all_profiles:
                        pr_copy = dict(pr)
                        for col_j in ["evde_kimseler", "zor_dersler", "hobiler", "teknoloji_aleti", "akademik_destek"]:
                            val_j = pr_copy.get(col_j, "")
                            if isinstance(val_j, str) and val_j.startswith("["):
                                try:
                                    pr_copy[col_j] = ", ".join(_pjson.loads(val_j))
                                except Exception:
                                    pass
                        clean_profiles.append(pr_copy)
                    df_full = pd.DataFrame(clean_profiles)
                    df_full.to_excel(buf_p, index=False, sheet_name="Öğrenci Profilleri")
                    buf_p.seek(0)
                    st.download_button(
                        "📥 Excel İndir",
                        data=buf_p.read(),
                        file_name="8B_Ogrenci_Profilleri.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="btn_profiles_excel_dl"
                    )


# ----------------- TAB 5: Rapor & Karne Üretici -----------------
with tab5:
    st.subheader("⚡ Tek Tıkla Rapor ve Karne Üretim & İndirme Merkezi")

    if current_role == "teacher":
        st.info("👩‍🏫 **Öğretmen:** Mevcut raporları indirebilirsiniz. Yeni sınav yüklemek için Admin girişi gereklidir.")

    st.markdown("Aşağıdaki butonları kullanarak tüm resmi raporları ve öğrenci karnelerini indirebilirsiniz.")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)

    with col_b1:
        st.markdown("#### 📑 Kapsamlı Word Raporu")
        w_path = os.path.join(EXPORTS_DIR, "8B_LGS_Akademik_Basari_ve_Strateji_Raporu.docx")
        if not os.path.exists(w_path):
            for alt in ["8B_LGS_Akademik_Rapor_Yeni.docx", "8B_LGS_Akademik_Basari_ve_Strateji_Raporu.docx"]:
                alt_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", alt)
                if os.path.exists(alt_p):
                    w_path = alt_p
                    break
        if current_role == "admin" and st.button("Raporu Yeniden Üret (.docx)", key="btn_word_gen", use_container_width=True):
            try:
                generate_word_report(selected_exam_name, results,
                                     {r['name']: get_student_kazanims(selected_exam_id, r['name']) for r in results},
                                     comps, w_path)
                st.success("Word Raporu hazırlandı!")
            except Exception as e:
                st.error(f"Hata: {e}")
        if os.path.exists(w_path):
            with open(w_path, "rb") as f_w:
                w_bytes = f_w.read()
            st.download_button("📥 Word Raporunu İndir (.docx)", data=w_bytes,
                               file_name="8B_LGS_Akademik_Basari_ve_Strateji_Raporu.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               use_container_width=True)

    with col_b2:
        st.markdown("#### 📗 Master Excel Takip Dosyası")
        x_path = os.path.join(EXPORTS_DIR, "8B_LGS_Takip_Sistemi.xlsx")
        if not os.path.exists(x_path):
            alt_x = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "8B_LGS_Takip_Sistemi.xlsx")
            if os.path.exists(alt_x):
                x_path = alt_x
        if current_role == "admin" and st.button("Excel'i Yeniden Üret (.xlsx)", key="btn_excel_gen", use_container_width=True):
            generate_excel_tracker(selected_exam_name, results,
                                   {r['name']: get_student_kazanims(selected_exam_id, r['name']) for r in results},
                                   comps, x_path)
            st.success("Master Excel hazırlandı!")
        if os.path.exists(x_path):
            with open(x_path, "rb") as f_x:
                x_bytes = f_x.read()
            st.download_button("📥 Excel Dosyasını İndir (.xlsx)", data=x_bytes,
                               file_name="8B_LGS_Takip_Sistemi.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

    with col_b3:
        st.markdown("#### 🖨️ Tüm Öğrenci Karneleri (29 Kişi)")
        c_dir = os.path.join(EXPORTS_DIR, "karneler")
        zip_karneler = os.path.join(EXPORTS_DIR, "8B_Tum_Karneler.zip")
        if not os.path.exists(zip_karneler):
            alt_z = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "8B_Tum_Karneler.zip")
            if os.path.exists(alt_z):
                zip_karneler = alt_z
        if current_role == "admin" and st.button("Karneleri Yeniden Paketle (ZIP)", key="btn_zip_gen", use_container_width=True):
            import zipfile
            cards = generate_all_student_cards(results, selected_exam_name,
                                               {r['name']: get_student_kazanims(selected_exam_id, r['name']) for r in results},
                                               c_dir)
            with zipfile.ZipFile(zip_karneler, 'w', zipfile.ZIP_DEFLATED) as zf:
                for cfile in cards:
                    zf.write(cfile, os.path.basename(cfile))
            st.success("29 karne başarıyla ZIP paketine dönüştürüldü!")
        if os.path.exists(zip_karneler):
            with open(zip_karneler, "rb") as f_z:
                z_bytes = f_z.read()
            st.download_button("📥 Tüm Karneleri ZIP İndir (29 Kişi)", data=z_bytes,
                               file_name="8B_Tum_Karneler.zip", mime="application/zip",
                               use_container_width=True)

    with col_b4:
        st.markdown("#### 📚 6 Branş Öğretmen Raporu")
        zip_branch = os.path.join(EXPORTS_DIR, "8B_Tum_Brans_Ogretmen_Raporlari.zip")
        try:
            all_kaz = {r['name']: get_student_kazanims(selected_exam_id, r['name']) for r in results}
            _, zip_branch = generate_all_branch_reports(selected_exam_name, results, all_kaz, comps)
            if os.path.exists(zip_branch):
                with open(zip_branch, "rb") as f_zb:
                    zb_bytes = f_zb.read()
                st.download_button("📥 6 Branşı ZIP İndir", data=zb_bytes,
                                   file_name="8B_Tum_Brans_Ogretmen_Raporlari.zip", mime="application/zip",
                                   use_container_width=True,
                                   key="btn_down_all_branch_zip_export_tab")
        except Exception as _e_zb:
            st.warning(f"Branş raporları hazırlanırken: {_e_zb}")


    # --- PIN LİSTESİ (Sadece Öğretmen ve Admin görür) ---
    st.markdown("---")
    st.subheader("🔑 Öğrenci Giriş Kodları (PIN Listesi)")
    st.caption("Bu liste yalnızca öğretmen ve admin tarafından görülebilir. Her öğrenciye yalnızca kendi kodunu verin.")

    import sqlite3 as _sqlite3
    from config import DATABASE_PATH as _DB_PATH
    _conn = _sqlite3.connect(_DB_PATH)
    _pin_rows = _conn.execute(
        "SELECT school_no, name, pin FROM students ORDER BY CAST(school_no AS INTEGER)"
    ).fetchall()
    _conn.close()

    if _pin_rows:
        # PIN tablosu
        pin_df = pd.DataFrame(_pin_rows, columns=["Okul No", "Adı Soyadı", "Giriş Kodu (PIN)"])
        st.dataframe(pin_df, use_container_width=True, height=600)

        # PIN listesini Excel olarak indir
        import io
        pin_buf = io.BytesIO()
        with pd.ExcelWriter(pin_buf, engine="openpyxl") as writer:
            pin_df.to_excel(writer, index=False, sheet_name="Öğrenci PIN Listesi")
        pin_buf.seek(0)
        st.download_button(
            "📥 PIN Listesini Excel Olarak İndir",
            data=pin_buf.read(),
            file_name="8B_Ogrenci_PIN_Listesi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        # Admin: PIN'leri sıfırla
        if current_role == "admin":
            st.markdown("---")
            with st.expander("⚠️ PIN Kodlarını Yeniden Oluştur (Admin)", expanded=False):
                st.warning("Bu işlem tüm öğrencilerin mevcut PIN kodlarını silip yeni 4 haneli kodlar oluşturur. "
                           "Eski kodlarla giriş yapılamaz! Yeni listeyi öğrencilere dağıtmayı unutmayın.")
                if st.button("🔄 Tüm PIN Kodlarını Yenile", key="btn_reset_pins"):
                    import random as _rnd
                    _chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
                    _conn2 = _sqlite3.connect(_DB_PATH)
                    _c2 = _conn2.cursor()
                    _ids = [r[0] for r in _c2.execute("SELECT id FROM students").fetchall()]
                    _used = set()
                    for _sid in _ids:
                        while True:
                            _new = "".join(_rnd.choices(_chars, k=4))
                            if _new not in _used:
                                _used.add(_new)
                                break
                        _c2.execute("UPDATE students SET pin = ? WHERE id = ?", (_new, _sid))
                    _conn2.commit()
                    _conn2.close()
                    st.success("✅ Tüm PIN kodları başarıyla yenilendi! Sayfayı yenileyin (F5) ve yeni listeyi indirin.")

