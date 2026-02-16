import React, { useState, useMemo } from "react";

interface InterfaceOperadoresProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

// Mapeamento de operadores para ícones e categorias
const OPERADORES_INFO: Record<string, { icone: string; categoria: string }> = {
  'EXECUTOR': { icone: '⚙️', categoria: 'Execução' },
  'REVISOR': { icone: '🔍', categoria: 'Revisão' },
  'APROVADOR': { icone: '✅', categoria: 'Aprovação' },
  'APOIO': { icone: '🤝', categoria: 'Suporte' },
  'GESTOR': { icone: '👔', categoria: 'Gestão' },
  'COORDENADOR-GERAL': { icone: '👩🏿‍💼', categoria: 'Coordenação Geral' },
  'COORDENADOR': { icone: '👩‍💼', categoria: 'Coordenação' },
  'ASSISTENTE': { icone: '👶', categoria: 'Assistência' },
  'ANALISTA': { icone: '💡', categoria: 'Análise' },
  'TÉCNICO': { icone: '🔧', categoria: 'Técnico' },
  'ESPECIALISTA': { icone: '🎓', categoria: 'Especialidade' },
  'CONSULTOR': { icone: '👨‍⚕️', categoria: 'Consultoria' },
  'AUDITOR': { icone: '🔎', categoria: 'Auditoria' },
  'SERVIDOR': { icone: '👤', categoria: 'Geral' },
  'SERVIDOR SÊNIOR': { icone: '🧓', categoria: 'Sênior' },
  'SERVIDORA': { icone: '👩', categoria: 'Geral' },
};

