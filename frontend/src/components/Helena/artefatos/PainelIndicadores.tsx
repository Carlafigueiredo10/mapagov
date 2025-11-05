/**
 * Painel de Indicadores de Valor Público (mini-OKR)
 * Artefato do Domínio 2 - Escopo e Valor
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface Indicador {
  id: string;
  objetivo: string;
  indicador: string;
  meta: string;
  prazo: string;
  progresso: number;
}

export const PainelIndicadores: React.FC = () => {
  const [indicadores, setIndicadores] = useState<Indicador[]>([
    {
      id: '1',
      objetivo: 'Melhorar atendimento digital',
      indicador: '% de solicitações resolvidas online',
      meta: '90%',
      prazo: 'Dez/2025',
      progresso: 65
    },
    {
      id: '2',
      objetivo: 'Reduzir retrabalho',
      indicador: 'Nº de processos devolvidos',
      meta: '−30%',
      prazo: 'Jun/2026',
      progresso: 40
    }
  ]);

  const handleChange = (id: string, campo: keyof Omit<Indicador, 'id'>, valor: string | number) => {
    setIndicadores(indicadores.map(i =>
      i.id === id ? { ...i, [campo]: valor } : i
    ));
  };

  const adicionarIndicador = () => {
    const novoIndicador: Indicador = {
      id: Date.now().toString(),
      objetivo: '',
      indicador: '',
      meta: '',
      prazo: '',
      progresso: 0
    };
    setIndicadores([...indicadores, novoIndicador]);
  };

  const removerIndicador = (id: string) => {
    setIndicadores(indicadores.filter(i => i.id !== id));
  };

  const handleExportar = () => {
    let texto = 'PAINEL DE INDICADORES DE VALOR PÚBLICO\n';
    texto += '=' .repeat(50) + '\n\n';

    indicadores.forEach((ind, index) => {
      texto += `${index + 1}. ${ind.objetivo}\n`;
      texto += `   Indicador: ${ind.indicador}\n`;
      texto += `   Meta: ${ind.meta}\n`;
      texto += `   Prazo: ${ind.prazo}\n`;
      texto += `   Progresso: ${ind.progresso}%\n\n`;
    });

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'painel-indicadores.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const getProgressoColor = (progresso: number) => {
    if (progresso >= 80) return '#22c55e';
    if (progresso >= 50) return '#eab308';
    return '#ef4444';
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>📊 Painel de Indicadores de Valor Público</h2>
        <p className="artefato-descricao">
          Traduz entregas em resultados mensuráveis. Estabelece metas claras ligadas ao valor público que o projeto pretende gerar.
        </p>
      </div>

      <div className="indicadores-grid">
        {indicadores.map((ind) => (
          <div key={ind.id} className="indicador-card">
            <div className="indicador-header">
              <input
                type="text"
                className="indicador-objetivo"
                value={ind.objetivo}
                onChange={(e) => handleChange(ind.id, 'objetivo', e.target.value)}
                placeholder="Objetivo estratégico"
              />
              <button
                className="btn-remover-small"
                onClick={() => removerIndicador(ind.id)}
                title="Remover indicador"
              >
                ✕
              </button>
            </div>

            <div className="indicador-body">
              <div className="indicador-field">
                <label>📈 Indicador:</label>
                <input
                  type="text"
                  value={ind.indicador}
                  onChange={(e) => handleChange(ind.id, 'indicador', e.target.value)}
                  placeholder="Como será medido?"
                />
              </div>

              <div className="indicador-row">
                <div className="indicador-field">
                  <label>🎯 Meta:</label>
                  <input
                    type="text"
                    value={ind.meta}
                    onChange={(e) => handleChange(ind.id, 'meta', e.target.value)}
                    placeholder="Ex: 90%"
                  />
                </div>
                <div className="indicador-field">
                  <label>📅 Prazo:</label>
                  <input
                    type="text"
                    value={ind.prazo}
                    onChange={(e) => handleChange(ind.id, 'prazo', e.target.value)}
                    placeholder="Ex: Dez/2025"
                  />
                </div>
              </div>

              <div className="indicador-field">
                <label>Progresso atual: {ind.progresso}%</label>
                <div className="progresso-container">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={ind.progresso}
                    onChange={(e) => handleChange(ind.id, 'progresso', parseInt(e.target.value))}
                    className="progresso-slider"
                  />
                  <div className="progresso-bar-bg">
                    <div
                      className="progresso-bar-fill"
                      style={{
                        width: `${ind.progresso}%`,
                        backgroundColor: getProgressoColor(ind.progresso)
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <button className="btn-adicionar" onClick={adicionarIndicador}>
        ➕ Adicionar Indicador
      </button>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Painel
        </button>
        <button className="btn-secundario" onClick={() => window.history.back()}>
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default PainelIndicadores;
