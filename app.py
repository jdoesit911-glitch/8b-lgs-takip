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
from core.student_card_gen import generate_all_student_cards, generate_single_student_card, get_subject_prescriptions
from config import EXPORTS_DIR, SUBJECTS

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
            pin_input = st.text_input("Öğrenci Giriş Kodunuz (4 hane):", placeholder="Örn: AB1C",
                                      help="Öğretmeninizden aldığınız 4 karakterli kodu giriniz.")
            if st.button("🎒 Öğrenci Olarak Giriş Yap", use_container_width=True):
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
                    st.rerun()
                else:
                    st.error("❌ Hatalı giriş kodu! Lütfen öğretmeninizden aldığınız 4 haneli kodu kontrol edin.")

        elif role_choice == "Öğretmen":
            st.info("👩‍🏫 **Öğretmen Girişi:** Tüm öğrenci verilerini ve raporları görüntüleyebilirsiniz.")
            pin_input = st.text_input("Öğretmen Erişim Şifresi:", type="password")
            if st.button("👩‍🏫 Öğretmen Olarak Giriş Yap", use_container_width=True):
                if pin_input == TEACHER_PIN:
                    st.session_state.role = "teacher"
                    st.rerun()
                else:
                    st.error("❌ Hatalı şifre!")

        elif role_choice == "Admin":
            st.info("🔑 **Admin Girişi:** Tüm yetkilere sahipsiniz. Yeni deneme sınavı yükleyebilirsiniz.")
            pin_input = st.text_input("Admin Şifresi:", type="password")
            if st.button("🔑 Admin Olarak Giriş Yap", use_container_width=True):
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
selected_exam_name = st.sidebar.selectbox("📅 Aktif Deneme Sınavı:", exam_names)

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

            # 6/6 – Excel takip dosyası
            prog_status.markdown("**6/6** 📗 Master Excel Takip Dosyası oluşturuluyor...")
            prog_bar.progress(90)
            x_out = os.path.join(EXPORTS_DIR, "8B_LGS_Takip_Sistemi.xlsx")
            try:
                generate_excel_tracker(exam_name_new, new_results, new_kaz_map, new_comps, x_out)
            except Exception as _e:
                st.warning(f"Excel dosyası oluşturulurken uyarı: {_e}")

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