const InterfaceOperadores: React.FC<InterfaceOperadoresProps> = ({ dados, onConfirm }) => {
  const [operadoresSelecionados, setOperadoresSelecionados] = useState<string[]>([]);
  const [operadoresDigitados, setOperadoresDigitados] = useState<string[]>([]);
  const [operadorManual, setOperadorManual] = useState<string>('');

  // Extrair lista de operadores do backend
  const listaOperadores = useMemo(() => {
    const opcoes = (dados as { opcoes?: string[] })?.opcoes;
    if (opcoes && Array.isArray(opcoes)) {
      return opcoes;
    }
    console.warn("InterfaceOperadores: opcoes ausentes ou inválidas");
    return [];
  }, [dados]);

  // Filtrar "Outros (especificar)" — substituído pelo campo manual
  const listaExibicao = useMemo(() =>
    listaOperadores.filter(op => op.toLowerCase() !== 'outros (especificar)'),
    [listaOperadores]
  );

  const todosOperadoresSelecionados = [...operadoresSelecionados, ...operadoresDigitados];

  const toggleOperador = (operador: string) => {
    setOperadoresSelecionados(prev =>
      prev.includes(operador)
        ? prev.filter(o => o !== operador)
        : [...prev, operador]
    );
  };

  const selecionarTodos = () => {
    if (operadoresSelecionados.length === listaExibicao.length) {
      setOperadoresSelecionados([]);
    } else {
      setOperadoresSelecionados([...listaExibicao]);
    }
  };

  const adicionarOperadorManual = () => {
    const operador = operadorManual.trim();
    if (operador && !todosOperadoresSelecionados.includes(operador)) {
      setOperadoresDigitados([...operadoresDigitados, operador]);
      setOperadorManual('');
    }
  };

  const removerOperadorDigitado = (operador: string) => {
    setOperadoresDigitados(operadoresDigitados.filter(o => o !== operador));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      adicionarOperadorManual();
    }
  };

  const handleConfirm = () => {
    const resposta = todosOperadoresSelecionados.length > 0
      ? JSON.stringify(todosOperadoresSelecionados)
      : 'nenhum';

    console.log('📤 InterfaceOperadores enviando:', resposta);
    onConfirm(resposta);
  };

  // Função auxiliar para pegar info do operador
  const getOperadorInfo = (operador: string) => {
    const operadorUpper = operador.toUpperCase().trim();
    return OPERADORES_INFO[operadorUpper] || { icone: '👤', categoria: 'Geral' };
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">👥 Quem são os responsáveis?</div>

      {listaOperadores.length > 0 ? (
        <>
          <div className="selecao-info">
            <span className="contador-selecao">
              {todosOperadoresSelecionados.length} operador(es) selecionado(s)
              {operadoresDigitados.length > 0 && ` (${operadoresDigitados.length} manual)`}
            </span>
            <button
              className="btn-selecionar-todos"
              onClick={selecionarTodos}
              type="button"
            >
              {operadoresSelecionados.length === listaExibicao.length
                ? 'Desmarcar Todos'
                : 'Selecionar Todos'}
            </button>
          </div>

          <div className="operadores-grid">
            {listaExibicao.map((operador, idx) => {
              const info = getOperadorInfo(operador);
              const isSelected = operadoresSelecionados.includes(operador);

              return (
                <div
                  key={idx}
                  className={`operador-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => toggleOperador(operador)}
                >
                  <div className="operador-icone">{info.icone}</div>
                  <div className="operador-info">
                    <div className="operador-nome">{operador}</div>
                    <div className="operador-categoria">{info.categoria}</div>
                  </div>
                  <div className="operador-checkbox">
                    {isSelected && <span className="check-icon">✓</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      ) : (
        <div className="aviso-sem-dados">
          <p>Nenhum operador disponível para seleção.</p>
        </div>
      )}

      {/* Operadores adicionados manualmente (chips) */}
      {operadoresDigitados.length > 0 && (
        <div className="operadores-digitados">
          <div className="operadores-digitados-label">
            📝 Operadores adicionados manualmente:
          </div>
          <div className="operadores-digitados-lista">
            {operadoresDigitados.map((operador, idx) => (
              <div key={idx} className="operador-digitado-chip">
                <span>{operador}</span>
                <button
                  className="btn-remover-operador"
                  onClick={() => removerOperadorDigitado(operador)}
                  title="Remover"
                  type="button"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Campo de entrada manual */}
      <div className="campo-manual-operador">
        <div className="campo-manual-operador-label">
          Outro operador? ✍️ Digite manualmente abaixo.
        </div>
        <div className="campo-manual-operador-group">
          <input
            type="text"
            className="campo-manual-operador-input"
            placeholder="Ex: Estagiário, Terceirizado TI, etc."
            value={operadorManual}
            onChange={(e) => setOperadorManual(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button
            className="btn-adicionar-operador"
            onClick={adicionarOperadorManual}
            disabled={!operadorManual.trim()}
            type="button"
          >
            + Adicionar
          </button>
        </div>
      </div>

      <div className="action-buttons">
        <button className="btn-interface btn-secondary" onClick={() => onConfirm('nao sei')}>
          Não Sei
        </button>
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar ({todosOperadoresSelecionados.length})
        </button>
      </div>

      <style>{`
        .selecao-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          padding: 0.75rem;
          background: #f8f9fa;
          border-radius: 6px;
        }

        .contador-selecao {
          font-size: 0.9rem;
          color: #495057;
          font-weight: 500;
        }

        .btn-selecionar-todos {
          padding: 0.5rem 1rem;
          background: #17a2b8;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-selecionar-todos:hover {
          background: #138496;
        }

        .operadores-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 0.75rem;
          margin-bottom: 1.5rem;
        }

        .operador-card {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: white;
          border: 2px solid #e9ecef;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          position: relative;
        }

        .operador-card:hover {
          border-color: #4a90e2;
          box-shadow: 0 2px 8px rgba(74, 144, 226, 0.15);
          transform: translateY(-1px);
        }

        .operador-card.selected {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-color: #667eea;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .operador-card.selected .operador-nome {
          color: white;
          font-weight: 600;
        }

        .operador-card.selected .operador-categoria {
          color: rgba(255, 255, 255, 0.85);
        }

        .operador-icone {
          font-size: 1.75rem;
          line-height: 1;
          flex-shrink: 0;
          filter: grayscale(0.3);
          transition: filter 0.2s;
        }

        .operador-card.selected .operador-icone {
          filter: grayscale(0) brightness(1.2);
        }

        .operador-info {
          flex: 1;
          min-width: 0;
        }

        .operador-nome {
          font-size: 0.80rem;
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 0.25rem;
          word-break: break-word;
        }

        .operador-categoria {
          font-size: 0.65rem;
          color: #6c757d;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .operador-checkbox {
          width: 24px;
          height: 24px;
          border: 2px solid #dee2e6;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          transition: all 0.2s;
        }

        .operador-card.selected .operador-checkbox {
          background: white;
          border-color: white;
        }

        .check-icon {
          color: #667eea;
          font-size: 1.2rem;
          font-weight: bold;
          line-height: 1;
        }

        .aviso-sem-dados {
          padding: 2rem;
          text-align: center;
          color: #6c757d;
          background: #f8f9fa;
          border-radius: 8px;
          margin: 1rem 0;
        }

        .operadores-digitados {
          margin: 1rem 0;
          padding: 1rem;
          background: #e8f5e9;
          border-radius: 8px;
          border: 2px solid #4caf50;
        }

        .operadores-digitados-label {
          margin-bottom: 0.75rem;
          font-size: 0.875rem;
          color: #2e7d32;
          font-weight: 600;
        }

        .operadores-digitados-lista {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .operador-digitado-chip {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 0.75rem;
          background: white;
          border: 2px solid #4caf50;
          border-radius: 20px;
          font-size: 0.875rem;
          font-weight: 500;
          color: #2e7d32;
        }

        .btn-remover-operador {
          width: 20px;
          height: 20px;
          padding: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f44336;
          color: white;
          border: none;
          border-radius: 50%;
          cursor: pointer;
          font-size: 12px;
          line-height: 1;
          transition: all 0.2s;
        }

        .btn-remover-operador:hover {
          background: #d32f2f;
          transform: scale(1.1);
        }

        .campo-manual-operador {
          margin: 1.5rem 0;
          padding: 1.25rem;
          background: #fff9e6;
          border-radius: 8px;
          border: 2px dashed #ffc107;
        }

        .campo-manual-operador-label {
          margin-bottom: 0.75rem;
          font-size: 0.875rem;
          color: #856404;
          font-weight: 500;
        }

        .campo-manual-operador-group {
          display: flex;
          gap: 0.5rem;
        }

        .campo-manual-operador-input {
          flex: 1;
          padding: 0.625rem 0.875rem;
          border: 2px solid #ddd;
          border-radius: 6px;
          font-size: 0.875rem;
          transition: all 0.2s;
        }

        .campo-manual-operador-input:focus {
          outline: none;
          border-color: #1351B4;
          background: #f8f9fa;
        }

        .btn-adicionar-operador {
          padding: 0.625rem 1.25rem;
          background: #28a745;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
          transition: all 0.2s;
          white-space: nowrap;
        }

        .btn-adicionar-operador:hover:not(:disabled) {
          background: #218838;
        }

        .btn-adicionar-operador:disabled {
          background: #6c757d;
          cursor: not-allowed;
          opacity: 0.5;
        }

        @media (max-width: 768px) {
          .operadores-grid {
            grid-template-columns: 1fr;
          }
          .campo-manual-operador-group {
            flex-direction: column;
          }
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .btn-interface {
          flex: 1;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
        }
      `}</style>
    </div>
  );
};

export default InterfaceOperadores;