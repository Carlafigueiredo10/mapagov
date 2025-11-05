/**
 * Organograma de Governança
 * Artefato do Domínio 3 - Equipe e Responsabilidades
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface InstanciaGovernanca {
  id: string;
  instancia: string;
  composicao: string;
  funcao: string;
  frequencia: string;
}

export const OrganogramaGovernanca: React.FC = () => {
  const [instancias, setInstancias] = useState<InstanciaGovernanca[]>([
    {
      id: '1',
      instancia: 'Comitê Gestor',
      composicao: 'Direção + Coordenação',
      funcao: 'Valida decisões estratégicas',
      frequencia: 'Mensal'
    },
    {
      id: '2',
      instancia: 'Equipe Técnica',
      composicao: 'Analistas + Apoio',
      funcao: 'Executa ações planejadas',
      frequencia: 'Semanal'
    },
    {
      id: '3',
      instancia: 'Apoio Institucional',
      composicao: 'Assessoria',
      funcao: 'Apoio transversal e registro',
      frequencia: 'Conforme demanda'
    }
  ]);

  const handleChange = (id: string, campo: keyof Omit<InstanciaGovernanca, 'id'>, valor: string) => {
    setInstancias(instancias.map(i =>
      i.id === id ? { ...i, [campo]: valor } : i
    ));
  };

  const adicionarInstancia = () => {
    const novaInstancia: InstanciaGovernanca = {
      id: Date.now().toString(),
      instancia: '',
      composicao: '',
      funcao: '',
      frequencia: ''
    };
    setInstancias([...instancias, novaInstancia]);
  };

  const removerInstancia = (id: string) => {
    setInstancias(instancias.filter(i => i.id !== id));
  };

  const handleExportar = () => {
    let texto = 'ORGANOGRAMA DE GOVERNANÇA\n';
    texto += '='.repeat(60) + '\n\n';

    instancias.forEach((inst, index) => {
      texto += `${index + 1}. ${inst.instancia}\n`;
      texto += `   Composição: ${inst.composicao}\n`;
      texto += `   Função: ${inst.funcao}\n`;
      texto += `   Frequência: ${inst.frequencia}\n\n`;
    });

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'organograma-governanca.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>🏢 Organograma de Governança</h2>
        <p className="artefato-descricao">
          Representa visualmente as instâncias de decisão e fluxos de comunicação do projeto.
          Define quem compõe cada instância, sua função e frequência de atuação.
        </p>
      </div>

      <div className="organograma-grid">
        {instancias.map((instancia, index) => (
          <div key={instancia.id} className="organograma-card">
            <div className="organograma-header">
              <span className="organograma-nivel">Nível {index + 1}</span>
              <input
                type="text"
                className="organograma-nome"
                value={instancia.instancia}
                onChange={(e) => handleChange(instancia.id, 'instancia', e.target.value)}
                placeholder="Nome da instância"
              />
              <button
                className="btn-remover-small"
                onClick={() => removerInstancia(instancia.id)}
                title="Remover instância"
              >
                ✕
              </button>
            </div>

            <div className="organograma-body">
              <div className="organograma-field">
                <label>👥 Composição:</label>
                <input
                  type="text"
                  value={instancia.composicao}
                  onChange={(e) => handleChange(instancia.id, 'composicao', e.target.value)}
                  placeholder="Quem faz parte?"
                />
              </div>

              <div className="organograma-field">
                <label>🎯 Função:</label>
                <input
                  type="text"
                  value={instancia.funcao}
                  onChange={(e) => handleChange(instancia.id, 'funcao', e.target.value)}
                  placeholder="Qual a responsabilidade?"
                />
              </div>

              <div className="organograma-field">
                <label>📅 Frequência:</label>
                <input
                  type="text"
                  value={instancia.frequencia}
                  onChange={(e) => handleChange(instancia.id, 'frequencia', e.target.value)}
                  placeholder="Com que frequência se reúne?"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button className="btn-adicionar" onClick={adicionarInstancia}>
        ➕ Adicionar Instância
      </button>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Organograma
        </button>
        <button className="btn-secundario" onClick={() => window.history.back()}>
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default OrganogramaGovernanca;
