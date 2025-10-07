import React from "react";

interface SummaryCardsProps {
  recordCount: number;
  columnCount: number;
  anomalyCount: number;
  forecast: number[];
}

const SummaryCards: React.FC<SummaryCardsProps> = ({ 
  recordCount, 
  columnCount, 
  anomalyCount, 
  forecast 
}) => {
  const tomorrowForecast = forecast?.length > 0 ? forecast[0].toFixed(0) : "-";

  const cards = [
    { 
      title: "Toplam Kayıt", 
      value: recordCount.toLocaleString(), 
      color: "bg-blue-100 text-blue-800",
      icon: "📊"
    },
    { 
      title: "Kolon Sayısı", 
      value: columnCount, 
      color: "bg-green-100 text-green-800",
      icon: "📋"
    },
    { 
      title: "Anomali Sayısı", 
      value: anomalyCount, 
      color: "bg-red-100 text-red-800",
      icon: "⚠️"
    },
    { 
      title: "Yarın Tahmini", 
      value: tomorrowForecast, 
      color: "bg-purple-100 text-purple-800",
      icon: "🔮"
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <div key={index} className={`p-6 rounded-2xl shadow-md ${card.color} hover:shadow-lg transition-shadow`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium opacity-80">{card.title}</h3>
              <p className="text-2xl font-bold mt-2">{card.value}</p>
            </div>
            <div className="text-3xl">
              {card.icon}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SummaryCards;
