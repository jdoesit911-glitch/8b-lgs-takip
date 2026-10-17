# 🎓 LGS Akademik Başarı ve Analiz Otomasyon Sistemi

Bu proje, ortaokul 8. sınıf (özellikle 8/B şubesi) öğrencilerinin yıl boyunca girecekleri tüm kurumsal LGS deneme sınavlarını (PARAF, Özdebir, Töder, Kırmızı Beyaz, EDESİS vb.) otomatik olarak analiz etmek, veri tabanında saklamak, zaman içindeki gelişimlerini takip etmek ve tek tıkla resmi raporlar ile bireysel öğrenci karneleri üretmek amacıyla geliştirilmiş tam kapsamlı bir otomasyon sistemidir.

---

## 🚀 Hızlı Başlangıç

### 1. Web Arayüzünü Başlatma (Tavsiye Edilen)
Masaüstündeki veya klasör içindeki başlatıcıya çift tıklayın:
- `C:\Users\ELRA\Desktop\8B sınıfı veriler\LGS_Takip_Sistemini_Baslat.bat`

Veya terminalden:
```powershell
cd "C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu"
streamlit run app.py
```
Tarayıcınızda otomatik olarak interaktif kontrol paneli (`http://localhost:8501`) açılacaktır.

### 2. Komut Satırı (CLI) ile Kullanım
Yeni bir deneme sınavı Excel dosyasını tek komutla işlemek için:
```powershell
python cli.py --file "C:\Users\ELRA\Downloads\PARAF LGS 1 Sonuç ve Analiz Raporları.xlsx" --class-name "8/B"
```

---

## 📁 Proje Dizin Yapısı

```
lgs_analiz_otomasyonu/
├── app.py                      # Streamlit İnteraktif Web Kontrol Paneli
├── cli.py                      # Komut Satırı Çalıştırma Arayüzü
├── config.py                   # Sınav katsayıları, soru sayıları, başarı kademeleri
├── core/
│   ├── database.py             # SQLite boylamsal (longitudinal) veritabanı yöneticisi
│   ├── parser.py               # Akıllı Excel ayrıştırıcı (yayıncı bağımsız)
│   ├── analyzer.py             # İstatistik, Pareto, SWOT ve destek grubu motoru
│   ├── word_generator.py       # 22 bölümlük Master Word Raporu (.docx) üreticisi
│   ├── excel_generator.py      # 7 sekmeli dinamik Master Excel Takip Dosyası (.xlsx)
│   └── student_card_gen.py     # Tek sayfalık baskıya hazır öğrenci karneleri üreticisi
├── database/
│   └── lgs_history.db          # Yıl boyunca girilen tüm sınavların SQLite veri tabanı
└── exports/                    # Çıktıların varsayılan kopyaları
```

---

## 🎯 Temel Yetenekler ve Özellikler

1. **Yıl Boyu Çoklu Deneme Takibi (Longitudinal Database):**
   - Her deneme sınavı (Deneme 1, 2, 3...) `lgs_history.db` SQLite veri tabanına kaydedilir.
   - Zaman içindeki net artışları ($\Delta \text{Net}$), plato yapan veya sıçrama yapan öğrenciler otomatik tespit edilir.
2. **Kazanım Matrisi ve Isı Haritası (Heatmap):**
   - Her öğrencinin hangi kazanımda %100 başarılı olduğu, hangisinde sıfır (%0) çektiği renkli olarak modellenir.
3. **Pareto Net Kaybı (80/20 İlkesi):**
   - Kaybedilen netlerin hangi ders ve konularda yoğunlaştığını hesaplar.
4. **Tek Tıkla Çıktı Üretimi:**
   - 📑 **Master Word Raporu (.docx):** Yönetici özeti, okul karşılaştırması ve 27 öğrenci profili.
   - 📗 **Master Excel Takip Dosyası (.xlsx):** Kazanım matrisli dinamik takip çizelgesi.
   - 🖨️ **Öğrenci Karneleri (.docx):** Her öğrenci için veli imzalı, 1 sayfalık baskıya hazır gelişim karnesi (`karneler/` klasörüne kaydedilir).

---

## ☁️ Sistemi İnternette Canlı Web Sitesine Dönüştürme (Ücretsiz Bulut)

Bu sistemi Streamlit Community Cloud üzerinde **tamamen ücretsiz** ve **7/24 kesintisiz** çalışan canlı bir web sitesi olarak yayınlayabilirsiniz. Böylece evden, akıllı tahtadan veya cep telefonunuzdan dilediğiniz zaman erişebilir, yeni deneme yükleyebilir veya rapor indirebilirsiniz.

### 3 Adımda Canlıya Alma:

1. **GitHub Deposu Oluşturma:**
   - [github.com](https://github.com) adresine gidin ve ücretsiz bir hesapla oturum açın.
   - Sağ üstteki `+` simgesine tıklayıp **"New repository"** seçin.
   - Depo adını yazın (örnek: `8b-lgs-takip`) ve **Private (Gizli)** veya Public olarak oluşturun.
   - Sayfada verilen HTTPS linkini kopyalayın (`https://github.com/kullanici/8b-lgs-takip.git`).

2. **Kodları GitHub'a Yükleme:**
   - Masaüstünüzdeki `8B sınıfı veriler` klasöründe yer alan **`Buluta_Yukle_GitHub_Streamlit.bat`** dosyasına çift tıklayın.
   - Kopyaladığınız GitHub linkini yapıştırıp Enter'a basın. Kodlar otomatik olarak GitHub deponuza yüklenecektir.

3. **Streamlit Cloud ile Canlıya Alma:**
   - [share.streamlit.io](https://share.streamlit.io) adresine gidin ve GitHub hesabınızla giriş yapın.
   - **"Create app"** (veya "New app") butonuna basın.
   - **Repository:** `kullanici/8b-lgs-takip` seçin.
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **"Deploy!"** butonuna basın.

🎉 **Sonuç:** Yaklaşık 1 dakika içinde `https://8b-lgs-takip.streamlit.app` gibi özel bir web linkiniz hazır olacaktır!

> 🔒 **Gizlilik ve Güvenlik Notu:**
> Öğrenci kişisel verilerinin korunması amacıyla web sitesine ilk girişte **Öğretmen PIN Kodu** sorulacaktır.
> **Varsayılan PIN:** `8B2026`

