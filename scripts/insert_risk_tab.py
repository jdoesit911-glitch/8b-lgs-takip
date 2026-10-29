import sys
sys.stdout.reconfigure(encoding='utf-8')

RISK_TAB_CODE = '''
# ----------------- TAB RISK: Sinif Risk Haritasi -----------------
with tab_risk:
    init_risk_table()
    st.subheader("\U0001f5fa\ufe0f S\u0131n\u0131f Risk Haritas\u0131 — S.\u0130.4.a")
    st.caption("Kaynaktan alind\u0131: \u00d6zel E\u011fitim ve Rehberlik Hizmetleri Genel M\u00fcdurlugu")

    if current_role not in ("admin", "teacher"):
        # ─── \u00d6\u011frenci Anket Bolumu ─────────────────────────────────────────────────
        st.info("\U0001f4cb Bu bolumde sana birka\u00e7 soru sorulacak. Yan\u0131tlar\u0131n gizlidir ve yaln\u0131zca s\u0131n\u0131f \u00f6\u011fretmenin gorebilir.")

        if "risk_survey_done" not in st.session_state:
            st.session_state.risk_survey_done = False

        if st.session_state.risk_survey_done:
            st.success("\u2705 Yan\u0131tlar\u0131n kaydedildi! Te\u015fekk\u00fcr ederiz.")
        else:
            with st.form("student_risk_form"):
                st.markdown("**L\u00fctfen a\u015fa\u011f\u0131daki sorular\u0131 d\u00fczg\u00fcnce yan\u0131tla. Hi\u00e7bir yan\u0131t yanl\u0131\u015f de\u011fildir.**")

                q_kardes = st.radio(
                    "1\ufe0f\u20e3 Ailende ka\u00e7 karde\u015fin var?",
                    ["Tek \u00e7ocu\u011fum (karde\u015fim yok)", "1-2 karde\u015fim var", "3-4 karde\u015fim var", "5 veya daha fazla karde\u015fim var"],
                    index=None
                )
                q_aile = st.radio(
                    "2\ufe0f\u20e3 \u015eu an evde kimlerle ya\u015f\u0131yorsun?",
                    ["Annem ve babamla birlikte", "Yaln\u0131zca annemle", "Yaln\u0131zca babamla",
                     "B\u00fcy\u00fckanne/b\u00fcy\u00fckbabamla", "Di\u011fer akrabalar\u0131mla"],
                    index=None
                )
                q_devams = st.radio(
                    "3\ufe0f\u20e3 Bu donem ka\u00e7 gun okula gidemedin? (hastal\u0131k, zorunluluk vb.)",
                    ["Hi\u00e7 devams\u0131zl\u0131\u011f\u0131m yok", "1-3 gun", "4-9 gun", "10 gun ve \u00fczeri"],
                    index=None
                )
                q_calis = st.radio(
                    "4\ufe0f\u20e3 Okul d\u0131\u015f\u0131nda bir i\u015fte ya da tezgahta \u00e7al\u0131\u015f\u0131yor musun?",
                    ["Hay\u0131r", "Evet, bazen yard\u0131m ediyorum", "Evet, d\u00fczenli \u00e7al\u0131\u015f\u0131yorum"],
                    index=None
                )
                q_akademik = st.radio(
                    "5\ufe0f\u20e3 Dersleri yeti\u015ftirmekte ya da anlamakta ciddi zorluk \u00e7ekiyor musun?",
                    ["Hay\u0131r, genel olarak takip edebiliyorum", "Baz\u0131 derslerde zorlan\u0131yorum", "Evet, \u00e7o\u011fu dersde zorlan\u0131yorum"],
                    index=None
                )
                q_diger = st.text_area(
                    "6\ufe0f\u20e3 Payla\u015fmak istedi\u011fin ba\u015fka bir durum var m\u0131? (\u0130ste\u011fe ba\u011fl\u0131, bo\u015f b\u0131rakabilirsin)",
                    placeholder="\u00d6rn: ula\u015f\u0131m problemi, okul malzemesi eksikli\u011fi, arkada\u015fl\u0131k sorunlar\u0131..."
                )

                submitted = st.form_submit_button("\u2705 Yan\u0131tlar\u0131m\u0131 Kaydet", use_container_width=True, type="primary")
                if submitted:
                    if "student_id" in st.session_state:
                        answers = {}
                        # Kardes
                        if q_kardes == "Tek \u00e7ocu\u011fum (karde\u015fim yok)":
                            set_risk_factor(st.session_state.student_id, 3, True, source="student")
                        elif q_kardes == "5 veya daha fazla karde\u015fim var":
                            set_risk_factor(st.session_state.student_id, 4, True, source="student")
                        # Aile yap\u0131s\u0131
                        aile_map = {
                            "Yaln\u0131zca annemle": 7,
                            "Yaln\u0131zca babamla": 8,
                            "B\u00fcy\u00fckanne/b\u00fcy\u00fckbabamla": 13,
                            "Di\u011fer akrabalar\u0131mla": 14,
                        }
                        if q_aile in aile_map:
                            set_risk_factor(st.session_state.student_id, aile_map[q_aile], True, source="student")
                        # Devams\u0131zl\u0131k
                        if q_devams == "10 gun ve \u00fczeri":
                            set_risk_factor(st.session_state.student_id, 31, True, source="student")
                        # \u00c7al\u0131\u015fma
                        if q_calis and q_calis != "Hay\u0131r":
                            set_risk_factor(st.session_state.student_id, 32, True, source="student")
                        # Akademik
                        if q_akademik and q_akademik != "Hay\u0131r, genel olarak takip edebiliyorum":
                            set_risk_factor(st.session_state.student_id, 33, True, source="student")
                        # Di\u011fer
                        if q_diger and q_diger.strip():
                            set_risk_factor(st.session_state.student_id, 35, True, source="student", note=q_diger[:200])
                        st.session_state.risk_survey_done = True
                        st.rerun()
                    else:
                        st.error("Oturum hatas\u0131. L\u00fctfen tekrar giri\u015f yap\u0131n.")

    else:
        # ─── \u00d6\u011fretmen / Admin Risk Haritas\u0131 Paneli ─────────────────────────────────
        import sqlite3 as _sq
        from config import DATABASE_PATH as _DBP

        _conn_r = _sq.connect(_DBP)
        _students_r = _conn_r.execute(
            "SELECT id, school_no, name FROM students ORDER BY CAST(school_no AS INTEGER) ASC, id ASC"
        ).fetchall()
        _conn_r.close()

        all_risk = get_all_risk_data()

        # --- \u00d6zet Metrik Kutular\u0131 ---
        total_students = len(_students_r)
        total_at_risk = sum(1 for sid, _ in [(s[0], all_risk.get(s[0], set())) for s in _students_r] if all_risk.get(s[0]))
        risk_summary = get_risk_summary()

        rm1, rm2, rm3 = st.columns(3)
        rm1.metric("\U0001f4cc Toplam \u00d6\u011frenci", total_students)
        rm2.metric("\u26a0\ufe0f Risk Faktoru Olan", total_at_risk,
                   help="En az 1 risk fakt\u00f6r\u00fc i\u015faretlenmi\u015f \u00f6\u011frenci say\u0131s\u0131")
        top_factor = max(risk_summary, key=risk_summary.get) if risk_summary else None
        rm3.metric("\U0001f525 En Yayg\u0131n Fakt\u00f6r",
                   FACTOR_DICT[top_factor]["label"][:30] + "..." if top_factor else "—",
                   f"{risk_summary.get(top_factor, 0)} \u00f6\u011frenci" if top_factor else "")

        st.markdown("---")

        # --- Risk Faktoru Giris Ekrani ---
        tab_grid, tab_summary, tab_export = st.tabs([
            "\U0001f4dd Risk Faktoru Giri\u015fi",
            "\U0001f4ca Ozet & Analiz",
            "\U0001f4e5 Resmi PDF \u0130ndir"
        ])

        with tab_grid:
            st.markdown("**\u00d6\u011frenci se\u00e7in ve risk fakt\u00f6rlerini i\u015faretleyin:**")

            # \u00d6\u011frenci se\u00e7imi
            student_names_r = [f"{s[1]} — {s[2]}" for s in _students_r]
            sel_student_risk = st.selectbox("\u00d6\u011frenci Se\u00e7", student_names_r, key="risk_stu_sel")
            sel_idx_r = student_names_r.index(sel_student_risk)
            sel_stu_id_r = _students_r[sel_idx_r][0]
            sel_stu_name_r = _students_r[sel_idx_r][2]

            cur_factors = get_student_risk_factors(sel_stu_id_r)

            st.markdown(f"**{sel_stu_name_r}** \u2014 Mevcut risk fakt\u00f6rleri: {len(cur_factors)}")

            # Kategori gruplar\u0131na gore g\u00f6ster
            categories = {}
            for f in RISK_FACTORS:
                categories.setdefault(f["category"], []).append(f)

            cat_icons = {
                "Aile Yap\u0131s\u0131":    "\U0001f3e0",
                "\u00d6zel Durum":     "\U0001f6a8",
                "Aile Sa\u011fl\u0131\u011f\u0131":   "\u2764\ufe0f",
                "\u00d6\u011frenci Durumu": "\U0001f393",
            }

            updated_factors = set(cur_factors)

            with st.form(f"risk_form_{sel_stu_id_r}"):
                for cat, factors in categories.items():
                    icon = cat_icons.get(cat, "\u2022")
                    st.markdown(f"**{icon} {cat}**")
                    cols_f = st.columns(2)
                    for i, f in enumerate(factors):
                        default_val = f["id"] in cur_factors
                        label = f["label"]
                        if f["teacher_only"]:
                            label += " \U0001f512"
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
            st.markdown("### 📄 Resmi Risk Haritası Dışa Aktarma")
            st.info("Aşağıdaki butona tıklayarak Özel Eğitim ve Rehberlik Hizmetleri Genel Müdürlüğü S.İ.4.a formatında Word belgesini indirin.")

            school_inp = st.text_input("Okul Adı", value="")
            class_inp = st.text_input("Sınıf Adı", value="8/B")

            if st.button("🖨️ Resmi Risk Haritasını Oluştur (.docx)", use_container_width=True, type="primary"):
                try:
                    from core.risk_pdf_exporter import export_risk_pdf
                    risk_out_path = os.path.join(EXPORTS_DIR, "8B_Sinif_Risk_Haritasi.docx")
                    os.makedirs(EXPORTS_DIR, exist_ok=True)
                    students_list = [{"id": s[0], "school_no": s[1], "name": s[2]} for s in _students_r]
                    export_risk_pdf(
                        students=students_list,
                        risk_data=all_risk,
                        output_path=risk_out_path,
                        school_name=school_inp or "……",
                        class_name=class_inp or "8/B"
                    )
                    st.session_state["risk_doc_path"] = risk_out_path
                    st.success("✅ Risk Haritası oluşturuldu!")
                except Exception as e_rp:
                    st.error(f"Hata: {e_rp}")

            risk_doc_path = st.session_state.get("risk_doc_path", "")
            if not risk_doc_path:
                risk_doc_path = os.path.join(EXPORTS_DIR, "8B_Sinif_Risk_Haritasi.docx")

            if os.path.exists(risk_doc_path):
                with open(risk_doc_path, "rb") as f_rd:
                    rd_bytes = f_rd.read()
                st.download_button(
                    "📥 Risk Haritasını İndir (.docx)",
                    data=rd_bytes,
                    file_name="8B_Sinif_Risk_Haritasi.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

'''

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

marker = '# ----------------- TAB 5: Rapor & Karne Üretici -----------------'
if marker in content:
    content2 = content.replace(marker, RISK_TAB_CODE + '\n' + marker, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content2)
    print("SUCCESS: tab_risk block inserted before TAB 5")
else:
    # Try to find TAB 5 with unicode
    for candidate in ['with tab5:', '# ----------------- TAB 5:']:
        idx = content.find(candidate)
        if idx >= 0:
            content2 = content[:idx] + RISK_TAB_CODE + '\n' + content[idx:]
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content2)
            print(f"SUCCESS via candidate: {candidate}")
            break
    else:
        print("MARKER NOT FOUND")
        print([l for l in content.split('\n') if 'TAB 5' in l or 'tab5' in l][:5])
