import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface CustomerData {
  customer_id: string;
  age: number;
  gender: string;
  segment: string;
  subscription_length: number;
  last_login_date: string;
  total_orders: number;
  total_spent: number;
  avg_order_value: number;
}

interface PredictionResult {
  churn_probability: number;
  confidence: number;
  prediction: string;
  prediction_id: number;
}

interface ModelInfo {
  id: number;
  version: string;
  accuracy: number;
  training_date: string;
  is_active: boolean;
  training_data_size: number;
}

const ChurnDashboard: React.FC = () => {
  const { token, logout } = useAuth();
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [predictions, setPredictions] = useState<PredictionResult[]>([]);
  const [isTraining, setIsTraining] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [customerData, setCustomerData] = useState<CustomerData>({
    customer_id: '',
    age: 0,
    gender: 'Male',
    segment: 'Premium',
    subscription_length: 365,
    last_login_date: '',
    total_orders: 0,
    total_spent: 0,
    avg_order_value: 0
  });

  // Model listesini yükle
  const loadModels = async () => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch('http://127.0.0.1:8000/api/v1/churn/models', { headers });
      if (response.ok) {
        const data = await response.json();
        setModels(data);
      }
    } catch (error) {
      console.error('Model yükleme hatası:', error);
    }
  };

  // Tahmin geçmişini yükle
  const loadPredictions = async () => {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch('http://127.0.0.1:8000/api/v1/churn/predictions', { headers });
      if (response.ok) {
        const data = await response.json();
        setPredictions(data);
      }
    } catch (error) {
      console.error('Tahmin geçmişi yükleme hatası:', error);
    }
  };

  useEffect(() => {
    loadModels();
    loadPredictions();
  }, []);

  // Model eğitimi
  const handleTrainModel = async () => {
    setIsTraining(true);
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch('http://127.0.0.1:8000/api/v1/churn/train', {
        method: 'POST',
        headers,
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Model başarıyla eğitildi!\nAccuracy: ${result.metrics?.accuracy || 'N/A'}`);
        loadModels(); // Model listesini yenile
      } else {
        const error = await response.json();
        alert(`Model eğitimi başarısız: ${error.detail}`);
      }
    } catch (error) {
      console.error('Model eğitimi hatası:', error);
      alert('Model eğitimi sırasında hata oluştu');
    } finally {
      setIsTraining(false);
    }
  };

  // Churn tahmini
  const handlePredict = async () => {
    setIsPredicting(true);
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch('http://127.0.0.1:8000/api/v1/churn/predict', {
        method: 'POST',
        headers,
        body: JSON.stringify(customerData),
      });
      
      if (response.ok) {
        const result = await response.json();
        setPredictionResult(result.prediction);
        loadPredictions(); // Tahmin geçmişini yenile
      } else {
        const error = await response.json();
        alert(`Tahmin hatası: ${error.detail}`);
      }
    } catch (error) {
      console.error('Tahmin hatası:', error);
      alert('Tahmin sırasında hata oluştu');
    } finally {
      setIsPredicting(false);
    }
  };

  const getRiskLevel = (probability: number) => {
    if (probability > 0.7) return { level: 'Yüksek', color: '#ef4444', icon: '🔴' };
    if (probability > 0.4) return { level: 'Orta', color: '#f59e0b', icon: '🟡' };
    return { level: 'Düşük', color: '#10b981', icon: '🟢' };
  };

  return (
    <div className="container">
      <div className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <h1>Churn Prediction Dashboard</h1>
            <nav className="nav">
              <Link to="/dashboard">
                Ana Dashboard
              </Link>
              <Link to="/churn" className="active">
                Churn Prediction
              </Link>
            </nav>
          </div>
        </div>
      </div>

      <div className="grid">
        {/* Model Eğitimi */}
        <div className="card">
          <h3>Model Eğitimi</h3>
          <p className="text-gray-500 mb-4">
            Müşteri verilerinizle churn modeli eğitin
          </p>
          <button
            onClick={handleTrainModel}
            disabled={isTraining}
            className={`button ${isTraining ? 'secondary' : ''}`}
            style={{ cursor: isTraining ? 'not-allowed' : 'pointer' }}
          >
            {isTraining ? 'Eğitiliyor...' : 'Model Eğit'}
          </button>
        </div>

        {/* Model Listesi */}
        <div className="card">
          <h3>Eğitilmiş Modeller</h3>
          {models.length > 0 ? (
            <div className="table">
              <table style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th>Versiyon</th>
                    <th>Accuracy</th>
                    <th>Eğitim Tarihi</th>
                    <th>Durum</th>
                    <th>Veri Boyutu</th>
                  </tr>
                </thead>
                <tbody>
                  {models.map((model, index) => (
                    <tr key={model.id || `model-${index}`}>
                      <td>v{model.version}</td>
                      <td>{(model.accuracy * 100).toFixed(1)}%</td>
                      <td>{new Date(model.training_date).toLocaleDateString('tr-TR')}</td>
                      <td>
                        <span className={`status ${model.is_active ? 'success' : 'failed'}`}>
                          {model.is_active ? 'Aktif' : 'Pasif'}
                        </span>
                      </td>
                      <td>{model.training_data_size}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center text-gray-500 p-4">
              Henüz eğitilmiş model bulunmuyor
            </div>
          )}
        </div>
      </div>

      {/* Churn Tahmini */}
      <div className="card">
        <h3>Yeni Müşteri Churn Tahmini</h3>
        <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
          <div>
            <div className="form-group">
              <label>Müşteri ID</label>
              <input
                type="text"
                value={customerData.customer_id}
                onChange={(e) => setCustomerData({...customerData, customer_id: e.target.value})}
                placeholder="CUST_001"
              />
            </div>
            
            <div className="form-group">
              <label>Yaş</label>
              <input
                type="number"
                value={customerData.age}
                onChange={(e) => setCustomerData({...customerData, age: parseInt(e.target.value) || 0})}
                placeholder="25"
              />
            </div>
            
            <div className="form-group">
              <label>Cinsiyet</label>
              <select
                value={customerData.gender}
                onChange={(e) => setCustomerData({...customerData, gender: e.target.value})}
              >
                <option value="Male">Erkek</option>
                <option value="Female">Kadın</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Segment</label>
              <select
                value={customerData.segment}
                onChange={(e) => setCustomerData({...customerData, segment: e.target.value})}
              >
                <option value="Premium">Premium</option>
                <option value="Standard">Standard</option>
                <option value="Basic">Basic</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Üyelik Süresi (gün)</label>
              <input
                type="number"
                value={customerData.subscription_length}
                onChange={(e) => setCustomerData({...customerData, subscription_length: parseInt(e.target.value) || 0})}
                placeholder="365"
              />
            </div>
          </div>
          
          <div>
            <div className="form-group">
              <label>Son Giriş Tarihi</label>
              <input
                type="date"
                value={customerData.last_login_date}
                onChange={(e) => setCustomerData({...customerData, last_login_date: e.target.value})}
              />
            </div>
            
            <div className="form-group">
              <label>Toplam Sipariş Sayısı</label>
              <input
                type="number"
                value={customerData.total_orders}
                onChange={(e) => setCustomerData({...customerData, total_orders: parseInt(e.target.value) || 0})}
                placeholder="10"
              />
            </div>
            
            <div className="form-group">
              <label>Toplam Harcama (TL)</label>
              <input
                type="number"
                value={customerData.total_spent}
                onChange={(e) => setCustomerData({...customerData, total_spent: parseFloat(e.target.value) || 0})}
                placeholder="1500"
              />
            </div>
            
            <div className="form-group">
              <label>Ortalama Sipariş Değeri (TL)</label>
              <input
                type="number"
                value={customerData.avg_order_value}
                onChange={(e) => setCustomerData({...customerData, avg_order_value: parseFloat(e.target.value) || 0})}
                placeholder="150"
              />
            </div>
            
            <button
              onClick={handlePredict}
              disabled={isPredicting}
              className={`button ${isPredicting ? 'secondary' : ''}`}
              style={{ 
                cursor: isPredicting ? 'not-allowed' : 'pointer',
                backgroundColor: '#8b5cf6',
                width: '100%'
              }}
            >
              {isPredicting ? 'Tahmin Yapılıyor...' : 'Churn Tahmini Yap'}
            </button>
          </div>
        </div>
      </div>

      {/* Tahmin Sonucu */}
      {predictionResult && (
        <div className="card">
          <h3>Tahmin Sonucu</h3>
          <div style={{ 
            padding: '20px', 
            border: '2px solid #e5e7eb', 
            borderRadius: '8px',
            backgroundColor: '#f9fafb'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
              <span style={{ fontSize: '24px' }}>
                {getRiskLevel(predictionResult.churn_probability).icon}
              </span>
              <div>
                <h4 style={{ margin: 0, fontSize: '18px' }}>
                  Churn Riski: {getRiskLevel(predictionResult.churn_probability).level}
                </h4>
                <p style={{ margin: 0, color: '#6b7280' }}>
                  Müşteri ID: {customerData.customer_id}
                </p>
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div>
                <strong>Churn Olasılığı:</strong>
                <div style={{ 
                  fontSize: '24px', 
                  fontWeight: 'bold',
                  color: getRiskLevel(predictionResult.churn_probability).color
                }}>
                  {(predictionResult.churn_probability * 100).toFixed(1)}%
                </div>
              </div>
              
              <div>
                <strong>Güven Seviyesi:</strong>
                <div style={{ fontSize: '18px', color: '#374151' }}>
                  {(predictionResult.confidence * 100).toFixed(1)}%
                </div>
              </div>
              
              <div>
                <strong>Tahmin:</strong>
                <div style={{ fontSize: '18px', color: '#374151' }}>
                  {predictionResult.prediction}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tahmin Geçmişi */}
      <div className="card">
        <h3>Son Tahminler</h3>
        {predictions.length > 0 ? (
          <div className="table">
            <table style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>Müşteri ID</th>
                  <th>Churn Riski</th>
                  <th>Olasılık</th>
                  <th>Güven</th>
                  <th>Tarih</th>
                </tr>
              </thead>
              <tbody>
                {predictions.slice(0, 10).map((pred, index) => {
                  const risk = getRiskLevel(pred.churn_probability);
                  return (
                    <tr key={pred.id || `pred-${index}`}>
                      <td>{pred.prediction_id}</td>
                      <td>
                        <span style={{ color: risk.color }}>
                          {risk.icon} {risk.level}
                        </span>
                      </td>
                      <td style={{ color: risk.color, fontWeight: 'bold' }}>
                        {(pred.churn_probability * 100).toFixed(1)}%
                      </td>
                      <td>{(pred.confidence * 100).toFixed(1)}%</td>
                      <td>{new Date().toLocaleDateString('tr-TR')}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center text-gray-500 p-4">
            Henüz tahmin yapılmamış
          </div>
        )}
      </div>
    </div>
  );
};

export default ChurnDashboard;