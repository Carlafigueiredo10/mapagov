import React, { useState } from 'react';

interface InterfaceCaixinhaReconhecimentoProps {
  dados?: {
    nome_usuario?: string;
  };
  onConfirm: (resposta: string) => void;
}

const InterfaceCaixinhaReconhecimento: React.FC<InterfaceCaixinhaReconhecimentoProps> = ({ dados, onConfirm }) => {
  const [mostrarConfetes, setMostrarConfetes] = useState(false);
  const [caixaAberta, setCaixaAberta] = useState(false);

  const handleClickCaixinha = () => {
    setCaixaAberta(true);
    setMostrarConfetes(true);

    // Confetes duram 3 segundos
    setTimeout(() => {
      setMostrarConfetes(false);
    }, 3000);

    // Aguarda 2 segundos e chama onConfirm
    setTimeout(() => {
      onConfirm('continuar');
    }, 2000);
  };

  return (
    <div className="interface-container fade-in">
      <div className="caixinha-container">
        {!caixaAberta ? (
          <div className="caixinha" onClick={handleClickCaixinha}>
            <div className="caixinha-tampa">🎁</div>
            <div className="caixinha-corpo"></div>
            <div className="caixinha-label">Clique aqui!</div>
          </div>
        ) : (
          <div className="trofeu-container">
            <div className="trofeu">🏆</div>
            <div className="trofeu-label">Parabéns!</div>
          </div>
        )}

        {mostrarConfetes && (
          <div className="confetes-container">
            {[...Array(50)].map((_, i) => (
              <div
                key={i}
                className="confete"
                style={{
                  left: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 0.5}s`,
                  background: ['#ff6b6b', '#4ecdc4', '#ffe66d', '#a8e6cf', '#ffd93d'][Math.floor(Math.random() * 5)]
                }}
              />
            ))}
          </div>
        )}
      </div>

      <style>{`
        .caixinha-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 3rem 1rem;
          position: relative;
          min-height: 300px;
        }

        .caixinha {
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center;
          transition: transform 0.3s ease;
          animation: pulse 2s ease-in-out infinite;
        }

        .caixinha:hover {
          transform: scale(1.1);
        }

        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
        }

        .caixinha-tampa {
          font-size: 5rem;
          filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
          animation: bounce 1s ease-in-out infinite;
        }

        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        .caixinha-label {
          margin-top: 1rem;
          font-size: 1.2rem;
          font-weight: 600;
          color: #667eea;
          animation: fadeInOut 2s ease-in-out infinite;
        }

        @keyframes fadeInOut {
          0%, 100% {
            opacity: 0.7;
          }
          50% {
            opacity: 1;
          }
        }

        .trofeu-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          animation: aparecer 0.5s ease-out;
        }

        @keyframes aparecer {
          from {
            opacity: 0;
            transform: scale(0.5) translateY(50px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }

        .trofeu {
          font-size: 8rem;
          animation: girar 1s ease-out;
          filter: drop-shadow(0 8px 16px rgba(255, 215, 0, 0.4));
        }

        @keyframes girar {
          0% {
            transform: rotate(-180deg) scale(0);
          }
          50% {
            transform: rotate(20deg) scale(1.2);
          }
          100% {
            transform: rotate(0deg) scale(1);
          }
        }

        .trofeu-label {
          margin-top: 1rem;
          font-size: 1.5rem;
          font-weight: 700;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .confetes-container {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          overflow: hidden;
        }

        .confete {
          position: absolute;
          width: 10px;
          height: 10px;
          top: -10px;
          opacity: 0;
          animation: cair 3s linear forwards;
        }

        @keyframes cair {
          0% {
            top: -10px;
            opacity: 1;
            transform: rotate(0deg);
          }
          100% {
            top: 100%;
            opacity: 0;
            transform: rotate(720deg);
          }
        }
      `}</style>
    </div>
  );
};

export default InterfaceCaixinhaReconhecimento;
