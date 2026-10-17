@echo off
chcp 65001 >nul
title 8/B LGS Sistemi - Bulut Dagitim Araci
echo ======================================================================
echo    8/B LGS TAKIP VE ANALIZ SISTEMINI BULUTA (STREAMLIT CLOUD) YUKLEME
echo ======================================================================
echo.
echo Bu arac yerel sistemi GitHub deponuza yukleyerek internetten
echo (telefon, akilli tahta, ev bilgisayari) erisilebilir hale getirir.
echo.
echo On Hazirlik:
echo 1. github.com adresine girip 'New repository' diyerek bos bir repo acin
echo    (Ornegin repo adi: 8b-lgs-takip).
echo 2. Olusan deponun HTTPS linkini kopyalayin.
echo.
set /p REPO_URL="GitHub Depo URL'sini buraya yapistirin: "
if "%REPO_URL%"=="" (
    echo.
    echo [HATA] Depo adresi bos birakilamaz!
    pause
    exit /b
)

cd /d "%~dp0"
if not exist "app.py" (
    cd /d "C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu"
)

echo.
echo [1/3] Git ayarlari yapilandiriliyor...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git branch -M main

echo [2/3] Guncel degisiklikler kaydediliyor...
git add .
git commit -m "Bulut guncellemesi" >nul 2>&1

echo [3/3] Kodlar GitHub'a gonderiliyor...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo   [TEBRIKLER] Kodlariniz GitHub'a basariyla aktarildi!
    echo ======================================================================
    echo.
    echo SON VE TEK ADIM (Streamlit Cloud'da Canliya Alma):
    echo 1. Tarayicinizda https://share.streamlit.io adresini acin.
    echo 2. 'Create app' butonuna basin.
    echo 3. 'Repository' kismindan actiginiz depoyu secin.
    echo 4. 'Main file path' kisminda 'app.py' yazdigindan emin olun.
    echo 5. 'Deploy!' butonuna tiklayin.
    echo.
    echo Yaklasik 1-2 dakika icinde sisteminiz internette canli ve aktif olacaktir!
    echo Ogretmen erisim PIN kodunuz: 8B2026
    echo ======================================================================
) else (
    echo.
    echo [BILGI/UYARI] Git push sirasinda GitHub kimlik dogrulamasi istenebilir.
    echo Tarayicida acilan oturum acma penceresinden GitHub hesabinizi onaylayiniz.
)

echo.
pause
