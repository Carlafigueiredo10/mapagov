// No arquivo: InterfaceSistemas.tsx

import React, { useState, useMemo } from 'react';

// Definindo as props que este componente recebe
interface SubInterfaceProps {
  dados: Record<string, unknown> | null | undefined;
  onConfirm: (resposta: string) => void;
}

// Mapeamento de sistemas para ícones e grupos
const SISTEMAS_INFO: Record<string, { icone: string; grupo: string }> = {
  'SIAPE': { icone: '💼', grupo: 'RH' },
  'SISAC': { icone: '💰', grupo: 'RH' },
  'SIGEPE': { icone: '👥', grupo: 'RH' },
  'SEI': { icone: '📄', grupo: 'Documentos' },
  'SEI+': { icone: '📋', grupo: 'Documentos' },
  'SOU GOV': { icone: '🌐', grupo: 'Cidadão' },
  'GOV.BR': { icone: '🏛️', grupo: 'Cidadão' },
  'SICONV': { icone: '🤝', grupo: 'Convênios' },
  'COMPRASNET': { icone: '🛒', grupo: 'Compras' },
  'SIASG': { icone: '📦', grupo: 'Compras' },
  'SICAF': { icone: '📇', grupo: 'Compras' },
  'TESOURO GERENCIAL': { icone: '💵', grupo: 'Financeiro' },
  'SIAFI': { icone: '💹', grupo: 'Financeiro' },
  'SIPEC': { icone: '👔', grupo: 'Gestão de Pessoas' },
  'SOUGOV': { icone: '🌐', grupo: 'Cidadão' },
};

const InterfaceSistemas: React.FC<SubInterfaceProps> = ({ dados, onConfirm }) => {
  const [sistemasSelecionados, setSistemasSelecionados] = useState<string[]>([]);

  // Extrair lista de sistemas do backend (aceita tanto 'sugestoes' quanto 'sistemas_por_categoria')
  const listaSistemas = useMemo(() => {
    // Tentar pegar 'sugestoes' primeiro (lista simples)
    const sugestoesDeDados = (dados as { sugestoes?: unknown[] })?.sugestoes;
    if (sugestoesDeDados && Array.isArray(sugestoesDeDados)) {
      return sugestoesDeDados as string[];
    }

    // Caso contrário, pegar 'sistemas_por_categoria' (dicionário por categoria)
    const sistemasPorCategoria = (dados as { sistemas_por_categoria?: Record<string, string[]> })?.sistemas_por_categoria;
    if (sistemasPorCategoria && typeof sistemasPorCategoria === 'object') {
      // Converter dicionário em lista plana
      const todosSistemas: string[] = [];
      Object.values(sistemasPorCategoria).forEach(categoria => {
        if (Array.isArray(categoria)) {
          todosSistemas.push(...categoria);
        }
      });
      return todosSistemas;
    }

    console.warn("InterfaceSistemas: dados ausentes ou em formato inválido.");
    return [];
  }, [dados]);

  const toggleSistema = (sistema: string) => {
    setSistemasSelecionados(prev =>
      prev.includes(sistema) ? prev.filter(s => s !== sistema) : [...prev, sistema]
    );
  };

  const selecionarTodos = () => {
    if (sistemasSelecionados.length === listaSistemas.length) {
      // Se todos estão selecionados, desselecionar todos
      setSistemasSelecionados([]);
    } else {
      // Caso contrário, selecionar todos
      setSistemasSelecionados([...listaSistemas]);
    }
  };

  const handleConfirm = () => {
    const resposta = sistemasSelecionados.length > 0 ? sistemasSelecionados.join(', ') : 'nenhum';
    onConfirm(resposta);
  }

  // Função auxiliar para pegar info do sistema
  const getSistemaInfo = (sistema: string) => {
    const sistemaUpper = sistema.toUpperCase().trim();
    return SISTEMAS_INFO[sistemaUpper] || { icone: '💻', grupo: 'Outros' };
  }

  return (
    <div className="interface-container fade-in">
        <div className="interface-title">💻 Quais sistemas são utilizados?</div>

        {listaSistemas.length > 0 ? (
          <>
            <div className="selecao-info">
              <span className="contador-selecao">
                {sistemasSelecionados.length} de {listaSistemas.length} selecionados
              </span>
              <button
                className="btn-selecionar-todos"
                onClick={selecionarTodos}
                type="button"
              >
                {sistemasSelecionados.length === listaSistemas.length ? 'Desmarcar Todos' : 'Selecionar Todos'}
              </button>
            </div>

            <div className="sistemas-grid">
                {listaSistemas.map((sys: string, idx: number) => {
                  const info = getSistemaInfo(sys);
                  const isSelected = sistemasSelecionados.includes(sys);

                  return (
                    <div
                        key={idx}
                        className={`sistema-card ${isSelected ? 'selected' : ''}`}
                        onClick={() => toggleSistema(sys)}
                    >
                        <div className="sistema-icone">{info.icone}</div>
                        <div className="sistema-info">
                          <div className="sistema-nome">{sys}</div>
                          <div className="sistema-grupo">{info.grupo}</div>
                        </div>
                        <div className="sistema-checkbox">
                          {isSelected && <span className="check-icon">✓</span>}
                        </div>
                    </div>
                  );
                })}
            </div>
          </>
        ) : (
          <div className="aviso-sem-dados">
            <p>Nenhum sistema disponível para seleção.</p>
          </div>
        )}

        <div className="action-buttons">
            <button className="btn-interface btn-secondary" onClick={() => onConfirm('nao sei')}>Não Sei</button>
            <button className="btn-interface btn-primary" onClick={handleConfirm}>Confirmar</button>
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

          .sistemas-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.75rem;
            margin-bottom: 1.5rem;
          }

          .sistema-card {
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

          .sistema-card:hover {
            border-color: #4a90e2;
            box-shadow: 0 2px 8px rgba(74, 144, 226, 0.15);
            transform: translateY(-1px);
          }

          .sistema-card.selected {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
          }

          .sistema-card.selected .sistema-nome {
            color: white;
            font-weight: 600;
          }

          .sistema-card.selected .sistema-grupo {
            color: rgba(255, 255, 255, 0.85);
          }

          .sistema-icone {
            font-size: 1.75rem;
            line-height: 1;
            flex-shrink: 0;
            filter: grayscale(0.3);
            transition: filter 0.2s;
          }

          .sistema-card.selected .sistema-icone {
            filter: grayscale(0) brightness(1.2);
          }

          .sistema-info {
            flex: 1;
            min-width: 0;
          }

          .sistema-nome {
            font-size: 0.80rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.25rem;
            word-break: break-word;
          }

          .sistema-grupo {
            font-size: 0.65rem;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }

          .sistema-checkbox {
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

          .sistema-card.selected .sistema-checkbox {
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

          @media (max-width: 768px) {
            .sistemas-grid {
              grid-template-columns: 1fr;
            }
          }
        `}</style>
    </div>
  );
};

export default InterfaceSistemas;