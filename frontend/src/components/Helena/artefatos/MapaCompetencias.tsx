/**
 * Mapa de Competências do Projeto
 * Artefato do Domínio 3 - Equipe e Responsabilidades
 */

import React, { useState } from 'react';
import './Artefatos.css';

type NivelCompetencia = 'basico' | 'intermediario' | 'avancado';

interface Competencia {
  id: string;
  competencia: string;
  nivelAtual: NivelCompetencia;
  nivelNecessario: NivelCompetencia;
  acaoProposta: string;
}

const nivelParaNumero = (nivel: NivelCompetencia): number => {
  const mapa = { basico: 33, intermediario: 66, avancado: 100 };
  return mapa[nivel];
};

const nivelParaTexto = (nivel: NivelCompetencia): string => {
  const mapa = { basico: 'Básico', intermediario: 'Intermediário', avancado: 'Avançado' };
  return mapa[nivel];
};

export const MapaCompetencias: React.FC = () => {
  const [competencias, setCompetencias] = useState<Competencia[]>([
    {
      id: '1',
      competencia: 'Análise de dados',
      nivelAtual: 'basico',
      nivelNecessario: 'intermediario',
      acaoProposta: 'Capacitação interna'
    },
    {
      id: '2',
      competencia: 'Gestão de riscos',
      nivelAtual: 'intermediario',
      nivelNecessario: 'avancado',
      acaoProposta: 'Mentoria CGRIS'
    },
    {
      id: '3',
      competencia: 'Comunicação institucional',
      nivelAtual: 'avancado',
      nivelNecessario: 'avancado',
      acaoProposta: 'Manter boas práticas'
    }
  ]);

  const handleChange = (id: string, campo: keyof Omit<Competencia, 'id'>, valor: string) => {
    setCompetencias(competencias.map(c =>
      c.id === id ? { ...c, [campo]: valor } : c
    ));
  };

  const adicionarCompetencia = () => {
    const novaCompetencia: Competencia = {
      id: Date.now().toString(),
      competencia: '',
      nivelAtual: 'basico',
      nivelNecessario: 'intermediario',
      acaoProposta: ''
    };
    setCompetencias([...competencias, novaCompetencia]);
  };

  const removerCompetencia = (id: string) => {
    setCompetencias(competencias.filter(c => c.id !== id));
  };

  const handleExportar = () => {
    let texto = 'MAPA DE COMPETÊNCIAS DO PROJETO\n';
    texto += '='.repeat(60) + '\n\n';

    competencias.forEach((comp, index) => {
      texto += `${index + 1}. ${comp.competencia}\n`;
      texto += `   Nível Atual: ${nivelParaTexto(comp.nivelAtual)}\n`;
      texto += `   Necessário: ${nivelParaTexto(comp.nivelNecessario)}\n`;
      texto += `   Ação Proposta: ${comp.acaoProposta}\n\n`;
    });

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'mapa-competencias.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const getGapColor = (atual: NivelCompetencia, necessario: NivelCompetencia) => {
    const gap = nivelParaNumero(necessario) - nivelParaNumero(atual);
    if (gap === 0) return '#22c55e'; // Verde
    if (gap > 0 && gap <= 33) return '#eab308'; // Amarelo
    return '#ef4444'; // Vermelho
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>🎯 Mapa de Competências do Projeto</h2>
        <p className="artefato-descricao">
          Identifica forças e lacunas técnicas da equipe, permitindo planejar capacitações.
          Compara o nível atual de cada competência com o nível necessário para o projeto.
        </p>
      </div>

      <div className="competencias-grid">
        {competencias.map((comp) => (
          <div key={comp.id} className="competencia-card">
            <div className="competencia-header">
              <input
                type="text"
                className="competencia-nome"
                value={comp.competencia}
                onChange={(e) => handleChange(comp.id, 'competencia', e.target.value)}
                placeholder="Nome da competência"
              />
              <button
                className="btn-remover-small"
                onClick={() => removerCompetencia(comp.id)}
                title="Remover competência"
              >
                ✕
              </button>
            </div>

            <div className="competencia-body">
              {/* Nível Atual */}
              <div className="competencia-nivel">
                <label>📊 Nível Atual:</label>
                <select
                  value={comp.nivelAtual}
                  onChange={(e) => handleChange(comp.id, 'nivelAtual', e.target.value)}
                >
                  <option value="basico">Básico</option>
                  <option value="intermediario">Intermediário</option>
                  <option value="avancado">Avançado</option>
                </select>
                <div className="nivel-bar-container">
                  <div
                    className="nivel-bar"
                    style={{
                      width: `${nivelParaNumero(comp.nivelAtual)}%`,
                      backgroundColor: '#94a3b8'
                    }}
                  />
                </div>
              </div>

              {/* Nível Necessário */}
              <div className="competencia-nivel">
                <label>🎯 Nível Necessário:</label>
                <select
                  value={comp.nivelNecessario}
                  onChange={(e) => handleChange(comp.id, 'nivelNecessario', e.target.value)}
                >
                  <option value="basico">Básico</option>
                  <option value="intermediario">Intermediário</option>
                  <option value="avancado">Avançado</option>
                </select>
                <div className="nivel-bar-container">
                  <div
                    className="nivel-bar"
                    style={{
                      width: `${nivelParaNumero(comp.nivelNecessario)}%`,
                      backgroundColor: getGapColor(comp.nivelAtual, comp.nivelNecessario)
                    }}
                  />
                </div>
              </div>

              {/* Ação Proposta */}
              <div className="competencia-acao">
                <label>💡 Ação Proposta:</label>
                <input
                  type="text"
                  value={comp.acaoProposta}
                  onChange={(e) => handleChange(comp.id, 'acaoProposta', e.target.value)}
                  placeholder="Como desenvolver essa competência?"
                />
              </div>

              {/* Indicador de Gap */}
              {nivelParaNumero(comp.nivelNecessario) > nivelParaNumero(comp.nivelAtual) && (
                <div className="competencia-alert">
                  ⚠️ Gap de desenvolvimento identificado
                </div>
              )}
              {nivelParaNumero(comp.nivelNecessario) === nivelParaNumero(comp.nivelAtual) && (
                <div className="competencia-success">
                  ✅ Nível adequado
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <button className="btn-adicionar" onClick={adicionarCompetencia}>
        ➕ Adicionar Competência
      </button>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Mapa de Competências
        </button>
        <button className="btn-secundario" onClick={() => window.history.back()}>
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default MapaCompetencias;