if st.sidebar.button("🔒 Çıkış Yap (Ekranı Kilitle)"):
    st.session_state.role = None
    st.session_state.student_name = None
    st.session_state.student_no = None
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

    # --- Öğrenci KPI ---
    st.markdown(f"## 🎒 Hoş Geldiniz, {student_name.title()}!")
    st.markdown("---")

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

    st.markdown("---")
    st.markdown("### 🔬 6 Branş İçin Kişiselleştirilmiş Gelişim Reçeteleri")
    sub_recs = get_subject_prescriptions(st_data, st_kaz)
    sub_cols = st.columns(2)
    idx_c = 0
    for s_title in ["Fen Bilimleri", "Matematik", "Türkçe", "İnkılap Tarihi", "Din Kültürü", "İngilizce"]:
        if s_title in sub_recs:
            s_info = sub_recs[s_title]
            with sub_cols[idx_c % 2]:
                with st.expander(f"{s_info['title']} (Net: {s_info['net']:.2f} | D:{s_info['d']} Y:{s_info['y']} B:{s_info['b']})"):
                    st.markdown(f"**📊 Kazanım Başarı Dökümü:** {s_info['summary']}")
                    if s_info.get('zero'):
                        st.error(f"**🔴 Sıfır Çekilenler (%0):** {', '.join(s_info['zero'])}")
                    if s_info.get('low'):
                        st.warning(f"**🟡 Pekiştirilecekler (<% 100):** {', '.join(s_info['low'])}")
                    if s_info.get('mast'):
                        st.success(f"**🟢 Tam Hakim Olunanlar:** {len(s_info['mast'])} kazanım")
                    st.info(f"**💡 Çalışma Reçetesi:** {s_info['advice']}")
                    if s_info.get('youtube'):
                        yt = s_info['youtube']
                        st.markdown(f"""
                        <div style='background-color:#FDEDEC; border-left:4px solid #C0392B; padding:10px; border-radius:6px; margin-top:8px;'>
                            <b style='color:#900C3F;'>📺 Önerilen YouTube Desteği:</b> <b>{yt['channel']}</b> <span style='background-color:{yt['badge_color']}; color:white; padding:2px 7px; border-radius:10px; font-size:11px; font-weight:bold;'>{yt['level_name']}</span><br>
                            <small>🎯 <b>Odak:</b> {yt['focus']}<br>
                            💡 <b>Çalışma Taktiği:</b> {yt['study_tip']}</small><br>
                            <a href='{yt['search_url']}' target='_blank' style='display:inline-block; margin-top:6px; background-color:#C0392B; color:white; padding:5px 12px; border-radius:4px; text-decoration:none; font-size:12px; font-weight:bold;'>
                                ▶️ {yt['channel']} ile Dersi İzle
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
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

    st.stop()  # Öğrenci görünümü burada biter


# ╔══════════════════════════════════════════════════════════╗
# ║       ÖĞRETMEN & ADMİN GÖRÜNÜMÜ (Tam Dashboard)         ║
# ╚══════════════════════════════════════════════════════════╝

tabs_list = [
    "📊 Sınıf Genel Görünümü",
    "🎯 Kazanım & Pareto Analizi",
    "👤 Bireysel Öğrenci Karneleri",
    "📈 Çoklu Deneme Gelişim Takibi",
    "⚡ Otomatik Rapor & Karne Üretici"
]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs_list)

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
    col_chart, col_tiers = st.columns([3, 2])
    with col_chart:
        st.subheader("📌 Ders Bazında 8/B ve Okul Karşılaştırması")
        comp_df = pd.DataFrame(comps)
        if not comp_df.empty:
            fig, ax = plt.subplots(figsize=(8, 4))
            x = np.arange(len(comp_df))
            width = 0.35
            ax.bar(x - width/2, comp_df['class_8b'], width, label='8/B Sınıfı', color='#1F497D')
            ax.bar(x + width/2, comp_df['school_avg'], width, label='Okul Ortalaması', color='#A6ACAF')
            ax.set_xticks(x)
            ax.set_xticklabels(comp_df['subject'], rotation=15, ha='right')
            ax.set_ylabel("Net")
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)
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
        st.markdown("""
        Bu otomasyon, her öğrencinin sınav netine ve sıfır/düşük çektiği kazanımlara göre otomatik seviye belirler, doğrudan ilgili hocanın konu anlatımına ve soru çözümüne yönlendirir:
        """)
        yt_summary_data = [
            {"Ders": "Matematik", "Temel Seviye (<8 Net)": "Partikül Matematik", "Orta Seviye (8-15 Net)": "İMT HOCA", "İyi Seviye (15+ Net)": "Çopur Hoca"},
            {"Ders": "Türkçe", "Temel Seviye (<8 Net)": "Tonguç Akademi", "Orta Seviye (8-15 Net)": "Hız Yayınları - Ebubekir Hoca", "İyi Seviye (15+ Net)": "Hız Yayınları / Ebubekir Hoca"},
            {"Ders": "Fen Bilimleri", "Temel Seviye (<8 Net)": "Derslike", "Orta Seviye (8-15 Net)": "Mehmet Hoca ile Fen", "İyi Seviye (15+ Net)": "Hız Yayınları / dnz hoca"},
            {"Ders": "İnkılap Tarihi", "Temel Seviye (<5 Net)": "Sosyal Kale", "Orta Seviye (5-8 Net)": "Sosyal Kale", "İyi Seviye (8+ Net)": "Buğra Hoca Sosyal Bilgiler Dersliği"},
            {"Ders": "Din Kültürü", "Temel Seviye (<5 Net)": "Cebrail Hocam", "Orta Seviye (5-8 Net)": "Cebrail Hocam", "İyi Seviye (8+ Net)": "Cebrail Hocam"},
            {"Ders": "İngilizce", "Temel Seviye (<5 Net)": "Tonguç Akademi", "Orta Seviye (5-8 Net)": "Dilek Demirel", "İyi Seviye (8+ Net)": "Ümitcan Hoca"},
        ]
        st.dataframe(pd.DataFrame(yt_summary_data), use_container_width=True, hide_index=True)

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

        st.markdown("---")
        st.markdown("### 🔬 6 Branş İçin Kişiselleştirilmiş Gelişim Reçeteleri")
        sub_recs = get_subject_prescriptions(st_data, st_kaz)
        sub_cols = st.columns(2)
        idx_c = 0
        for s_title in ["Fen Bilimleri", "Matematik", "Türkçe", "İnkılap Tarihi", "Din Kültürü", "İngilizce"]:
            if s_title in sub_recs:
                s_info = sub_recs[s_title]
                with sub_cols[idx_c % 2]:
                    with st.expander(f"{s_info['title']} (Net: {s_info['net']:.2f} | D:{s_info['d']} Y:{s_info['y']} B:{s_info['b']})",
                                     expanded=(s_title == "Fen Bilimleri")):
                        st.markdown(f"**📊 Kazanım Başarı Dökümü:** {s_info['summary']}")
                        if s_info.get('zero'):
                            st.error(f"**🔴 Sıfır Çekilenler:** {', '.join(s_info['zero'])}")
                        if s_info.get('low'):
                            st.warning(f"**🟡 Pekiştirilecekler:** {', '.join(s_info['low'])}")
                        if s_info.get('mast'):
                            st.success(f"**🟢 Tam Hakim Olunanlar:** {len(s_info['mast'])} kazanım")
                        st.info(f"**💡 Çalışma Reçetesi:** {s_info['advice']}")
                        if s_info.get('youtube'):
                            yt = s_info['youtube']
                            st.markdown(f"""
                            <div style='background-color:#FDEDEC; border-left:4px solid #C0392B; padding:10px; border-radius:6px; margin-top:8px;'>
                                <b style='color:#900C3F;'>📺 Önerilen YouTube Desteği:</b> <b>{yt['channel']}</b> <span style='background-color:{yt['badge_color']}; color:white; padding:2px 7px; border-radius:10px; font-size:11px; font-weight:bold;'>{yt['level_name']}</span><br>
                                <small>🎯 <b>Odak:</b> {yt['focus']}<br>
                                💡 <b>Çalışma Taktiği:</b> {yt['study_tip']}</small><br>
                                <a href='{yt['search_url']}' target='_blank' style='display:inline-block; margin-top:6px; background-color:#C0392B; color:white; padding:5px 12px; border-radius:4px; text-decoration:none; font-size:12px; font-weight:bold;'>
                                    ▶️ {yt['channel']} ile Dersi İncele
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                idx_c += 1

# ----------------- TAB 4: Çoklu Deneme Gelişim -----------------
with tab4:
    st.subheader("📈 Çoklu Deneme Sınavı ve Zaman Serisi Gelişim Takibi")
    st.markdown("Yıl boyunca uygulanan tüm deneme sınavlarının karşılaştırmalı net eğrileri burada izlenir.")

    # Tab 3'teki selected_student kullanılır
    if 'selected_student' not in dir():
        selected_student = results[0]['name'] if results else ""

    st_hist = get_student_history(selected_student)
    if len(st_hist) > 1:
        df_hist = pd.DataFrame(st_hist)
        fig_h, ax_h = plt.subplots(figsize=(8, 3))
        ax_h.plot(df_hist['exam_name'], df_hist['top_net'], marker='o', linewidth=2, color='#1F497D', label='Toplam Net')
        ax_h.set_ylabel("Net")
        ax_h.grid(True, linestyle='--', alpha=0.5)
        ax_h.legend()
        st.pyplot(fig_h)
    else:
        st.info("Sistemde şu an yalnızca 1 deneme sınavı kayıtlıdır. 2. ve 3. denemeler yüklendikçe grafik burada belirecektir.")

# ----------------- TAB 5: Rapor & Karne Üretici -----------------
with tab5:
    st.subheader("⚡ Tek Tıkla Rapor ve Karne Üretim & İndirme Merkezi")

    if current_role == "teacher":
        st.info("👩‍🏫 **Öğretmen:** Mevcut raporları indirebilirsiniz. Yeni sınav yüklemek için Admin girişi gereklidir.")

    st.markdown("Aşağıdaki butonları kullanarak tüm resmi raporları ve öğrenci karnelerini indirebilirsiniz.")
    col_b1, col_b2, col_b3 = st.columns(3)

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
        st.markdown("#### 🖨️ 27 Öğrencinin Tüm Karneleri")
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
            st.success("27 karne başarıyla ZIP paketine dönüştürüldü!")
        if os.path.exists(zip_karneler):
            with open(zip_karneler, "rb") as f_z:
                z_bytes = f_z.read()
            st.download_button("📥 27 Karneyi ZIP Olarak İndir", data=z_bytes,
                               file_name="8B_Tum_Karneler.zip", mime="application/zip",
                               use_container_width=True)

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

