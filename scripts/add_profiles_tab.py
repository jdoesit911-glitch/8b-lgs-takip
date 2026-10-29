import sys
sys.stdout.reconfigure(encoding='utf-8')

PROFILES_TAB_CODE = '''
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
                    summary_rows.append({
                        "Okul No":      p.get("school_no", ""),
                        "Adı Soyadı":   p.get("name", ""),
                        "Cinsiyet":     p.get("cinsiyet", ""),
                        "Cep Tel":      p.get("cep_telefon", ""),
                        "Kardeş":       p.get("kardes_sayisi", ""),
                        "Anne Eğitim":  p.get("anne_egitim", ""),
                        "Baba Eğitim":  p.get("baba_egitim", ""),
                        "Devamsızlık":  p.get("devamsizlik_gun", ""),
                        "Ders Zorluk":  p.get("ders_zorluk", ""),
                        "Çalışma":      p.get("calisma_durumu", ""),
                        "Genel His":    p.get("genel_his", ""),
                        "Destek İstek": p.get("destek_istek", ""),
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
- İlaç kullanımı: {sel_prof_data.get('ilac_kullaniyor','-')} {('('+sel_prof_data.get('ilac_adi','')+')'  ) if sel_prof_data.get('ilac_adi') else ''}
- Tanı: {sel_prof_data.get('tani_var','-')} {('('+sel_prof_data.get('tani_aciklama','')+')'  ) if sel_prof_data.get('tani_aciklama') else ''}
- Özel eğitim: {sel_prof_data.get('ozel_egitim','-')}
- Ailede hastalık: {sel_prof_data.get('ailede_hastalik','-')}

**🏫 Okul Hayatı**
- Devamsızlık: {sel_prof_data.get('devamsizlik_gun','-')}
- Ders zorluğu: {sel_prof_data.get('ders_zorluk','-')}
- Zor dersler: {', '.join(_pjson.loads(sel_prof_data.get('zor_dersler','[]') or '[]'))}
- Okul değiştirdi: {sel_prof_data.get('okul_degistirdi','-')}
- Arkadaş edinme: {sel_prof_data.get('arkadas_edinme','-')}

**🌇 Günlük Hayat**
- Çalışma: {sel_prof_data.get('calisma_durumu','-')}
- Ders ortamı: {sel_prof_data.get('ders_ortami','-')}
- İnternet: {sel_prof_data.get('internet_erisim','-')}

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
                    df_full = pd.DataFrame(all_profiles)
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
'''

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 3-tab admin panel with 4-tab panel
old_tabs = (
    '        tab_grid, tab_summary, tab_export = st.tabs([\n'
    '            "📝 Risk Faktoru Girişi",\n'
    '            "📊 Ozet & Analiz",\n'
    '            "📥 Resmi PDF İndir"\n'
    '        ])'
)
new_tabs = (
    '        tab_grid, tab_summary, tab_export, tab_profiles = st.tabs([\n'
    '            "📝 Risk Faktörü Girişi",\n'
    '            "📊 Özet & Analiz",\n'
    '            "📥 Resmi PDF İndir",\n'
    '            "📋 Öğrenci Profilleri"\n'
    '        ])'
)

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs, 1)
    print("Tab header replaced OK")
else:
    print("Tab header NOT FOUND")
    idx = content.find('tab_grid, tab_summary, tab_export')
    print(repr(content[idx:idx+300]))

# Find end of tab_export block (just before the closing of tab_risk with block)
# Insert tab_profiles after the last line of tab_export
insert_marker = '                )\n\n'
# Find where tab_export ends - after the download button closing paren
idx_export_end = content.find('                    use_container_width=True\n                )\n\n', content.find('with tab_export:'))
if idx_export_end > 0:
    insert_at = idx_export_end + len('                    use_container_width=True\n                )\n\n')
    content = content[:insert_at] + PROFILES_TAB_CODE + '\n' + content[insert_at:]
    print("Profiles tab inserted OK")
else:
    # fallback: append before the TAB 5 marker
    idx_tab5 = content.find('# ----------------- TAB 5:')
    if idx_tab5 > 0:
        # go back to find end of with tab_risk block
        # just insert before TAB 5
        content = content[:idx_tab5] + PROFILES_TAB_CODE + '\n' + content[idx_tab5:]
        print("Profiles tab inserted before TAB 5 (fallback)")
    else:
        print("FALLBACK MARKER NOT FOUND")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

import ast
with open('app.py', 'r', encoding='utf-8') as f:
    src = f.read()
try:
    ast.parse(src)
    print(f"SYNTAX OK — {len(src.splitlines())} lines")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
