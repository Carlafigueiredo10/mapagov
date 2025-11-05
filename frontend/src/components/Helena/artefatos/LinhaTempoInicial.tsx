/**
 * Linha do Tempo Inicial
 * Artefato de acompanhamento temporal do Domínio 1
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface MarcoTemporal {
  id: string;
  periodo: string;
  marco: string;
  responsavel: string;
  status: '✅' | '⏳' | '⚙️' | '❌';
}

const STATUS_OPTIONS = ['✅', '⏳', '⚙️', '❌'] as const;

export const LinhaTempoInicial: React.FC = () => {
  const [marcos, setMarcos] = useState<MarcoTemporal[]>([
    {
      id: '1',
      periodo: 'Janeiro',
      marco: 'Definir escopo e governança',
      responsavel: 'Coordenação de Planejamento',
      status: '✅'
    }
  ]);

  const adicionarMarco = () => {
    const novoMarco: MarcoTemporal = {
      id: Date.now().toString(),
      periodo: '',
      marco: '',
      responsavel: '',
      status: '⏳'
    };
    setMarcos([...marcos, novoMarco]);
  };

  const atualizarMarco = (id: string, campo: keyof MarcoTemporal, valor: string) => {
    setMarcos(marcos.map(m =>
      m.id === id ? { ...m, [campo]: valor } : m
    ));
  };

  const removerMarco = (id: string) => {
    setMarcos(marcos.filter(m => m.id !== id));
  };

  const cycleStatus = (id: string) => {
    const marco = marcos.find(m => m.id === id);
    if (!marco) return;

    const currentIndex = STATUS_OPTIONS.indexOf(marco.status);
    const nextStatus = STATUS_OPTIONS[(currentIndex + 1) % STATUS_OPTIONS.length];

    atualizarMarco(id, 'status', nextStatus);
  };

  const handleExportar = () => {
    const texto = `
LINHA DO TEMPO INICIAL
======================

${marcos.map((m, i) => `
${i + 1}. ${m.status} ${m.periodo || '(período não definido)'}
   Marco: ${m.marco || '(não definido)'}
   Responsável: ${m.responsavel || '(não definido)'}
`).join('\n')}
    `.trim();

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'linha-do-tempo-inicial.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>🧰 Linha do Tempo Inicial</h2>
        <p className="artefato-descricao">
          Visão simples de horizonte temporal — sem exigir cronograma Gantt.
          Serve para orientar a equipe e registrar marcos decisórios.
        </p>
      </div>

      <div className="timeline-container">
        <button className="timeline-add-btn" onClick={adicionarMarco}>
          ➕ Adicionar Marco
        </button>

        <div className="timeline-items">
          {marcos.map((marco) => (
            <div key={marco.id} className="timeline-item">
              <input
                type="text"
                value={marco.periodo}
                onChange={(e) => atualizarMarco(marco.id, 'periodo', e.target.value)}
                placeholder="Mês/Período"
              />
              <input
                type="text"
                value={marco.marco}
                onChange={(e) => atualizarMarco(marco.id, 'marco', e.target.value)}
                placeholder="Marco Principal"
              />
              <input
                type="text"
                value={marco.responsavel}
                onChange={(e) => atualizarMarco(marco.id, 'responsavel', e.target.value)}
                placeholder="Responsável"
              />
              <div
                className="timeline-status"
                onClick={() => cycleStatus(marco.id)}
                title="Clique para mudar status"
              >
                {marco.status}
              </div>
              <button
                className="timeline-delete"
                onClick={() => removerMarco(marco.id)}
                title="Remover marco"
              >
                🗑️
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Linha do Tempo
        </button>
        <p className="footer-hint">
          💡 <strong>Legenda:</strong> ✅ Concluído | ⏳ Aguardando | ⚙️ Em andamento | ❌ Atrasado
        </p>
      </div>
    </div>
  );
};

export default LinhaTempoInicial;
