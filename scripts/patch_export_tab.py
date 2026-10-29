import sys
sys.stdout.reconfigure(encoding='utf-8')

NEW_EXPORT_TAB = '''
        with tab_export:
            st.markdown("### 📄 Resmi Risk Haritası — Tek Sayfa Çıktı")

            ex1, ex2 = st.columns(2)
            school_inp = ex1.text_input("Okul Adı", value="", key="risk_school_inp")
            class_inp  = ex2.text_input("Sınıf Adı", value="8/B", key="risk_class_inp")

            students_list = [{"id": s[0], "school_no": s[1], "name": s[2]} for s in _students_r]

            col_dl1, col_dl2 = st.columns(2)

            # ── Word İndir ────────────────────────────────────────────────────
            with col_dl1:
                st.markdown("#### 📝 Word Belgesi (.docx)")
                st.caption("Yatay A4, tek sayfa, renkli kategoriler, ✓ işaretleri")
                if st.button("⚙️ Word Dosyasını Oluştur", key="btn_risk_word", use_container_width=True, type="primary"):
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
            with col_dl2:
                st.markdown("#### 🖨️ Tarayıcıda Yazdır / PDF")
                st.caption("Önizlemeyi açın → Ctrl+P → 'Yatay' seçin → PDF olarak kaydedin")
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
'''

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the entire tab_export block
old_start = '        with tab_export:\n            st.markdown("### 📄 Resmi Risk Haritası Dışa Aktarma")'
old_end_marker = '                if st.button("❌ Önizlemeyi Kapat"'
# Find a clean end — just before the final closing of the tab_export with block
# which is the profiles tab starting
profiles_marker = '\n        with tab_profiles:\n'

idx_start = content.find(old_start)
idx_profiles = content.find(profiles_marker)

if idx_start == -1:
    print("START NOT FOUND")
elif idx_profiles == -1:
    print("PROFILES MARKER NOT FOUND")
else:
    old_block = content[idx_start:idx_profiles]
    content2 = content[:idx_start] + NEW_EXPORT_TAB + '\n' + content[idx_profiles:]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content2)
    print(f"REPLACED: {len(old_block)} chars → {len(NEW_EXPORT_TAB)} chars")

    import ast
    with open('app.py', 'r', encoding='utf-8') as f:
        src = f.read()
    try:
        ast.parse(src)
        print(f"SYNTAX OK — {len(src.splitlines())} lines")
    except SyntaxError as e:
        print(f"SYNTAX ERROR: {e}")
