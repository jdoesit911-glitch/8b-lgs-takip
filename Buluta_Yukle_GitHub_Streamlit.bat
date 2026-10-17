@echo off
chcp 65001 >nul
title 8/B LGS Sistemi - Bulut Dagitim Araci
echo ======================================================================
echo    8/B LGS TAKIP VE ANALIZ SISTEMINI BULUTA (STREAMLIT CLOUD) YUKLEME
echo ======================================================================
echo.
echo GitHub Kullanici Adiniz: jdoesit911-glitch
echo Hedef Depo: https://github.com/jdoesit911-glitch/8b-lgs-takip.git
echo.
echo [DIKKAT]: Eger GitHub'da '8b-lgs-takip' adli depoyu HENUZ ACMADIYSANIZ:
echo Tarayicinizda https://github.com/new adresine gidip
echo Repository name kismina '8b-lgs-takip' yazin ve yesil 'Create repository' butonuna basin!
echo.
echo Depoyu actiysaniz devam etmek icin herhangi bir tusa basin...
pause >nul

cd /d "%~dp0"
if not exist "app.py" (
    cd /d "C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu"
)

echo.
echo [1/3] Git ayarlari kontrol ediliyor...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/jdoesit911-glitch/8b-lgs-takip.git
git branch -M main

echo [2/3] Guncel dosyalar hazirlaniyor...
git add .
git commit -m "Bulut guncellemesi" >nul 2>&1

echo [3/3] Kodlar GitHub'a gonderiliyor...
echo.
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo   [TEBRIKLER] Kodlariniz GitHub'a basariyla aktarildi!
    echo ======================================================================
    echo.
    echo Simdi Streamlit ekranina (tarayiciniza) donun:
    echo Kirmizi uyarilarin kayboldugunu goreceksiniz!
    echo Sol alttaki mavi 'Deploy' butonuna basarak sitenizi hemen acabilirsiniz!
    echo ======================================================================
) else (
    echo.
    echo ======================================================================
    echo [UYARI] Yukleme tamamlanamadi! Olası 2 neden:
    echo 1. https://github.com/new adresinden '8b-lgs-takip' adli depoyu henuz acmadiniz.
    echo 2. Tarayicida GitHub oturumunuz acik degil veya erisim izni verilmedi.
    echo ======================================================================
)

echo.
pause
