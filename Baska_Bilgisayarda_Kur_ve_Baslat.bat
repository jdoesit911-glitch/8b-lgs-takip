@echo off
chcp 65001 > nul
title 8/B LGS Takip Sistemi - Kurulum ve Başlatıcı
echo ============================================================
echo   8/B LGS TAKIP VE ANALIZ SISTEMI - OTOMATIK KURULUM
echo ============================================================
echo.
echo 1. Gerekli Python kütüphaneleri kontrol ediliyor / yükleniyor...
pip install -r requirements.txt
echo.
echo 2. Sistem başlatılıyor... Lütfen bekleyin.
echo Web paneli otomatik olarak tarayıcınızda açılacaktır.
echo.
streamlit run app.py --server.port 8501 --server.headless false
pause
