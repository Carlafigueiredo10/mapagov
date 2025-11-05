/**
 * Acordo de Trabalho da Equipe (Team Charter)
 * Artefato do Domínio 3 - Equipe e Responsabilidades
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface AcordoDados {
  comunicacao: string;
  tomadaDecisao: string;
  registro: string;
  conflitos: string;
  horarioReuniao: string;
  ferramentasUtilizadas: string;
}

export const AcordoTrabalho: React.FC = () => {
  const [dados, setDados] = useState<AcordoDados>({
    comunicacao: 'Canal oficial: Teams. Reunião semanal às quartas, 10h.',
    tomadaDecisao: 'Decisões técnicas: coordenação; estratégicas: comitê.',
    registro: 'Atas no SEI e notas no dashboard.',
    conflitos: 'Resolver diretamente; escalar se persistirem.',
    horarioReuniao: 'Quartas-feiras, 10h-11h',
    ferramentasUtilizadas: 'Teams, SEI, Trello'
  });

  const handleChange = (campo: keyof AcordoDados, valor: string) => {
    setDados({ ...dados, [campo]: valor });
  };

  const handleExportar = () => {
    const texto = `
ACORDO DE TRABALHO DA EQUIPE (TEAM CHARTER)
===========================================

📞 COMUNICAÇÃO
${dados.comunicacao || '(não preenchido)'}

⚖️ TOMADA DE DECISÃO
${dados.tomadaDecisao || '(não preenchido)'}

📝 REGISTRO E DOCUMENTAÇÃO
${dados.registro || '(não preenchido)'}

⚡ GESTÃO DE CONFLITOS
${dados.conflitos || '(não preenchido)'}

🕐 HORÁRIO DE REUNIÕES
${dados.horarioReuniao || '(não preenchido)'}

🛠️ FERRAMENTAS UTILIZADAS
${dados.ferramentasUtilizadas || '(não preenchido)'}

---
Data de criação: ${new Date().toLocaleDateString('pt-BR')}
    `.trim();

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'acordo-trabalho-equipe.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>📜 Acordo de Trabalho da Equipe</h2>
        <p className="artefato-descricao">
          Define rituais, regras e responsabilidades de convivência e execução.
          Estabelece como a equipe se comunica, decide, registra informações e resolve conflitos.
        </p>
      </div>

      <div className="acordo-trabalho-form">
        {/* Comunicação */}
        <div className="acordo-campo">
          <label>
            <span className="acordo-icone">📞</span>
            <strong>Comunicação</strong>
            <span className="acordo-hint">Como a equipe se comunica? Canal oficial? Frequência de reuniões?</span>
          </label>
          <textarea
            value={dados.comunicacao}
            onChange={(e) => handleChange('comunicacao', e.target.value)}
            placeholder='Ex: "Canal oficial: Teams. Reunião semanal às quartas, 10h."'
            rows={3}
          />
        </div>

        {/* Tomada de Decisão */}
        <div className="acordo-campo">
          <label>
            <span className="acordo-icone">⚖️</span>
            <strong>Tomada de Decisão</strong>
            <span className="acordo-hint">Quem decide o quê? Como as decisões são tomadas?</span>
          </label>
          <textarea
            value={dados.tomadaDecisao}
            onChange={(e) => handleChange('tomadaDecisao', e.target.value)}
            placeholder='Ex: "Decisões técnicas: coordenação; estratégicas: comitê."'
            rows={3}
          />
        </div>

        {/* Registro */}
        <div className="acordo-campo">
          <label>
            <span className="acordo-icone">📝</span>
            <strong>Registro e Documentação</strong>
            <span className="acordo-hint">Como as informações são registradas? Onde?</span>
          </label>
          <textarea
            value={dados.registro}
            onChange={(e) => handleChange('registro', e.target.value)}
            placeholder='Ex: "Atas no SEI e notas no dashboard."'
            rows={3}
          />
        </div>

        {/* Conflitos */}
        <div className="acordo-campo">
          <label>
            <span className="acordo-icone">⚡</span>
            <strong>Gestão de Conflitos</strong>
            <span className="acordo-hint">Como resolver divergências e conflitos?</span>
          </label>
          <textarea
            value={dados.conflitos}
            onChange={(e) => handleChange('conflitos', e.target.value)}
            placeholder='Ex: "Resolver diretamente; escalar se persistirem."'
            rows={3}
          />
        </div>

        {/* Horário de Reuniões */}
        <div className="acordo-campo">
          <label>
            <span className="acordo-icone">🕐</span>
            <strong>Horário de Reuniões</strong>
            <span className="acordo-hint">Quando a equipe se reúne?</span>
          </label>
          <input
            type="text"
            value={dados.horarioReuniao}
            onChange={(e) => handleChange('horarioReuniao', e.target.value)}
            placeholder='Ex: "Quartas-feiras, 10h-11h"'
          />
        </div>

        {/* Ferramentas */}
        <div className="acordo-campo">
          <label>
            <span className="acordo-icone">🛠️</span>
            <strong>Ferramentas Utilizadas</strong>
            <span className="acordo-hint">Quais sistemas e ferramentas a equipe usa?</span>
          </label>
          <input
            type="text"
            value={dados.ferramentasUtilizadas}
            onChange={(e) => handleChange('ferramentasUtilizadas', e.target.value)}
            placeholder='Ex: "Teams, SEI, Trello"'
          />
        </div>
      </div>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Acordo
        </button>
        <button className="btn-secundario" onClick={() => window.history.back()}>
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default AcordoTrabalho;
