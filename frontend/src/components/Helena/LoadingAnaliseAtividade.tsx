import React, { useState, useEffect } from 'react';

interface LoadingAnaliseAtividadeProps {
  descricao?: string;
}

const LoadingAnaliseAtividade: React.FC<LoadingAnaliseAtividadeProps> = ({ descricao }) => {
  const [stepAtual, setStepAtual] = useState(0);

  const steps = [
    { emoji: '⏳', texto: 'Lendo sua descrição...' },
    { emoji: '🔍', texto: 'Buscando atividades similares no banco de dados...' },
    { emoji: '📊', texto: 'Analisando 1.247 atividades da DECIPEX...' },
    { emoji: '🤖', texto: 'Aplicando inteligência artificial para encontrar o melhor match...' },
    { emoji: '✨', texto: 'Preparando sugestão personalizada...' }
  ];

  useEffect(() => {
    console.log('🎬 LoadingAnaliseAtividade montado!');

    // Avançar step a cada 5 segundos (total ~25s)
    const interval = setInterval(() => {
      setStepAtual((prev) => {
        const proximo = prev < steps.length - 1 ? prev + 1 : prev;
        console.log(`📊 Step: ${prev} → ${proximo}`);
        return proximo;
      });
    }, 5000); // 5 segundos por step

    return () => {
      console.log('🛑 LoadingAnaliseAtividade desmontado');
      clearInterval(interval);
    };
  }, [steps.length]);

  return (
    <div className="loading-analise-container">
      <div className="loading-header">
        <div className="loading-spinner"></div>
        <h3>Analisando sua atividade...</h3>
      </div>

      {descricao && (
        <div className="loading-descricao">
          <strong>Sua descrição:</strong> "{descricao}"
        </div>
      )}

      <div className="loading-steps">
        {steps.map((step, index) => (
          <div
            key={index}
            className={`loading-step ${
              index < stepAtual ? 'completed' :
              index === stepAtual ? 'active' :
              'pending'
            }`}
          >
            <div className="step-icon">
              {index < stepAtual ? '✅' : step.emoji}
            </div>
            <div className="step-texto">{step.texto}</div>
          </div>
        ))}
      </div>

      <div className="loading-footer">
        Isso pode levar até 30 segundos. Aguarde, estou trabalhando! 💪
      </div>

      <style>{`
        .loading-analise-container {
          padding: 24px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 12px;
          color: white;
          max-width: 600px;
          margin: 20px auto;
          box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }

        .loading-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 20px;
          padding-bottom: 16px;
          border-bottom: 2px solid rgba(255,255,255,0.3);
        }

        .loading-header h3 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
        }

        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid rgba(255,255,255,0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .loading-descricao {
          background: rgba(255,255,255,0.15);
          padding: 12px;
          border-radius: 8px;
          margin-bottom: 24px;
          font-size: 14px;
          line-height: 1.5;
        }

        .loading-descricao strong {
          display: block;
          margin-bottom: 6px;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .loading-steps {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 20px;
        }

        .loading-step {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          border-radius: 8px;
          background: rgba(255,255,255,0.1);
          transition: all 0.3s ease;
        }

        .loading-step.completed {
          background: rgba(76, 175, 80, 0.3);
        }

        .loading-step.active {
          background: rgba(255,255,255,0.25);
          animation: pulse 1.5s ease-in-out infinite;
        }

        .loading-step.pending {
          opacity: 0.5;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.02); }
        }

        .step-icon {
          font-size: 24px;
          min-width: 32px;
          text-align: center;
        }

        .step-texto {
          flex: 1;
          font-size: 15px;
          font-weight: 500;
        }

        .loading-footer {
          text-align: center;
          font-size: 13px;
          padding: 12px;
          background: rgba(255,255,255,0.1);
          border-radius: 8px;
          font-style: italic;
        }
      `}</style>
    </div>
  );
};

export default LoadingAnaliseAtividade;
