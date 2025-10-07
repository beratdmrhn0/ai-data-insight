.PHONY: test test-cov test-fast test-integration test-property clean

# Varsayılan test komutu
test:
	pytest tests/ -v

# Hızlı test (max 1 hata, warning'ler gizli)
test-fast:
	pytest tests/ -v --maxfail=1 --disable-warnings

# Coverage raporu ile test
test-cov:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

# Sadece integration testler
test-integration:
	pytest tests/test_integration.py -v

# Sadece property-based testler
test-property:
	pytest tests/test_property_based.py -v

# Sadece unit testler
test-unit:
	pytest tests/test_preprocess.py tests/test_anomaly.py tests/test_forecast.py tests/test_api.py -v

# Tüm testler + coverage
test-all:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml

# Test cache temizle
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .coverage

# Test kalite kontrolü
test-quality:
	@echo "🧪 Test Kalite Kontrolü"
	@echo "========================"
	@echo "📊 Test Coverage:"
	pytest tests/ --cov=. --cov-report=term-missing --quiet
	@echo ""
	@echo "⚡ Test Hızı:"
	time pytest tests/ --maxfail=1 --disable-warnings --quiet
	@echo ""
	@echo "✅ Test Kalitesi: Tüm testler geçti!"
