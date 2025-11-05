/**
 * Mapa de Exclusões e Restrições
 * Artefato do Domínio 2 - Escopo e Valor
 */

import React, { useState } from 'react';
import './Artefatos.css';

type TipoItem = 'exclusao' | 'restricao';

interface ItemExclusao {
  id: string;
  tipo: TipoItem;
  descricao: string;
  justificativa: string;
}

export const MapaExclusoes: React.FC = () => {
  const [itens, setItens] = useState<ItemExclusao[]>([
    {
      id: '1',
      tipo: 'exclusao',
      descricao: 'Não abrange novas contratações permanentes.',
      justificativa: 'Fora da competência da unidade.'
    },
    {
      id: '2',
      tipo: 'restricao',
      descricao: 'Execução condicionada à liberação orçamentária.',
      justificativa: 'Dependência externa.'
    }
  ]);

  const [filtro, setFiltro] = useState<TipoItem | 'todos'>('todos');

  const handleChange = (id: string, campo: keyof Omit<ItemExclusao, 'id'>, valor: string | TipoItem) => {
    setItens(itens.map(i =>
      i.id === id ? { ...i, [campo]: valor } : i
    ));
  };

  const adicionarItem = (tipo: TipoItem) => {
    const novoItem: ItemExclusao = {
      id: Date.now().toString(),
      tipo,
      descricao: '',
      justificativa: ''
    };
    setItens([...itens, novoItem]);
  };

  const removerItem = (id: string) => {
    setItens(itens.filter(i => i.id !== id));
  };

  const handleExportar = () => {
    let texto = 'MAPA DE EXCLUSÕES E RESTRIÇÕES\n';
    texto += '=' .repeat(50) + '\n\n';

    const exclusoes = itens.filter(i => i.tipo === 'exclusao');
    const restricoes = itens.filter(i => i.tipo === 'restricao');

    if (exclusoes.length > 0) {
      texto += 'EXCLUSÕES (O que NÃO está no escopo):\n';
      texto += '-'.repeat(50) + '\n';
      exclusoes.forEach((item, index) => {
        texto += `${index + 1}. ${item.descricao}\n`;
        texto += `   Justificativa: ${item.justificativa}\n\n`;
      });
    }

    if (restricoes.length > 0) {
      texto += '\nRESTRIÇÕES (Limitações e condições):\n';
      texto += '-'.repeat(50) + '\n';
      restricoes.forEach((item, index) => {
        texto += `${index + 1}. ${item.descricao}\n`;
        texto += `   Justificativa: ${item.justificativa}\n\n`;
      });
    }

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mapa-exclusoes-restricoes.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const itensFiltrados = filtro === 'todos'
    ? itens
    : itens.filter(i => i.tipo === filtro);

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>🚫 Mapa de Exclusões e Restrições</h2>
        <p className="artefato-descricao">
          Deixa explícito o que o projeto <strong>não inclui</strong>, prevenindo escopo inflado.
          Registra também as <strong>restrições</strong> e condições que afetam a execução.
        </p>
      </div>

      <div className="mapa-controls">
        <div className="filtro-buttons">
          <button
            className={`filtro-btn ${filtro === 'todos' ? 'active' : ''}`}
            onClick={() => setFiltro('todos')}
          >
            📋 Todos ({itens.length})
          </button>
          <button
            className={`filtro-btn ${filtro === 'exclusao' ? 'active' : ''}`}
            onClick={() => setFiltro('exclusao')}
          >
            🚫 Exclusões ({itens.filter(i => i.tipo === 'exclusao').length})
          </button>
          <button
            className={`filtro-btn ${filtro === 'restricao' ? 'active' : ''}`}
            onClick={() => setFiltro('restricao')}
          >
            ⚠️ Restrições ({itens.filter(i => i.tipo === 'restricao').length})
          </button>
        </div>

        <div className="adicionar-buttons">
          <button
            className="btn-adicionar-small"
            onClick={() => adicionarItem('exclusao')}
          >
            ➕ Nova Exclusão
          </button>
          <button
            className="btn-adicionar-small"
            onClick={() => adicionarItem('restricao')}
          >
            ➕ Nova Restrição
          </button>
        </div>
      </div>

      <div className="exclusoes-lista">
        {itensFiltrados.map((item) => (
          <div key={item.id} className={`exclusao-card exclusao-${item.tipo}`}>
            <div className="exclusao-header">
              <select
                value={item.tipo}
                onChange={(e) => handleChange(item.id, 'tipo', e.target.value as TipoItem)}
                className="exclusao-tipo-select"
              >
                <option value="exclusao">🚫 Exclusão</option>
                <option value="restricao">⚠️ Restrição</option>
              </select>
              <button
                className="btn-remover-small"
                onClick={() => removerItem(item.id)}
                title="Remover item"
              >
                ✕
              </button>
            </div>

            <div className="exclusao-body">
              <div className="exclusao-field">
                <label>Descrição:</label>
                <textarea
                  value={item.descricao}
                  onChange={(e) => handleChange(item.id, 'descricao', e.target.value)}
                  placeholder={
                    item.tipo === 'exclusao'
                      ? 'O que NÃO está incluído no projeto?'
                      : 'Qual a limitação ou condição?'
                  }
                  rows={2}
                />
              </div>

              <div className="exclusao-field">
                <label>Justificativa:</label>
                <textarea
                  value={item.justificativa}
                  onChange={(e) => handleChange(item.id, 'justificativa', e.target.value)}
                  placeholder="Por que essa exclusão/restrição existe?"
                  rows={2}
                />
              </div>
            </div>
          </div>
        ))}

        {itensFiltrados.length === 0 && (
          <div className="lista-vazia">
            <p>Nenhum item {filtro !== 'todos' ? `do tipo "${filtro}"` : ''} cadastrado.</p>
            <p>Use os botões acima para adicionar exclusões ou restrições.</p>
          </div>
        )}
      </div>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Mapa
        </button>
        <button className="btn-secundario" onClick={() => window.history.back()}>
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default MapaExclusoes;
