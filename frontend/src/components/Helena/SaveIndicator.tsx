import React from "react";

interface SaveIndicatorProps {
  status: "salvando" | "salvo" | "erro" | "idle";
  ultimoSalvamento?: Date;
}

const SaveIndicator: React.FC<SaveIndicatorProps> = ({ status, ultimoSalvamento }) => {
  const formatarTempo = (data: Date) => {
    const agora = new Date();
    const diff = Math.floor((agora.getTime() - data.getTime()) / 1000);

    if (diff < 5) return "agora mesmo";
    if (diff < 60) return `há ${diff}s`;
    if (diff < 3600) return `há ${Math.floor(diff / 60)}min`;
    return data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  };

  const getStatusConfig = () => {
    switch (status) {
      case "salvando":
        return {
          icon: "⏳",
          text: "Salvando...",
          color: "#3b82f6",
          bgColor: "#eff6ff",
        };
      case "salvo":
        return {
          icon: "✓",
          text: ultimoSalvamento ? `Salvo ${formatarTempo(ultimoSalvamento)}` : "Salvo",
          color: "#10b981",
          bgColor: "#f0fdf4",
        };
      case "erro":
        return {
          icon: "⚠",
          text: "Erro ao salvar",
          color: "#ef4444",
          bgColor: "#fef2f2",
        };
      default:
        return null;
    }
  };

  const config = getStatusConfig();

  if (!config) return null;

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        padding: "4px 12px",
        borderRadius: "12px",
        backgroundColor: config.bgColor,
        color: config.color,
        fontSize: "13px",
        fontWeight: 500,
        transition: "all 0.3s ease",
        border: `1px solid ${config.color}20`,
      }}
    >
      <span
        style={{
          fontSize: "14px",
          animation: status === "salvando" ? "pulse 1.5s ease-in-out infinite" : "none",
        }}
      >
        {config.icon}
      </span>
      <span>{config.text}</span>
      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.95); }
          }
        `}
      </style>
    </div>
  );
};

export default SaveIndicator;
