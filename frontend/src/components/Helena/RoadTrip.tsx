import React from 'react';

/**
 * RoadTrip — Carro animado na estrada representando progresso
 * Animação simples e leve sem dependências extras
 */

interface RoadTripProps {
  onContinue?: () => void;
}

const RoadTrip: React.FC<RoadTripProps> = ({ onContinue }) => {
  return (
    <div className="roadtrip-container" onClick={onContinue} style={{ cursor: onContinue ? 'pointer' : 'default' }}>
      {/* Céu/Horizonte */}
      <div className="roadtrip-sky" />

      {/* Estrada */}
      <div className="roadtrip-road">
        {/* Faixa pontilhada central */}
        <div className="roadtrip-lane" />
      </div>

      {/* Gramado */}
      <div className="roadtrip-grass" />

      {/* Carro animado */}
      <div className="roadtrip-car">
        <svg width="120" height="60" viewBox="0 0 120 60" fill="none">
          {/* Carroceria */}
          <rect x="12" y="18" width="84" height="20" rx="6" fill="#0EA5E9" />
          <path d="M39 18 L57 8 H87 C91 8 94 11 94 15 V18 H39Z" fill="#0284C7" />
          {/* Janela */}
          <path d="M47 16 L59 10 H85 C87 10 89 12 89 14 V16 H47Z" fill="#E0F2FE" />

          {/* Roda traseira */}
          <g className="roadtrip-wheel">
            <circle cx="36" cy="42" r="8" fill="#1F2937" />
            <circle cx="36" cy="42" r="4" fill="#4B5563" />
          </g>

          {/* Roda dianteira */}
          <g className="roadtrip-wheel">
            <circle cx="84" cy="42" r="8" fill="#1F2937" />
            <circle cx="84" cy="42" r="4" fill="#4B5563" />
          </g>

          {/* Farol */}
          <circle cx="24" cy="26" r="2.5" fill="#FDE68A" />
        </svg>
      </div>

      {/* Placas na beira da estrada */}
      <div className="roadtrip-signs">
        <div className="roadtrip-sign">📍</div>
        <div className="roadtrip-sign">🗺️</div>
        <div className="roadtrip-sign">🚦</div>
      </div>

      {/* Texto motivacional */}
      <div className="roadtrip-message">
        ✅ Normas mapeadas!<br />
        Estrada segura por aqui.
        {onContinue && (
          <div className="roadtrip-cta">
            👉 Clique para continuar
          </div>
        )}
      </div>

      <style>{`
        .roadtrip-container {
          position: relative;
          width: 100%;
          height: 280px;
          margin: 20px 0;
          overflow: hidden;
          border-radius: 12px;
          background: linear-gradient(to bottom, #87CEEB 0%, #E0F2FE 100%);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .roadtrip-sky {
          position: absolute;
          inset: 0;
          height: 50%;
          background: linear-gradient(to bottom, rgba(135,206,235,0.4) 0%, transparent 100%);
        }

        .roadtrip-road {
          position: absolute;
          bottom: 50px;
          left: -20%;
          right: -20%;
          height: 80px;
          background: linear-gradient(to bottom, #444 0%, #333 100%);
          border-radius: 50px;
          box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }

        .roadtrip-lane {
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          height: 4px;
          transform: translateY(-50%);
          background: repeating-linear-gradient(
            to right,
            white 0,
            white 40px,
            transparent 40px,
            transparent 80px
          );
          animation: roadtrip-dash 2s linear infinite;
        }

        @keyframes roadtrip-dash {
          from { background-position: 0 0; }
          to { background-position: 80px 0; }
        }

        .roadtrip-grass {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 50px;
          background: linear-gradient(to bottom, #22c55e 0%, #16a34a 100%);
        }

        .roadtrip-car {
          position: absolute;
          bottom: 58px;
          left: -120px;
          animation: roadtrip-drive 8s linear infinite;
          filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
          transform: scaleX(-1);
        }

        @keyframes roadtrip-drive {
          from { left: -120px; }
          to { left: 110%; }
        }

        .roadtrip-wheel {
          transform-box: fill-box;
          transform-origin: 50% 50%;
          animation: roadtrip-spin 0.6s linear infinite;
        }

        @keyframes roadtrip-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .roadtrip-signs {
          position: absolute;
          right: 40px;
          bottom: 140px;
          display: flex;
          flex-direction: column;
          gap: 20px;
          opacity: 0.4;
        }

        .roadtrip-sign {
          font-size: 32px;
          animation: roadtrip-bounce 2s ease-in-out infinite;
        }

        .roadtrip-sign:nth-child(2) {
          animation-delay: 0.3s;
        }

        .roadtrip-sign:nth-child(3) {
          animation-delay: 0.6s;
        }

        @keyframes roadtrip-bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }

        .roadtrip-message {
          position: absolute;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(255,255,255,0.95);
          padding: 16px 28px;
          border-radius: 12px;
          font-weight: 600;
          color: #1351B4;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          backdrop-filter: blur(8px);
          text-align: center;
          border: 2px solid rgba(19, 81, 180, 0.2);
          transition: all 0.3s ease;
        }

        .roadtrip-container:hover .roadtrip-message {
          transform: translateX(-50%) scale(1.05);
          box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        }

        .roadtrip-cta {
          margin-top: 8px;
          font-size: 14px;
          color: #059669;
          font-weight: 600;
          animation: roadtrip-pulse 1.5s ease-in-out infinite;
        }

        @keyframes roadtrip-pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
      `}</style>
    </div>
  );
};

export default RoadTrip;
