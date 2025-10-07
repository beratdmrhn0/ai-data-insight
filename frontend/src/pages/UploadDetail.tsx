import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ForecastChart from "../components/ForecastChart";

export default function UploadDetail() {
  const { id } = useParams();
  const [result, setResult] = useState<any>(null);
  const [preprocessData, setPreprocessData] = useState<any>(null);

  useEffect(() => {
    // Analiz sonuçlarını al
    fetch(`http://127.0.0.1:8000/api/v1/upload/${id}/result`)
      .then((res) => res.json())
      .then((json) => {
        console.log("API Response:", json);
        console.log("Summary:", json.summary);
        console.log("Insights:", json.insights);
        setResult(json);
      });

    // Preprocessing sonuçlarını al
    fetch(`http://127.0.0.1:8000/api/v1/preprocess/${id}`, {
      method: 'POST'
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Preprocess Response:", data);
        setPreprocessData(data);
      })
      .catch((err) => {
        console.error("Preprocess Error:", err);
      });
  }, [id]);

  if (!result) return <div className="p-6">Yükleniyor...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-lg border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-8">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                      Data Insight Dashboard
                    </h1>
                    <p className="mt-1 text-gray-600 font-medium">Upload #{id} - E-ticaret Veri Analizi</p>
                  </div>
                </div>
              </div>
              <div className="hidden md:flex items-center space-x-4">
                <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  ✅ Analiz Tamamlandı
                </div>
                <div className="text-sm text-gray-500">
                  {new Date().toLocaleDateString('tr-TR')}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="group bg-white/70 backdrop-blur-sm overflow-hidden shadow-xl rounded-2xl border border-white/20 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Toplam Kayıt</p>
                    <p className="text-3xl font-bold text-gray-900">{result.summary?.rows || 0}</p>
                  </div>
                  <div className="w-14 h-14 bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <div className="group bg-white/70 backdrop-blur-sm overflow-hidden shadow-xl rounded-2xl border border-white/20 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Kolon Sayısı</p>
                    <p className="text-3xl font-bold text-gray-900">{result.summary?.columns?.length || 0}</p>
                  </div>
                  <div className="w-14 h-14 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <div className="group bg-white/70 backdrop-blur-sm overflow-hidden shadow-xl rounded-2xl border border-white/20 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Son Sipariş</p>
                    <p className="text-lg font-bold text-gray-900">
                      {result.summary?.last_order_date ? new Date(result.summary.last_order_date).toLocaleDateString('tr-TR') : 'N/A'}
                    </p>
                  </div>
                  <div className="w-14 h-14 bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <div className="group bg-white/70 backdrop-blur-sm overflow-hidden shadow-xl rounded-2xl border border-white/20 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Churn Riski</p>
                    <p className="text-3xl font-bold text-gray-900">{result.insights?.churn_at_risk_count || 0}</p>
                  </div>
                  <div className="w-14 h-14 bg-gradient-to-r from-red-500 to-red-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Insights Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Top SKUs */}
            {result.insights?.top_skus && (
              <div className="bg-white/70 backdrop-blur-sm shadow-xl rounded-2xl border border-white/20 overflow-hidden">
                <div className="bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">En Çok Satan Ürünler</h3>
                      <p className="text-amber-100 text-sm">Top 5 performans</p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {Object.entries(result.insights.top_skus).slice(0, 5).map(([sku, qty]: [string, any], index: number) => (
                      <div key={sku} className="group flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl hover:shadow-md transition-all duration-200">
                        <div className="flex items-center space-x-4">
                          <div className="relative">
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                              <span className="text-white text-sm font-bold">#{index + 1}</span>
                            </div>
                            {index === 0 && (
                              <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                                <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                </svg>
                              </div>
                            )}
                          </div>
                          <div>
                            <span className="font-semibold text-gray-900 text-lg">{sku}</span>
                            <p className="text-gray-600 text-sm">Ürün Kodu</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-2 rounded-xl text-lg font-bold shadow-lg">
                            {qty}
                          </span>
                          <p className="text-gray-600 text-sm mt-1">adet satıldı</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Churn Risk Analysis */}
            {result.insights?.churn_at_risk_count !== undefined && (
              <div className="bg-white/70 backdrop-blur-sm shadow-xl rounded-2xl border border-white/20 overflow-hidden">
                <div className="bg-gradient-to-r from-red-500 to-pink-500 px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">Müşteri Churn Analizi</h3>
                      <p className="text-red-100 text-sm">Risk değerlendirmesi</p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <div className="text-center">
                    <div className="w-24 h-24 bg-gradient-to-r from-red-100 to-pink-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-4xl font-bold text-red-600">{result.insights.churn_at_risk_count}</span>
                    </div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Risk Altındaki Müşteri</h4>
                    <p className="text-gray-600 mb-4 text-sm">Son 90 gün içinde sipariş vermemiş</p>
                    <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl p-4">
                      <div className="flex items-center space-x-2 mb-2">
                        <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-semibold text-red-800">Öneri</span>
                      </div>
                      <p className="text-sm text-red-700">
                        Pazarlama kampanyaları ve kişiselleştirilmiş teklifler ile bu müşterileri geri kazanabilirsiniz.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Anomaly Detection */}
            {result.insights?.anomalies && result.insights.anomalies.length > 0 && (
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">🔍 Anomali Tespiti</h3>
                  <div className="overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Satır</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fiyat</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {result.insights.anomalies.slice(0, 5).map((a: any, idx: number) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{a.sku}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{a.row_index + 1}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-600">₺{a.price}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {result.insights.anomalies.length > 5 && (
                      <div className="text-center mt-4">
                        <span className="text-sm text-gray-500">
                          ... ve {result.insights.anomalies.length - 5} anomali daha
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Predictions */}
            {result.insights?.predictions && result.insights.predictions.length > 0 && (
              <div className="bg-white/70 backdrop-blur-sm shadow-xl rounded-2xl border border-white/20 overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-500 to-purple-500 px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">Talep Tahminleri</h3>
                      <p className="text-indigo-100 text-sm">AI destekli öngörüler</p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    {result.insights.predictions.slice(0, 6).map((p: number, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl hover:shadow-md transition-all duration-200">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center">
                            <span className="text-white text-xs font-bold">{idx + 1}</span>
                          </div>
                          <span className="font-medium text-gray-900">Satır {idx + 1}</span>
                        </div>
                        <div className="text-right">
                          <span className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white px-3 py-1 rounded-lg text-sm font-bold">
                            {p.toFixed(1)}
                          </span>
                          <p className="text-gray-600 text-xs mt-1">adet tahmin</p>
                        </div>
                      </div>
                    ))}
                    {result.insights.predictions.length > 6 && (
                      <div className="text-center mt-4 p-3 bg-gray-50 rounded-xl">
                        <span className="text-sm text-gray-600 font-medium">
                          ... ve {result.insights.predictions.length - 6} tahmin daha
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Forecast Chart - Güncellenmiş */}
            {preprocessData?.forecast && preprocessData.forecast.length > 0 && (
              <div className="bg-white/70 backdrop-blur-sm shadow-xl rounded-2xl border border-white/20 overflow-hidden">
                <div className="bg-gradient-to-r from-green-500 to-emerald-500 px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">🔮 7 Günlük Satış Tahmini</h3>
                      <p className="text-green-100 text-sm">AI destekli gelecek tahminleri</p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Tahmin Tablosu */}
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">Günlük Tahminler</h4>
                      <div className="space-y-2">
                        {preprocessData.forecast.map((value: number, index: number) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
                            <span className="font-medium text-gray-900">Gün {index + 1}</span>
                            <span className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-3 py-1 rounded-lg text-sm font-bold">
                              {value.toFixed(1)} adet
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Tahmin Özeti */}
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">Tahmin Özeti</h4>
                      <div className="space-y-4">
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4">
                          <div className="flex items-center justify-between">
                            <span className="text-gray-700">Ortalama Günlük Tahmin</span>
                            <span className="font-bold text-blue-600">
                              {(preprocessData.forecast.reduce((a: number, b: number) => a + b, 0) / preprocessData.forecast.length).toFixed(1)} adet
                            </span>
                          </div>
                        </div>
                        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4">
                          <div className="flex items-center justify-between">
                            <span className="text-gray-700">Haftalık Toplam Tahmin</span>
                            <span className="font-bold text-purple-600">
                              {preprocessData.forecast.reduce((a: number, b: number) => a + b, 0).toFixed(1)} adet
                            </span>
                          </div>
                        </div>
                        <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-4">
                          <div className="flex items-center justify-between">
                            <span className="text-gray-700">En Yüksek Günlük Tahmin</span>
                            <span className="font-bold text-orange-600">
                              {Math.max(...preprocessData.forecast).toFixed(1)} adet
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Tahmin Detayları */}
            {preprocessData?.forecast && preprocessData.forecast.length > 0 && (
              <div className="bg-white border rounded p-4">
                <h3 className="text-lg font-semibold mb-2">Tahmin Detayları</h3>
                <p className="text-sm text-gray-600 mb-4">Aşağıda 1 haftalık tahmin sonuçlarını görüyorsunuz</p>
                <table className="w-full border border-gray-300">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border border-gray-300 px-4 py-2 text-left">Gün</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Tahmin Değeri</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preprocessData.forecast.slice(0, 7).map((forecast: number, idx: number) => (
                      <tr key={idx}>
                        <td className="border border-gray-300 px-4 py-2">Gün {idx + 1}</td>
                        <td className="border border-gray-300 px-4 py-2">{forecast.toFixed(1)} adet tahmin</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Data Summary */}
          <div className="bg-white border rounded p-4">
            <h3 className="text-lg font-semibold mb-2">Veri Seti Özeti</h3>
            <p className="text-sm text-gray-600 mb-4">Yüklenen veri dosyasının temel istatistikleri ve özellikleri</p>
            <table className="w-full border border-gray-300">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border border-gray-300 px-4 py-2 text-left">Özellik</th>
                  <th className="border border-gray-300 px-4 py-2 text-left">Değer</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-gray-300 px-4 py-2">Toplam Kayıt</td>
                  <td className="border border-gray-300 px-4 py-2">{preprocessData?.record_count || result.summary?.rows || 0}</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2">Kolon Sayısı</td>
                  <td className="border border-gray-300 px-4 py-2">{preprocessData?.column_count || result.summary?.columns?.length || 0}</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2">Tespit Edilen Anomali</td>
                  <td className="border border-gray-300 px-4 py-2">{preprocessData?.anomaly_count || result.insights?.anomalies?.length || 0}</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2">Yarın Tahmini</td>
                  <td className="border border-gray-300 px-4 py-2">
                    {preprocessData?.forecast && preprocessData.forecast.length > 0 
                      ? `${preprocessData.forecast[0].toFixed(1)} adet`
                      : 'Tahmin yapılamadı'
                    }
                  </td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2">Haftalık Toplam Tahmin</td>
                  <td className="border border-gray-300 px-4 py-2">
                    {preprocessData?.forecast && preprocessData.forecast.length > 0 
                      ? `${preprocessData.forecast.reduce((a: number, b: number) => a + b, 0).toFixed(1)} adet`
                      : 'Tahmin yapılamadı'
                    }
                  </td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-4 py-2">Ortalama Günlük Tahmin</td>
                  <td className="border border-gray-300 px-4 py-2">
                    {preprocessData?.forecast && preprocessData.forecast.length > 0 
                      ? `${(preprocessData.forecast.reduce((a: number, b: number) => a + b, 0) / preprocessData.forecast.length).toFixed(1)} adet`
                      : 'Tahmin yapılamadı'
                    }
                  </td>
                </tr>
              </tbody>
            </table>
            
            {/* Summary Stats Tablosu */}
            {preprocessData?.summary_stats && (
              <div className="mt-8">
                <h4 className="text-md font-semibold text-gray-900 mb-2 text-center">Detaylı İstatistikler</h4>
                <p className="text-sm text-gray-600 mb-4 text-center">Her kolon için sayısal istatistikler (ortalama, minimum, maksimum, standart sapma)</p>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border border-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="border px-2 py-1 text-left">Kolon</th>
                        <th className="border px-2 py-1 text-center">Count</th>
                        <th className="border px-2 py-1 text-center">Mean</th>
                        <th className="border px-2 py-1 text-center">Min</th>
                        <th className="border px-2 py-1 text-center">Max</th>
                        <th className="border px-2 py-1 text-center">Std</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.keys(preprocessData.summary_stats).map((column) => {
                        const stats = preprocessData.summary_stats[column];
                        return (
                          <tr key={column} className="hover:bg-gray-50">
                            <td className="border px-2 py-1 font-medium">{column}</td>
                            <td className="border px-2 py-1 text-center">
                              {typeof stats.count === 'number' ? stats.count.toFixed(0) : stats.count}
                            </td>
                            <td className="border px-2 py-1 text-center">
                              {typeof stats.mean === 'number' ? stats.mean.toFixed(2) : '-'}
                            </td>
                            <td className="border px-2 py-1 text-center">
                              {typeof stats.min === 'number' ? stats.min.toFixed(2) : stats.min}
                            </td>
                            <td className="border px-2 py-1 text-center">
                              {typeof stats.max === 'number' ? stats.max.toFixed(2) : stats.max}
                            </td>
                            <td className="border px-2 py-1 text-center">
                              {typeof stats.std === 'number' ? stats.std.toFixed(2) : '-'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}