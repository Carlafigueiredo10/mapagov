import React, { useState } from 'react';
import { useChatStore } from '../../store/chatStore';

interface Sugestao {
  macroprocesso: string;
  processo: string;
  subprocesso: string;
  atividade: string;
  codigo_sugerido?: string;
  resultado_final?: string;
  justificativa?: string;
}

interface InterfaceConfirmacaoArquiteturaProps {
  dados?: {
    sugestao?: Sugestao;
    botoes?: string[];
  };
  onConfirm: (resposta: string) => void;
}

const InterfaceConfirmacaoArquitetura: React.FC<InterfaceConfirmacaoArquiteturaProps> = ({ dados, onConfirm }) => {
  const isProcessing = useChatStore((s) => s.isProcessing);
  const sugestaoInicial = dados?.sugestao;
  const botoes = dados?.botoes || ['✅ Confirmar e Continuar', '✏️ Ajustar Manualmente'];

  const [modoEdicao, setModoEdicao] = useState(false);
  const [sugestaoEditada, setSugestaoEditada] = useState<Sugestao>(sugestaoInicial || {
    macroprocesso: '',
    processo: '',
    subprocesso: '',
    atividade: ''
  });

  if (!sugestaoInicial) {
    return null;
  }

  const handleConfirmarEdicao = () => {
    const comando = JSON.stringify({
      acao: 'preencher_arquitetura_completa',
      sugestao: sugestaoEditada
    });
    onConfirm(comando);
  };

  const handleCancelarEdicao = () => {
    setSugestaoEditada(sugestaoInicial);
    setModoEdicao(false);
  };

  return (
    <div className="interface-container fade-in">
      <div className="confirmacao-arquitetura-container">
        <div className="sugestao-card">
          <div className="sugestao-header">
            <span className="icone-check">✨</span>
            <h3>{modoEdicao ? 'Editar Arquitetura' : 'Minha sugestão'}</h3>
          </div>

          <div className="sugestao-detalhes">
            <div className="item">
              <span className="label">📋 Macroprocesso:</span>
              {modoEdicao ? (
                <input
                  type="text"
                  className="input-edicao"
                  value={sugestaoEditada.macroprocesso}
                  onChange={(e) => setSugestaoEditada({...sugestaoEditada, macroprocesso: e.target.value})}
                />
              ) : (
                <span className="valor">{sugestaoEditada.macroprocesso}</span>
              )}
            </div>

            <div className="item">
              <span className="label">📋 Processo:</span>
              {modoEdicao ? (
                <input
                  type="text"
                  className="input-edicao"
                  value={sugestaoEditada.processo}
                  onChange={(e) => setSugestaoEditada({...sugestaoEditada, processo: e.target.value})}
                />
              ) : (
                <span className="valor">{sugestaoEditada.processo}</span>
              )}
            </div>

            <div className="item">
              <span className="label">📋 Subprocesso:</span>
              {modoEdicao ? (
                <input
                  type="text"
                  className="input-edicao"
                  value={sugestaoEditada.subprocesso}
                  onChange={(e) => setSugestaoEditada({...sugestaoEditada, subprocesso: e.target.value})}
                />
              ) : (
                <span className="valor">{sugestaoEditada.subprocesso}</span>
              )}
            </div>

            <div className="item">
              <span className="label">📋 Atividade:</span>
              {modoEdicao ? (
                <input
                  type="text"
                  className="input-edicao"
                  value={sugestaoEditada.atividade}
                  onChange={(e) => setSugestaoEditada({...sugestaoEditada, atividade: e.target.value})}
                />
              ) : (
                <span className="valor">{sugestaoEditada.atividade}</span>
              )}
            </div>

            {sugestaoEditada.codigo_sugerido && (
              <div className="item codigo">
                <span className="label">🔢 CAP (Código da sua atividade):</span>
                <span className="valor codigo-valor">{sugestaoEditada.codigo_sugerido}</span>
              </div>
            )}

            {sugestaoInicial.justificativa && (
              <div className="justificativa">
                <span className="label">💡 Justificativa:</span>
                <p>{sugestaoInicial.justificativa}</p>
              </div>
            )}
          </div>
        </div>

        <div className="action-buttons">
          {modoEdicao ? (
            <>
              <button
                className="btn-interface btn-success"
                onClick={handleConfirmarEdicao}
                disabled={isProcessing}
              >
                ✅ Salvar Alterações
              </button>
              <button
                className="btn-interface btn-secondary"
                onClick={handleCancelarEdicao}
              >
                ✖️ Cancelar
              </button>
            </>
          ) : (
            <>
              <button
                className="btn-interface btn-success"
                onClick={() => {
                  const comando = JSON.stringify({
                    acao: 'preencher_arquitetura_completa',
                    sugestao: sugestaoEditada
                  });
                  onConfirm(comando);
                }}
                disabled={isProcessing}
              >
                {botoes[0]}
              </button>
              <button
                className="btn-interface btn-secondary-outline"
                onClick={() => setModoEdicao(true)}
                disabled={isProcessing}
              >
                {botoes[1]}
              </button>
            </>
          )}
        </div>
      </div>

      <style>{`
        .confirmacao-arquitetura-container {
          width: 100%;
          max-width: 700px;
          margin: 0 auto;
        }

        .sugestao-card {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 12px;
          padding: 1.5rem;
          color: white;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
          margin-bottom: 1.5rem;
        }

        .sugestao-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1.25rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        }

        .icone-check {
          font-size: 1.5rem;
        }

        .sugestao-header h3 {
          margin: 0;
          font-size: 1.25rem;
          font-weight: 600;
        }

        .sugestao-detalhes {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .item {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .item .label {
          font-size: 0.9rem;
          opacity: 0.9;
          font-weight: 500;
        }

        .item .valor {
          font-size: 1.05rem;
          font-weight: 600;
          padding: 0.5rem;
          background: rgba(255, 255, 255, 0.15);
          border-radius: 6px;
        }

        .input-edicao {
          font-size: 1.05rem;
          font-weight: 500;
          padding: 0.75rem;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 6px;
          background: rgba(255, 255, 255, 0.95);
          color: #333;
          font-family: inherit;
          transition: all 0.2s;
        }

        .input-edicao:focus {
          outline: none;
          border-color: #fff;
          background: #fff;
          box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2);
        }

        .item.codigo {
          margin-top: 0.5rem;
          padding-top: 1rem;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
        }

        .codigo-valor {
          font-family: 'Courier New', monospace;
          font-weight: 700;
          letter-spacing: 1px;
        }

        .justificativa {
          margin-top: 0.5rem;
          padding: 1rem;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          border-left: 3px solid rgba(255, 255, 255, 0.5);
        }

        .justificativa .label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 600;
          font-size: 0.9rem;
        }

        .justificativa p {
          margin: 0;
          font-size: 0.95rem;
          line-height: 1.5;
          opacity: 0.95;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
        }

        .btn-interface {
          flex: 1;
          padding: 0.875rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
          font-family: inherit;
        }

        .btn-success {
          background: #28a745;
          color: white;
        }

        .btn-success:hover {
          background: #218838;
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
        }

        .btn-secondary-outline {
          background: transparent;
          color: #667eea;
          border: 2px solid #667eea;
        }

        .btn-secondary-outline:hover {
          background: #667eea;
          color: white;
          transform: translateY(-1px);
        }

        .btn-interface:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }
      `}</style>
    </div>
  );
};

export default InterfaceConfirmacaoArquitetura;
