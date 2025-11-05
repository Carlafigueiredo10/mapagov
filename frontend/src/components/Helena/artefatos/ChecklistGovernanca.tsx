/**
 * Checklist de Governança
 * Artefato de verificação de estrutura do Domínio 1
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface ItemChecklist {
  id: string;
  pergunta: string;
  descricao: string;
  checked: boolean;
}

export const ChecklistGovernanca: React.FC = () => {
  const [itens, setItens] = useState<ItemChecklist[]>([
    {
      id: '1',
      pergunta: 'Comitê de governança definido?',
      descricao: 'Existe instância que aprova e acompanha o projeto?',
      checked: false
    },
    {
      id: '2',
      pergunta: 'Responsável técnico nomeado?',
      descricao: 'Há um gestor claramente designado?',
      checked: false
    },
    {
      id: '3',
      pergunta: 'Canal de comunicação definido?',
      descricao: 'Como a equipe se comunica (reuniões, chat, SEI)?',
      checked: false
    },
    {
      id: '4',
      pergunta: 'Registros formais criados?',
      descricao: 'Há SEI, termo de abertura ou outro instrumento?',
      checked: false
    },
    {
      id: '5',
      pergunta: 'Critérios de decisão claros?',
      descricao: 'O que precisa de aprovação superior?',
      checked: false
    }
  ]);

  const toggleItem = (id: string) => {
    setItens(itens.map(item =>
      item.id === id ? { ...item, checked: !item.checked } : item
    ));
  };

  const checkedCount = itens.filter(i => i.checked).length;
  const totalCount = itens.length;
  const percentual = Math.round((checkedCount / totalCount) * 100);

  const handleExportar = () => {
    const texto = `
CHECKLIST DE GOVERNANÇA
========================

Progresso: ${checkedCount}/${totalCount} itens (${percentual}%)

${itens.map((item, i) => `
${i + 1}. ${item.checked ? '✅' : '❌'} ${item.pergunta}
   ${item.descricao}
`).join('\n')}

${percentual === 100 ? '\n✅ GOVERNANÇA COMPLETA!' : '\n⚠️ Ainda há pendências de governança.'}
    `.trim();

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'checklist-governanca.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>🧰 Checklist de Governança</h2>
        <p className="artefato-descricao">
          Garante que o projeto nasceu com papéis, ritos e decisões formais definidos.
          Evita o clássico <strong>"ninguém sabia quem decidia"</strong>.
        </p>
      </div>

      {/* Barra de Progresso */}
      <div className="checklist-progresso">
        <h3>📊 Progresso da Governança</h3>
        <div className="checklist-barra">
          <div
            className="checklist-barra-fill"
            style={{ width: `${percentual}%` }}
          >
            {percentual > 15 && `${percentual}%`}
          </div>
        </div>
        <p className="checklist-resultado">
          {checkedCount} de {totalCount} itens concluídos
          {percentual === 100 && ' - 🎉 Governança Completa!'}
        </p>
      </div>

      {/* Lista de Itens */}
      <div className="checklist-items">
        {itens.map((item) => (
          <div
            key={item.id}
            className={`checklist-item ${item.checked ? 'checked' : ''}`}
            onClick={() => toggleItem(item.id)}
          >
            <div className="checklist-checkbox">
              {item.checked && '✓'}
            </div>
            <div className="checklist-content">
              <strong>{item.pergunta}</strong>
              <span>{item.descricao}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Checklist
        </button>
        <p className="footer-hint">
          💡 <strong>Dica:</strong> Clique nos itens para marcá-los como concluídos.
        </p>
      </div>
    </div>
  );
};

export default ChecklistGovernanca;
