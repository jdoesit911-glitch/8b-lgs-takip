@echo off
chcp 65001 >nul
title 8/B LGS - GitHub Yukle
color 0A
echo.
echo ====================================================
echo   8/B LGS SISTEMI - GITHUB'A DOSYA YUKLEME ARACI
echo ====================================================
echo.
echo Bu pencere acik kalacak - lutfen kapatmayin!
echo.

:: Proje dizinine git
cd /d "C:\Users\ELRA\.gemini\antigravity\scratch\lgs_analiz_otomasyonu"

echo [1/4] Proje dizini kontrol ediliyor...
if not exist "app.py" (
    echo HATA: app.py bulunamadi! Lutfen dosyalari kontrol edin.
    pause
    exit /b
)
echo      OK - app.py bulundu.
echo.

echo [2/4] Git durumu kontrol ediliyor...
git status
echo.

echo [3/4] Degisiklikler kaydediliyor...
git add .
git commit -m "8B LGS Bulut Surumu - %date% %time%"
echo.

echo [4/4] GitHub hesabiniza (jdoesit911-glitch) gonderiliyor...
echo      -> Tarayicinizda GitHub giris penceresi acilabilir.
echo      -> Acilirsa 'Sign in with browser' butonuna basip onaylayin.
echo.
git push -u origin main
echo.

if %ERRORLEVEL% EQU 0 (
    color 0A
    echo ====================================================
    echo   BASARILI! Kodlar GitHub'a yuklendi.
    echo   Simdi Streamlit sayfasini yenileyin (F5).
    echo   Kirmizi uyarilar kaybolacak ve Deploy aktif olacak!
    echo ====================================================
) else (
    color 0C
    echo ====================================================
    echo   HATA: Yukleme tamamlanamadi.
    echo   Hata kodu: %ERRORLEVEL%
    echo.
    echo   Cozum: Tarayicinizda github.com'da oturum acik mi?
    echo   'github.com/jdoesit911-glitch' linkini tarayicida acip
    echo   giris yaptiginizdan emin olun, sonra tekrar deneyin.
    echo ====================================================
)

echo.
echo Bu pencereyi kapatmak icin herhangi bir tusa basin...
pause >nul
