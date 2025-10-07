@echo off
echo 🧪 AI Data Insight Test Suite
echo ================================

if "%1"=="fast" (
    echo ⚡ Hızlı Test Çalıştırılıyor...
    pytest tests/ -v --maxfail=1 --disable-warnings
) else if "%1"=="cov" (
    echo 📊 Coverage Test Çalıştırılıyor...
    pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
) else if "%1"=="unit" (
    echo 🔧 Unit Testler Çalıştırılıyor...
    pytest tests/test_preprocess.py tests/test_anomaly.py tests/test_forecast.py tests/test_api.py -v
) else if "%1"=="integration" (
    echo 🔗 Integration Testler Çalıştırılıyor...
    pytest tests/test_integration.py -v
) else if "%1"=="property" (
    echo 🎲 Property-Based Testler Çalıştırılıyor...
    pytest tests/test_property_based.py -v
) else if "%1"=="all" (
    echo 🚀 Tüm Testler + Coverage Çalıştırılıyor...
    pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
) else if "%1"=="clean" (
    echo 🧹 Test Cache Temizleniyor...
    rmdir /s /q .pytest_cache 2>nul
    rmdir /s /q htmlcov 2>nul
    del coverage.xml 2>nul
    del .coverage 2>nul
    echo ✅ Temizlik tamamlandı!
) else (
    echo 📋 Kullanım:
    echo   test.bat fast        - Hızlı test
    echo   test.bat cov         - Coverage ile test
    echo   test.bat unit        - Unit testler
    echo   test.bat integration - Integration testler
    echo   test.bat property    - Property-based testler
    echo   test.bat all         - Tüm testler + coverage
    echo   test.bat clean       - Cache temizle
    echo.
    echo 🔧 Varsayılan test çalıştırılıyor...
    pytest tests/ -v
)

if %ERRORLEVEL% EQU 0 (
    echo ✅ Testler başarılı!
) else (
    echo ❌ Testler başarısız!
    exit /b 1
)
