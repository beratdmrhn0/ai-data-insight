# AI Data Insight Test Suite - PowerShell Version
param(
    [string]$Command = "default"
)

Write-Host "🧪 AI Data Insight Test Suite" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

switch ($Command.ToLower()) {
    "fast" {
        Write-Host "⚡ Hızlı Test Çalıştırılıyor..." -ForegroundColor Yellow
        pytest tests/ -v --maxfail=1 --disable-warnings
    }
    "cov" {
        Write-Host "📊 Coverage Test Çalıştırılıyor..." -ForegroundColor Yellow
        pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
    }
    "unit" {
        Write-Host "🔧 Unit Testler Çalıştırılıyor..." -ForegroundColor Yellow
        pytest tests/test_preprocess.py tests/test_anomaly.py tests/test_forecast.py tests/test_api.py -v
    }
    "integration" {
        Write-Host "🔗 Integration Testler Çalıştırılıyor..." -ForegroundColor Yellow
        pytest tests/test_integration.py -v
    }
    "property" {
        Write-Host "🎲 Property-Based Testler Çalıştırılıyor..." -ForegroundColor Yellow
        pytest tests/test_property_based.py -v
    }
    "all" {
        Write-Host "🚀 Tüm Testler + Coverage Çalıştırılıyor..." -ForegroundColor Yellow
        pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
    }
    "clean" {
        Write-Host "🧹 Test Cache Temizleniyor..." -ForegroundColor Yellow
        if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
        if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
        if (Test-Path "coverage.xml") { Remove-Item -Force "coverage.xml" }
        if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
        Write-Host "✅ Temizlik tamamlandı!" -ForegroundColor Green
        return
    }
    "help" {
        Write-Host "📋 Kullanım:" -ForegroundColor Green
        Write-Host "  .\test.ps1 fast        - Hızlı test" -ForegroundColor White
        Write-Host "  .\test.ps1 cov         - Coverage ile test" -ForegroundColor White
        Write-Host "  .\test.ps1 unit        - Unit testler" -ForegroundColor White
        Write-Host "  .\test.ps1 integration - Integration testler" -ForegroundColor White
        Write-Host "  .\test.ps1 property    - Property-based testler" -ForegroundColor White
        Write-Host "  .\test.ps1 all         - Tüm testler + coverage" -ForegroundColor White
        Write-Host "  .\test.ps1 clean       - Cache temizle" -ForegroundColor White
        Write-Host "  .\test.ps1 help        - Bu yardım" -ForegroundColor White
        return
    }
    default {
        Write-Host "🔧 Varsayılan test çalıştırılıyor..." -ForegroundColor Yellow
        pytest tests/ -v
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Testler başarılı!" -ForegroundColor Green
} else {
    Write-Host "❌ Testler başarısız!" -ForegroundColor Red
    exit 1
}
