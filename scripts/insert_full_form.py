import sys
sys.stdout.reconfigure(encoding='utf-8')

STUDENT_FORM_CODE = r'''
        # ─── Öğrenci Tanıma Formu ────────────────────────────────────────────────────
        from core.student_profile import (init_profile_table, save_profile, get_profile,
                                          profile_exists, profile_to_risk_factors)
        init_profile_table()

        stu_id_form = st.session_state.get("student_id")
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

                with st.form("student_profile_form", clear_on_submit=False):

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
                    ilac_kullaniyor = st.radio("4.1 Sürekli kullandığınız bir ilaç veya tıbbi cihazınız var mı?",
                                               ["Hayır", "Evet"], horizontal=True,
                                               index=0 if existing.get("ilac_kullaniyor","Hayır") == "Hayır" else 1)
                    ilac_adi = ""
                    if ilac_kullaniyor == "Evet":
                        ilac_adi = st.text_input("İlaç/cihaz adı (zorunlu değil)", value=existing.get("ilac_adi",""))

                    tani_var = st.radio("4.2 Tanısı konulmuş bir hastalığınız ya da engel durumunuz var mı?",
                                        ["Hayır", "Evet"], horizontal=True,
                                        index=0 if existing.get("tani_var","Hayır") == "Hayır" else 1)
                    tani_aciklama = ""
                    if tani_var == "Evet":
                        tani_aciklama = st.text_input("Rahatsızlığınızı belirtmek ister misiniz? (zorunlu değil)",
                                                      value=existing.get("tani_aciklama",""))

                    ozel_egitim_opts = ["Hayır", "Evet, özel eğitim alıyorum",
                                        "Evet, kaynaştırma öğrencisiyim", "Evet, destek eğitimi alıyorum"]
                    ozel_egitim = st.radio("4.3 Özel eğitim, kaynaştırma veya destek eğitimi alıyor musunuz?",
                                           ozel_egitim_opts,
                                           index=ozel_egitim_opts.index(existing.get("ozel_egitim","Hayır")) if existing.get("ozel_egitim") in ozel_egitim_opts else 0)

                    ailede_hastalik = st.radio("4.4 Ailenizde uzun süreli bir hastalığı ya da engel durumu olan biri var mı?",
                                               ["Hayır", "Evet"], horizontal=True,
                                               index=0 if existing.get("ailede_hastalik","Hayır") == "Hayır" else 1)

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

                    tekno_opts = ["Tablet / Bilgisayar", "Akıllı telefon", "Hiçbiri"]
                    teknoloji_aleti = st.radio("6.4 Kendinize ait bir teknolojik aletiniz var mı?",
                                               tekno_opts, horizontal=True,
                                               index=tekno_opts.index(existing.get("teknoloji_aleti","Akıllı telefon")) if existing.get("teknoloji_aleti") in tekno_opts else 1)

                    st.markdown("---")
                    # ── BÖLÜM 7: İlgi ve Hobiler ───────────────────────────────────
                    st.markdown("### 🎨 Bölüm 7 — İlgi ve Hobiler")
                    hobi_opts = ["Spor / Hareket", "Müzik / Sanat / Resim",
                                 "Kitap okumak", "Teknoloji / Oyun", "Doğa / Gezi", "Diğer"]
                    _hobi_default = _json.loads(existing.get("hobiler","[]") or "[]") if existing else []
                    hobiler = st.multiselect("7.1 Ne yapmaktan hoşlanırsınız? (Birden fazla seçebilirsiniz)",
                                             hobi_opts, default=_hobi_default)

                    kurs_kulup = st.radio("7.2 Okul dışında katıldığınız bir kurs, kulüp veya spor var mı?",
                                          ["Hayır", "Evet"], horizontal=True,
                                          index=0 if existing.get("kurs_kulup","Hayır") == "Hayır" else 1)
                    kurs_adi = ""
                    if kurs_kulup == "Evet":
                        kurs_adi = st.text_input("Hangisi?", value=existing.get("kurs_adi",""))

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
                    submitted_profile = st.form_submit_button("✅ Formu Kaydet", use_container_width=True, type="primary")

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
                        "ozel_egitim": ozel_egitim, "ailede_hastalik": ailede_hastalik,
                        "devamsizlik_gun": devamsizlik_gun, "ders_zorluk": ders_zorluk,
                        "zor_dersler": zor_dersler, "okul_degistirdi": okul_degistirdi,
                        "arkadas_edinme": arkadas_edinme,
                        "calisma_durumu": calisma_durumu, "ders_ortami": ders_ortami,
                        "internet_erisim": internet_erisim, "teknoloji_aleti": teknoloji_aleti,
                        "hobiler": hobiler, "kurs_kulup": kurs_kulup, "kurs_adi": kurs_adi,
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
'''

# Build the replacement: replace old student anket block with new comprehensive form
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the student survey section inside tab_risk
old_start = "        if \"risk_survey_done\" not in st.session_state:"
old_end   = "                    else:\n                        st.error(\"Oturum hatası. Lütfen tekrar giriş yapın.\")"

idx_start = content.find(old_start)
idx_end   = content.find(old_end)

if idx_start == -1 or idx_end == -1:
    print(f"MARKERS NOT FOUND: start={idx_start}, end={idx_end}")
    # show context around tab_risk student section
    idx_tab_risk = content.find("with tab_risk:")
    print("tab_risk at:", idx_tab_risk)
    print(repr(content[idx_tab_risk:idx_tab_risk+500]))
else:
    # Find end of old_end line
    idx_end_full = content.find("\n", idx_end + len(old_end)) + 1

    # Also remove the risk_survey_done success block just before
    # Find the "if st.session_state.risk_survey_done:" block
    survey_done_marker = "        if st.session_state.risk_survey_done:\n            st.success"
    idx_done_start = content.rfind(survey_done_marker, 0, idx_start)

    if idx_done_start != -1:
        replace_start = idx_done_start
    else:
        replace_start = idx_start

    old_block = content[replace_start:idx_end_full]
    content2  = content[:replace_start] + STUDENT_FORM_CODE + "\n" + content[idx_end_full:]

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content2)
    print("REPLACED OK")

    # Verify syntax
    import ast
    with open('app.py', 'r', encoding='utf-8') as f:
        src = f.read()
    try:
        ast.parse(src)
        print(f"SYNTAX OK - {len(src.splitlines())} lines")
    except SyntaxError as e:
        print(f"SYNTAX ERROR: {e}")
