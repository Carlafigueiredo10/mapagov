// No arquivo: InterfaceSistemas.tsx

import React, { useState, useMemo } from 'react';

// Definindo as props que este componente recebe
interface SubInterfaceProps {
  dados: Record<string, unknown> | null | undefined;
  onConfirm: (resposta: string) => void;
}

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

            <div className="options-grid">
                {listaSistemas.map((sys: string, idx: number) => (
                    <div
                        key={idx}
                        className={`option-card ${sistemasSelecionados.includes(sys) ? 'selected' : ''}`}
                        onClick={() => toggleSistema(sys)}
                    >
                        <input type="checkbox" readOnly checked={sistemasSelecionados.includes(sys)} />
                        <label>{sys}</label>
                    </div>
                ))}
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

          .aviso-sem-dados {
            padding: 2rem;
            text-align: center;
            color: #6c757d;
            background: #f8f9fa;
            border-radius: 8px;
            margin: 1rem 0;
          }
        `}</style>
    </div>
  );
};

export default InterfaceSistemas;