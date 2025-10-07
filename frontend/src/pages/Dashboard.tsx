import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import ForecastChart from "../components/ForecastChart";
import SummaryCards from "../components/SummaryCards";
import { useAuth } from "../contexts/AuthContext";

// Backend -> UI status eşlemesi:
// pipeline_history.status: "started" | "completed" | "failed"
// UI'da: Running | Success | Failed
const STATUS_MAP: Record<string, "Running" | "Success" | "Failed" | "Other"> = {
  started: "Running",
  completed: "Success",
  failed: "Failed",
};

type HistoryItem = {
  upload_id: number;
  status: string;       // started | completed | failed
  created_at: string;   // "2025-10-01 13:45:41.632457"
  message?: string | null;
};

// Renkler (pie/line için)
const COLORS = {
  Success: "#4CAF50",
  Failed: "#F44336",
  Running: "#FFC107",
};

// Yardımcı: "YYYY-MM-DD" formuna indir
function toDay(dateStr: string): string {
  // "2025-10-01 13:45:41.632457" -> "2025-10-01"
  return dateStr?.slice(0, 10);
}

export default function Dashboard() {
  const { token, logout } = useAuth();
  const [raw, setRaw] = useState<HistoryItem[]>([]);
  const [statusFilter, setStatusFilter] = useState<"all" | "Success" | "Failed" | "Running">("all");
  const [days, setDays] = useState<number>(30); // Son X gün görünümü
  const [uploading, setUploading] = useState(false);
  const [summaryData, setSummaryData] = useState<any>(null);

  const fetchData = () => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    fetch("http://127.0.0.1:8000/api/v1/pipeline/history", { headers })
      .then((res) => res.json())
      .then((json) => {
        console.log("Raw API Data:", json);
        setRaw(json);
        
        // En son upload'ın verilerini çek
        if (json && json.length > 0) {
          const latestUpload = json[0];
          const headers: HeadersInit = {
            'Content-Type': 'application/json',
          };
          
          if (token) {
            headers['Authorization'] = `Bearer ${token}`;
          }
          
          fetch(`http://127.0.0.1:8000/api/v1/preprocess/${latestUpload.upload_id}`, {
            method: 'POST',
            headers
          })
            .then(res => res.json())
            .then(data => {
              console.log("Summary data:", data);
              setSummaryData(data);
            })
            .catch(err => console.error("Summary fetch error:", err));
        }
      })
      .catch((err) => console.error("Fetch error:", err));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    const headers: HeadersInit = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    fetch('http://127.0.0.1:8000/api/v1/upload', {
      method: 'POST',
      headers,
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      console.log('Upload successful:', data);
      // Upload başarılı olduktan sonra verileri yenile
      setTimeout(() => {
        fetchData();
      }, 2000);
    })
    .catch(error => {
      console.error('Upload error:', error);
    })
    .finally(() => {
      setUploading(false);
      // Input'u temizle
      event.target.value = '';
    });
  };

  // Backend status -> UI status dönüşümü ve gün filtreleme
  const filtered = useMemo(() => {
    const today = new Date();
    const cutoff = new Date(today);
    cutoff.setDate(today.getDate() - days);

    // API response'unun array olup olmadığını kontrol et
    if (!Array.isArray(raw)) {
      return [];
    }

    const result = raw
      .map((r) => ({
        ...r,
        uiStatus: STATUS_MAP[r.status] ?? "Other",
        day: toDay(r.created_at),
        createdAtDate: new Date(r.created_at.replace(" ", "T")), // Safari uyumu için
      }))
      .filter((r) => {
        const inRange = r.createdAtDate >= cutoff;
        const statusMatch = statusFilter === "all" || r.uiStatus === statusFilter;
        return inRange && statusMatch;
      });

    console.log("Filtered Data:", result);
    console.log("Cutoff Date:", cutoff);
    console.log("Days Filter:", days);

    return result;
  }, [raw, statusFilter, days]);

  // Pie chart datası (filtrelenmiş kümeye göre)
  const pieData = useMemo(() => {
    const counts = { Success: 0, Failed: 0, Running: 0 };
    filtered.forEach((r) => {
      if (r.uiStatus === "Success") counts.Success++;
      else if (r.uiStatus === "Failed") counts.Failed++;
      else if (r.uiStatus === "Running") counts.Running++;
    });
    return [
      { name: "Success", value: counts.Success },
      { name: "Failed", value: counts.Failed },
      { name: "Running", value: counts.Running },
    ];
  }, [filtered]);

  // Line chart (zaman serisi): gün bazlı Running/Failed/Success sayıları
  const lineData = useMemo(() => {
    // Gün -> { day, Success, Failed, Running }
    const map: Record<string, { day: string; Success: number; Failed: number; Running: number }> = {};
    filtered.forEach((r) => {
      if (!r.day) return;
      if (!map[r.day]) map[r.day] = { day: r.day, Success: 0, Failed: 0, Running: 0 };
      if (r.uiStatus === "Success") map[r.day].Success += 1;
      if (r.uiStatus === "Failed") map[r.day].Failed += 1;
      if (r.uiStatus === "Running") map[r.day].Running += 1;
    });
    // Tarihe göre sırala
    return Object.values(map).sort((a, b) => (a.day < b.day ? -1 : 1));
  }, [filtered]);

  return (
    <div className="container">
      <div className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <h1>Dashboard</h1>
            <nav className="nav">
              <Link to="/dashboard" className="active">
                Ana Dashboard
              </Link>
              <Link to="/churn">
                Churn Prediction
              </Link>
            </nav>
          </div>
          <div className="flex" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={logout}
              style={{
                padding: '8px 16px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Çıkış
            </button>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className={`button ${uploading ? 'secondary' : ''}`}
              style={{ cursor: uploading ? 'not-allowed' : 'pointer' }}
            >
              {uploading ? 'Yükleniyor...' : 'CSV Dosya Yükle'}
            </label>
            <button
              onClick={fetchData}
              className="button"
              style={{ backgroundColor: '#10b981' }}
            >
              Yenile
            </button>
          </div>
        </div>
      </div>

      {/* Filtreler */}
      <div className="card">
        <div className="flex" style={{ gap: '16px', alignItems: 'center' }}>
          <div className="form-group" style={{ margin: 0, minWidth: '200px' }}>
            <label>Durum:</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
            >
              <option value="all">Tümü</option>
              <option value="Success">Success</option>
              <option value="Failed">Failed</option>
              <option value="Running">Running</option>
            </select>
          </div>
          
          <div className="form-group" style={{ margin: 0, minWidth: '200px' }}>
            <label>Zaman penceresi:</label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
            >
              <option value={7}>Son 7 gün</option>
              <option value={30}>Son 30 gün</option>
              <option value={90}>Son 90 gün</option>
              <option value={365}>Son 1 yıl</option>
            </select>
          </div>
          
          <div className="text-gray-500">
            Toplam kayıt: {filtered.length}
          </div>
        </div>
      </div>

      <div className="grid">
        {/* Durum Dağılımı */}
        <div className="card">
          <h3>Durum Dağılımı</h3>
          <p className="text-gray-500 mb-4">
            Pipeline'ların başarı, başarısızlık ve çalışma durumlarının dağılımı
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
            {pieData.map((item) => (
              <div key={item.name} className="text-center">
                <div 
                  className="status"
                  style={{ 
                    backgroundColor: COLORS[item.name as keyof typeof COLORS],
                    color: 'white',
                    fontSize: '14px',
                    padding: '8px 12px'
                  }}
                >
                  {item.name} {item.value}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Zaman Serisi */}
        <div className="card">
          <h3>Zaman Serisi</h3>
          <p className="text-gray-500 mb-4">
            Günlere göre pipeline çalıştırma sayıları ve durum dağılımları
          </p>
          
          {lineData.length > 0 ? (
            <div className="table">
              <table style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th>Tarih</th>
                    <th>Success</th>
                    <th>Failed</th>
                    <th>Running</th>
                  </tr>
                </thead>
                <tbody>
                  {lineData.map((item) => (
                    <tr key={item.day}>
                      <td>{item.day}</td>
                      <td className="status success">{item.Success}</td>
                      <td className="status failed">{item.Failed}</td>
                      <td className="status running">{item.Running}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center text-gray-500 p-4">
              Veri bulunamadı
            </div>
          )}
        </div>
      </div>


      {/* Upload Listesi */}
      <div className="card">
        <h3>Upload Listesi</h3>
        <p className="text-gray-500 mb-4">
          Yüklenen dosyaların işlem durumları ve detay sayfalarına erişim
        </p>
        
        {filtered.length > 0 ? (
          <div className="table">
            <table style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Durum</th>
                  <th>Tarih</th>
                  <th>Mesaj</th>
                  <th>Aksiyon</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((item, index) => (
                  <tr key={`${item.upload_id}-${index}`}>
                    <td>{item.upload_id}</td>
                    <td>
                      <span className={`status ${item.uiStatus.toLowerCase()}`}>
                        {item.uiStatus}
                      </span>
                    </td>
                    <td>{item.created_at}</td>
                    <td>{item.message || '-'}</td>
                    <td>
                      <Link 
                        to={`/upload/${item.upload_id}`}
                        className="button"
                        style={{ 
                          padding: '4px 8px', 
                          fontSize: '12px',
                          backgroundColor: '#007bff',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          textDecoration: 'none',
                          display: 'inline-block'
                        }}
                      >
                        Tahmin Göster
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center text-gray-500 p-4">
            Henüz upload bulunmuyor
          </div>
        )}
      </div>
    </div>
  );
}