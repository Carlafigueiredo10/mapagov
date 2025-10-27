import React, { useState, useEffect } from 'react';

interface InterfaceArquiteturaHierarquicaProps {
  dados: {
    macroprocessos?: string[];
    hierarquia_completa?: Record<string, {
      processos: Record<string, {
        subprocessos: Record<string, {
          atividades: string[];
        }>;
      }>;
    }>;
  };
  onEnviar: (valor: string) => void;
}

const InterfaceArquiteturaHierarquica: React.FC<InterfaceArquiteturaHierarquicaProps> = ({ dados, onEnviar }) => {
  const { macroprocessos = [], hierarquia_completa = {} } = dados;

  const [macroSelecionado, setMacroSelecionado] = useState<string>('');
  const [processoSelecionado, setProcessoSelecionado] = useState<string>('');
  const [subprocessoSelecionado, setSubprocessoSelecionado] = useState<string>('');
  const [atividadeSelecionada, setAtividadeSelecionada] = useState<string>('');

  const [processosDisponiveis, setProcessosDisponiveis] = useState<string[]>([]);
  const [subprocessosDisponiveis, setSubprocessosDisponiveis] = useState<string[]>([]);
  const [atividadesDisponiveis, setAtividadesDisponiveis] = useState<string[]>([]);

  // Atualizar processos quando macroprocesso mudar
  useEffect(() => {
    if (macroSelecionado && hierarquia_completa[macroSelecionado]) {
      const processos = Object.keys(hierarquia_completa[macroSelecionado].processos);
      setProcessosDisponiveis(processos);
      setProcessoSelecionado('');
      setSubprocessoSelecionado('');
      setAtividadeSelecionada('');
      setSubprocessosDisponiveis([]);
      setAtividadesDisponiveis([]);
    } else {
      setProcessosDisponiveis([]);
    }
  }, [macroSelecionado, hierarquia_completa]);

  // Atualizar subprocessos quando processo mudar
  useEffect(() => {
    if (macroSelecionado && processoSelecionado && hierarquia_completa[macroSelecionado]?.processos[processoSelecionado]) {
      const subprocessos = Object.keys(hierarquia_completa[macroSelecionado].processos[processoSelecionado].subprocessos);
      setSubprocessosDisponiveis(subprocessos);
      setSubprocessoSelecionado('');
      setAtividadeSelecionada('');
      setAtividadesDisponiveis([]);
    } else {
      setSubprocessosDisponiveis([]);
    }
  }, [macroSelecionado, processoSelecionado, hierarquia_completa]);

  // Atualizar atividades quando subprocesso mudar
  useEffect(() => {
    if (macroSelecionado && processoSelecionado && subprocessoSelecionado &&
        hierarquia_completa[macroSelecionado]?.processos[processoSelecionado]?.subprocessos[subprocessoSelecionado]) {
      const atividades = hierarquia_completa[macroSelecionado].processos[processoSelecionado].subprocessos[subprocessoSelecionado].atividades;
      setAtividadesDisponiveis(atividades);
      setAtividadeSelecionada('');
    } else {
      setAtividadesDisponiveis([]);
    }
  }, [macroSelecionado, processoSelecionado, subprocessoSelecionado, hierarquia_completa]);

  const handleConfirmar = () => {
    if (!macroSelecionado || !processoSelecionado || !subprocessoSelecionado || !atividadeSelecionada) {
      alert('Por favor, selecione todos os níveis da arquitetura antes de confirmar.');
      return;
    }

    // Enviar JSON com a seleção completa
    const selecao = JSON.stringify({
      macroprocesso: macroSelecionado,
      processo: processoSelecionado,
      subprocesso: subprocessoSelecionado,
      atividade: atividadeSelecionada
    });

    onEnviar(selecao);
  };

  return (
    <div className="arquitetura-hierarquica-container">
      <div className="dropdowns-container">
        {/* Macroprocesso */}
        <div className="dropdown-grupo">
          <label>📊 Macroprocesso</label>
          <select
            value={macroSelecionado}
            onChange={(e) => setMacroSelecionado(e.target.value)}
            className="dropdown-hierarquico"
          >
            <option value="">Selecione...</option>
            {macroprocessos.map((macro) => (
              <option key={macro} value={macro}>{macro}</option>
            ))}
          </select>
        </div>

        {/* Processo */}
        {processosDisponiveis.length > 0 && (
          <div className="dropdown-grupo fade-in">
            <label>⚙️ Processo</label>
            <select
              value={processoSelecionado}
              onChange={(e) => setProcessoSelecionado(e.target.value)}
              className="dropdown-hierarquico"
            >
              <option value="">Selecione...</option>
              {processosDisponiveis.map((processo) => (
                <option key={processo} value={processo}>{processo}</option>
              ))}
            </select>
          </div>
        )}

        {/* Subprocesso */}
        {subprocessosDisponiveis.length > 0 && (
          <div className="dropdown-grupo fade-in">
            <label>🔧 Subprocesso</label>
            <select
              value={subprocessoSelecionado}
              onChange={(e) => setSubprocessoSelecionado(e.target.value)}
              className="dropdown-hierarquico"
            >
              <option value="">Selecione...</option>
              {subprocessosDisponiveis.map((subprocesso) => (
                <option key={subprocesso} value={subprocesso}>{subprocesso}</option>
              ))}
            </select>
          </div>
        )}

        {/* Atividade */}
        {atividadesDisponiveis.length > 0 && (
          <div className="dropdown-grupo fade-in">
            <label>✅ Atividade</label>
            <select
              value={atividadeSelecionada}
              onChange={(e) => setAtividadeSelecionada(e.target.value)}
              className="dropdown-hierarquico"
            >
              <option value="">Selecione...</option>
              {atividadesDisponiveis.map((atividade) => (
                <option key={atividade} value={atividade}>{atividade}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Botão de confirmação */}
      {atividadeSelecionada && (
        <div className="botao-confirmar-container fade-in">
          <button
            className="btn-confirmar-selecao"
            onClick={handleConfirmar}
          >
            ✅ Confirmar Seleção
          </button>
        </div>
      )}

      <style>{`
        .arquitetura-hierarquica-container {
          margin: 1.5rem 0;
          padding: 1.5rem;
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .dropdowns-container {
          display: flex;
          flex-direction: column;
          gap: 1.2rem;
        }

        .dropdown-grupo {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .dropdown-grupo label {
          font-weight: 600;
          font-size: 0.95rem;
          color: #2c3e50;
        }

        .dropdown-hierarquico {
          padding: 0.8rem 1rem;
          border: 2px solid #3498db;
          border-radius: 8px;
          font-size: 1rem;
          background: white;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .dropdown-hierarquico:hover {
          border-color: #2980b9;
          box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
        }

        .dropdown-hierarquico:focus {
          outline: none;
          border-color: #2980b9;
          box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }

        .botao-confirmar-container {
          margin-top: 1.5rem;
          display: flex;
          justify-content: center;
        }

        .btn-confirmar-selecao {
          padding: 1rem 2.5rem;
          background: #27ae60;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
        }

        .btn-confirmar-selecao:hover {
          background: #229954;
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(39, 174, 96, 0.4);
        }

        .btn-confirmar-selecao:active {
          transform: translateY(0);
        }

        .fade-in {
          animation: fadeIn 0.4s ease-in;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (max-width: 768px) {
          .arquitetura-hierarquica-container {
            padding: 1rem;
          }

          .dropdown-hierarquico {
            font-size: 0.9rem;
          }

          .btn-confirmar-selecao {
            width: 100%;
            padding: 0.9rem;
            font-size: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default InterfaceArquiteturaHierarquica;
