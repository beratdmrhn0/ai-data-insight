import React, { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";

interface ForecastChartProps {
  uploadId: number;
}

const ForecastChart: React.FC<ForecastChartProps> = ({ uploadId }) => {
  const { token } = useAuth();
  const [forecast, setForecast] = useState<number[]>([]);
  const [anomalyCount, setAnomalyCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const headers: HeadersInit = {
      "Accept": "application/json",
      "Content-Type": "application/json"
    };
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    fetch(`http://127.0.0.1:8000/api/v1/preprocess/${uploadId}`, {
      method: "POST",
      headers
    })
      .then(res => res.json())
      .then(data => {
        setForecast(data.forecast || []);
        setAnomalyCount(data.anomaly_count || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [uploadId]);

  if (loading) {
    return (
      <div className="bg-white p-4 rounded-2xl shadow-md">
        <h2 className="text-xl font-semibold mb-2">Satış Tahmini</h2>
        <div className="h-48 flex items-center justify-center">
          <div className="text-gray-500">Yükleniyor...</div>
        </div>
      </div>
    );
  }

  if (!forecast || forecast.length === 0) {
    return (
      <div className="bg-white p-4 rounded-2xl shadow-md">
        <h2 className="text-xl font-semibold mb-2">Satış Tahmini</h2>
        <div className="h-48 flex items-center justify-center">
          <div className="text-gray-500">Tahmin verisi bulunamadı</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border rounded p-4">
      <h2 className="text-lg font-semibold mb-2">Satış Tahmini</h2>
      <p className="text-sm text-gray-600 mb-4">Doğrusal regresyon modeli ile gelecek 7 gün için satış adet tahminleri</p>
      <table className="w-full border border-gray-300">
        <thead className="bg-gray-100">
          <tr>
            <th className="border border-gray-300 px-4 py-2 text-left">Gün</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Tahmin</th>
          </tr>
        </thead>
        <tbody>
          {forecast.map((value, index) => (
            <tr key={index}>
              <td className="border border-gray-300 px-4 py-2">Gün {index + 1}</td>
              <td className="border border-gray-300 px-4 py-2">{value.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {anomalyCount > 0 && (
        <div className="mt-4 text-sm text-red-600">
          Anomali sayısı: {anomalyCount}
        </div>
      )}
    </div>
  );
};

export default ForecastChart;
