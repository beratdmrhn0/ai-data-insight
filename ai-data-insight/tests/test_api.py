import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from main import app


class TestAPI:
    """API endpoint'lerinin testleri"""
    
    @pytest.fixture
    def client(self):
        """Test client oluşturur"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_csv_file(self):
        """Test için CSV dosyası oluşturur"""
        content = """sku,quantity,price,customer_id,order_date
A,10,100.0,C1,2023-01-01
B,20,200.0,C2,2023-01-02
C,30,300.0,C3,2023-01-03"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_root_endpoint(self, client):
        """Root endpoint testi"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data
    
    def test_upload_csv_success(self, client, sample_csv_file):
        """CSV upload başarılı testi"""
        try:
            with open(sample_csv_file, 'rb') as f:
                files = {'file': ('test.csv', f, 'text/csv')}
                response = client.post("/api/v1/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "upload_id" in data
            assert "status" in data
            assert data["status"] == "uploaded"
            
        finally:
            os.unlink(sample_csv_file)
    
    def test_upload_non_csv_file(self, client):
        """Non-CSV dosya upload testi"""
        content = "This is not a CSV file"
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(content)
        temp_file.close()
        
        try:
            with open(temp_file.name, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                response = client.post("/api/v1/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "CSV kabul ediliyor" in data["error"]
            
        finally:
            os.unlink(temp_file.name)
    
    def test_upload_no_file(self, client):
        """Dosya olmadan upload testi"""
        response = client.post("/api/v1/upload")
        assert response.status_code == 422  # Validation error
    
    def test_pipeline_history_endpoint(self, client):
        """Pipeline history endpoint testi"""
        response = client.get("/api/v1/pipeline/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Her item'da gerekli alanlar olmalı
        if len(data) > 0:
            item = data[0]
            required_fields = ["upload_id", "status", "created_at"]
            for field in required_fields:
                assert field in item
    
    def test_preprocess_endpoint_invalid_id(self, client):
        """Geçersiz upload ID ile preprocess testi"""
        response = client.post("/api/v1/preprocess/99999")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "bulunamadı" in data["error"]
    
    def test_upload_status_endpoint(self, client):
        """Upload status endpoint testi"""
        # Önce bir upload yap
        sample_csv = """sku,quantity,price
A,10,100.0
B,20,200.0"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(sample_csv)
        temp_file.close()
        
        try:
            with open(temp_file.name, 'rb') as f:
                files = {'file': ('test.csv', f, 'text/csv')}
                upload_response = client.post("/api/v1/upload", files=files)
            
            upload_data = upload_response.json()
            upload_id = upload_data["upload_id"]
            
            # Status kontrolü
            response = client.get(f"/api/v1/upload/{upload_id}/status")
            assert response.status_code == 200
            data = response.json()
            assert "upload_id" in data
            assert "status" in data
            assert "filename" in data
            assert data["upload_id"] == upload_id
            
        finally:
            os.unlink(temp_file.name)
    
    def test_upload_status_invalid_id(self, client):
        """Geçersiz upload ID ile status testi"""
        response = client.get("/api/v1/upload/99999/status")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "bulunamadı" in data["error"]
    
    def test_predict_endpoint_no_model(self, client):
        """Model olmadan predict endpoint testi"""
        sample_csv = """sku,quantity,price
A,10,100.0"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(sample_csv)
        temp_file.close()
        
        try:
            with open(temp_file.name, 'rb') as f:
                files = {'file': ('test.csv', f, 'text/csv')}
                response = client.post("/api/v1/predict", files=files)
            
            # Endpoint çalışmalı (model varsa prediction, yoksa error)
            assert response.status_code == 200
            data = response.json()
            # Ya prediction ya da error olmalı
            assert ("predictions" in data) or ("error" in data)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_cors_headers(self, client):
        """CORS header'ları testi"""
        response = client.options("/")
        # CORS preflight request'i test et
        assert response.status_code in [200, 405]  # 405 da kabul edilebilir
    
    def test_response_content_type(self, client):
        """Response content type testi"""
        response = client.get("/api/v1/pipeline/history")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
