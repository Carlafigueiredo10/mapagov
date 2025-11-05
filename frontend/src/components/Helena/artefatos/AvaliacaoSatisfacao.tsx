import React, { useState } from 'react';
import './Artefatos.css';

type GrupoConsultado = 'servidores' | 'gestores' | 'beneficiarios' | 'parceiros' | 'stakeholders_externos';
type TipoInstrumento = 'pesquisa_digital' | 'entrevista' | 'grupo_focal' | 'nps' | 'likert';
type NivelSatisfacao = 'muito_satisfeito' | 'satisfeito' | 'neutro' | 'insatisfeito' | 'muito_insatisfeito';

interface Avaliacao {
  id: string;
  grupoConsultado: GrupoConsultado;
  instrumento: TipoInstrumento;
  dataColeta: string;
  participantes: string;
  nivelSatisfacao: NivelSatisfacao;
  percentualPositivo: string;
  principalInsight: string;
  acaoDecorrente: string;
}

export const AvaliacaoSatisfacao: React.FC = () => {
  const [avaliacoes, setAvaliacoes] = useState<Avaliacao[]>([
    {
      id: '1',
      grupoConsultado: 'servidores',
      instrumento: 'pesquisa_digital',
      dataColeta: '2025-03-15',
      participantes: '45',
      nivelSatisfacao: 'satisfeito',
      percentualPositivo: '85',
      principalInsight: 'Valorizar feedback contínuo durante o projeto',
      acaoDecorrente: 'Institucionalizar reuniões semanais de alinhamento'
    },
    {
      id: '2',
      grupoConsultado: 'gestores',
      instrumento: 'entrevista',
      dataColeta: '2025-03-20',
      participantes: '8',
      nivelSatisfacao: 'muito_satisfeito',
      percentualPositivo: '90',
      principalInsight: 'Melhorar comunicação de resultados intermediários',
      acaoDecorrente: 'Criar dashboard executivo com atualização automática'
    },
    {
      id: '3',
      grupoConsultado: 'beneficiarios',
      instrumento: 'nps',
      dataColeta: '2025-03-25',
      participantes: '120',
      nivelSatisfacao: 'satisfeito',
      percentualPositivo: '78',
      principalInsight: 'Simplificar linguagem técnica nos canais de atendimento',
      acaoDecorrente: 'Revisar manual do usuário com linguagem acessível'
    }
  ]);

  const adicionarAvaliacao = () => {
    const novaAvaliacao: Avaliacao = {
      id: Date.now().toString(),
      grupoConsultado: 'servidores',
      instrumento: 'pesquisa_digital',
      dataColeta: '',
      participantes: '',
      nivelSatisfacao: 'neutro',
      percentualPositivo: '',
      principalInsight: '',
      acaoDecorrente: ''
    };
    setAvaliacoes([...avaliacoes, novaAvaliacao]);
  };

  const removerAvaliacao = (id: string) => {
    setAvaliacoes(avaliacoes.filter(a => a.id !== id));
  };

  const atualizarAvaliacao = (id: string, campo: keyof Avaliacao, valor: any) => {
    setAvaliacoes(avaliacoes.map(a => a.id === id ? { ...a, [campo]: valor } : a));
  };

  const getGrupoIcon = (grupo: GrupoConsultado): string => {
    const icons = {
      servidores: '👥',
      gestores: '👔',
      beneficiarios: '🙋',
      parceiros: '🤝',
      stakeholders_externos: '🌐'
    };
    return icons[grupo];
  };

  const getGrupoLabel = (grupo: GrupoConsultado): string => {
    const labels = {
      servidores: 'Servidores',
      gestores: 'Gestores',
      beneficiarios: 'Beneficiários',
      parceiros: 'Parceiros',
      stakeholders_externos: 'Stakeholders Externos'
    };
    return labels[grupo];
  };

  const getInstrumentoLabel = (instrumento: TipoInstrumento): string => {
    const labels = {
      pesquisa_digital: 'Pesquisa Digital',
      entrevista: 'Entrevista',
      grupo_focal: 'Grupo Focal',
      nps: 'NPS',
      likert: 'Escala Likert'
    };
    return labels[instrumento];
  };

  const getSatisfacaoColor = (nivel: NivelSatisfacao): string => {
    const colors = {
      muito_satisfeito: '#198754',
      satisfeito: '#20c997',
      neutro: '#ffc107',
      insatisfeito: '#fd7e14',
      muito_insatisfeito: '#dc3545'
    };
    return colors[nivel];
  };

  const getSatisfacaoLabel = (nivel: NivelSatisfacao): string => {
    const labels = {
      muito_satisfeito: '😄 Muito Satisfeito',
      satisfeito: '🙂 Satisfeito',
      neutro: '😐 Neutro',
      insatisfeito: '🙁 Insatisfeito',
      muito_insatisfeito: '😞 Muito Insatisfeito'
    };
    return labels[nivel];
  };

  const calcularMediaSatisfacao = (): number => {
    if (avaliacoes.length === 0) return 0;
    const valores = {
      muito_satisfeito: 5,
      satisfeito: 4,
      neutro: 3,
      insatisfeito: 2,
      muito_insatisfeito: 1
    };
    const soma = avaliacoes.reduce((acc, av) => acc + valores[av.nivelSatisfacao], 0);
    return (soma / avaliacoes.length);
  };

  const calcularPercentualGeral = (): number => {
    if (avaliacoes.length === 0) return 0;
    const avaliacoesComPercentual = avaliacoes.filter(a => a.percentualPositivo);
    if (avaliacoesComPercentual.length === 0) return 0;
    const soma = avaliacoesComPercentual.reduce((acc, av) => acc + parseFloat(av.percentualPositivo || '0'), 0);
    return soma / avaliacoesComPercentual.length;
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  AVALIAÇÃO DE SATISFAÇÃO E VALOR PÚBLICO PERCEBIDO\n';
    conteudo += '  Domínio 7 - Impacto e Aprendizado\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '⭐ PERCEPÇÃO DOS GRUPOS CONSULTADOS\n\n';

    avaliacoes.forEach((av, index) => {
      conteudo += `${index + 1}. ${getGrupoIcon(av.grupoConsultado)} ${getGrupoLabel(av.grupoConsultado).toUpperCase()}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   📋 Instrumento:           ${getInstrumentoLabel(av.instrumento)}\n`;
      conteudo += `   📅 Data de Coleta:        ${av.dataColeta ? new Date(av.dataColeta).toLocaleDateString('pt-BR') : '—'}\n`;
      conteudo += `   👥 Participantes:         ${av.participantes || '—'}\n`;
      conteudo += `   😄 Nível de Satisfação:   ${getSatisfacaoLabel(av.nivelSatisfacao)}\n`;
      conteudo += `   📊 % Percepção Positiva:  ${av.percentualPositivo ? av.percentualPositivo + '%' : '—'}\n`;
      conteudo += `   💡 Principal Insight:\n`;
      conteudo += `      ${av.principalInsight || '—'}\n`;
      conteudo += `   🎯 Ação Decorrente:\n`;
      conteudo += `      ${av.acaoDecorrente || '—'}\n`;
      conteudo += '\n';
    });

    // Estatísticas gerais
    const mediaSatisfacao = calcularMediaSatisfacao();
    const percentualGeral = calcularPercentualGeral();
    const totalMuitoSatisfeito = avaliacoes.filter(a => a.nivelSatisfacao === 'muito_satisfeito').length;
    const totalSatisfeito = avaliacoes.filter(a => a.nivelSatisfacao === 'satisfeito').length;
    const totalNegativo = avaliacoes.filter(a => a.nivelSatisfacao === 'insatisfeito' || a.nivelSatisfacao === 'muito_insatisfeito').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📊 ESTATÍSTICAS GERAIS\n\n';
    conteudo += `Total de avaliações: ${avaliacoes.length}\n`;
    conteudo += `Média de satisfação: ${mediaSatisfacao.toFixed(2)}/5.0\n`;
    conteudo += `% Geral de percepção positiva: ${percentualGeral.toFixed(1)}%\n\n`;
    conteudo += `Muito Satisfeitos: ${totalMuitoSatisfeito}\n`;
    conteudo += `Satisfeitos: ${totalSatisfeito}\n`;
    conteudo += `Insatisfeitos: ${totalNegativo}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📄 Relatório de percepção de valor público\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'avaliacao_satisfacao.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const mediaSatisfacao = calcularMediaSatisfacao();
  const percentualGeral = calcularPercentualGeral();
  const totalMuitoSatisfeito = avaliacoes.filter(a => a.nivelSatisfacao === 'muito_satisfeito').length;
  const totalSatisfeito = avaliacoes.filter(a => a.nivelSatisfacao === 'satisfeito').length;
  const totalNegativo = avaliacoes.filter(a => a.nivelSatisfacao === 'insatisfeito' || a.nivelSatisfacao === 'muito_insatisfeito').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>⭐ Avaliação de Satisfação e Valor Público Percebido</h2>
          <p className="artefato-descricao">
            Coletar percepções de beneficiários, parceiros e equipe sobre o projeto.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas Gerais */}
      <div className="estatisticas-stakeholders">
        <div className="stat-card stat-concluido">
          <div className="stat-icon">😄</div>
          <div className="stat-info">
            <div className="stat-value">{totalMuitoSatisfeito}</div>
            <div className="stat-label">Muito Satisfeitos</div>
          </div>
        </div>
        <div className="stat-card stat-analise">
          <div className="stat-icon">🙂</div>
          <div className="stat-info">
            <div className="stat-value">{totalSatisfeito}</div>
            <div className="stat-label">Satisfeitos</div>
          </div>
        </div>
        <div className="stat-card stat-critico">
          <div className="stat-icon">🙁</div>
          <div className="stat-info">
            <div className="stat-value">{totalNegativo}</div>
            <div className="stat-label">Insatisfeitos</div>
          </div>
        </div>
        <div className="stat-card" style={{ backgroundColor: '#0d6efd' }}>
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <div className="stat-value">{percentualGeral.toFixed(1)}%</div>
            <div className="stat-label">Percepção Positiva</div>
          </div>
        </div>
      </div>

      {/* Indicador de Média Geral */}
      <div style={{
        padding: '1.5rem',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        marginBottom: '1.5rem',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '0.9rem', color: '#6c757d', marginBottom: '0.5rem' }}>
          Média Geral de Satisfação
        </div>
        <div style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          color: mediaSatisfacao >= 4 ? '#198754' : mediaSatisfacao >= 3 ? '#ffc107' : '#dc3545'
        }}>
          {mediaSatisfacao.toFixed(2)} / 5.0
        </div>
        <div style={{
          width: '100%',
          height: '12px',
          backgroundColor: '#e9ecef',
          borderRadius: '6px',
          marginTop: '1rem',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${(mediaSatisfacao / 5) * 100}%`,
            height: '100%',
            backgroundColor: mediaSatisfacao >= 4 ? '#198754' : mediaSatisfacao >= 3 ? '#ffc107' : '#dc3545',
            transition: 'width 0.3s ease'
          }} />
        </div>
      </div>

      {/* Alerta de Insatisfação */}
      {totalNegativo > 0 && (
        <div className="alerta-pendencias" style={{ borderLeftColor: '#dc3545' }}>
          <span className="alerta-icon">⚠️</span>
          <strong>Atenção:</strong> {totalNegativo} avaliação(ões) com percepção negativa. Analisar insights.
        </div>
      )}

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarAvaliacao}>
          ➕ Adicionar Avaliação
        </button>
      </div>

      {/* Cards de Avaliação */}
      <div className="comunicacao-cards-grid">
        {avaliacoes.map((av) => (
          <div
            key={av.id}
            className="comunicacao-card"
            style={{ borderLeft: `4px solid ${getSatisfacaoColor(av.nivelSatisfacao)}` }}
          >
            <div className="comunicacao-card-header">
              <div className="canal-badge" style={{ backgroundColor: '#0d6efd' }}>
                {getGrupoIcon(av.grupoConsultado)} {getGrupoLabel(av.grupoConsultado)}
              </div>
              <div className="canal-badge" style={{ backgroundColor: getSatisfacaoColor(av.nivelSatisfacao) }}>
                {getSatisfacaoLabel(av.nivelSatisfacao)}
              </div>
              <button
                className="btn-remover-card"
                onClick={() => removerAvaliacao(av.id)}
                title="Remover"
              >
                ✕
              </button>
            </div>

            <div className="comunicacao-form">
              <div className="form-row">
                <div className="form-group-comunicacao">
                  <label>👥 Grupo Consultado</label>
                  <select
                    value={av.grupoConsultado}
                    onChange={(e) => atualizarAvaliacao(av.id, 'grupoConsultado', e.target.value)}
                  >
                    <option value="servidores">👥 Servidores</option>
                    <option value="gestores">👔 Gestores</option>
                    <option value="beneficiarios">🙋 Beneficiários</option>
                    <option value="parceiros">🤝 Parceiros</option>
                    <option value="stakeholders_externos">🌐 Stakeholders Externos</option>
                  </select>
                </div>

                <div className="form-group-comunicacao">
                  <label>📋 Instrumento</label>
                  <select
                    value={av.instrumento}
                    onChange={(e) => atualizarAvaliacao(av.id, 'instrumento', e.target.value)}
                  >
                    <option value="pesquisa_digital">Pesquisa Digital</option>
                    <option value="entrevista">Entrevista</option>
                    <option value="grupo_focal">Grupo Focal</option>
                    <option value="nps">NPS</option>
                    <option value="likert">Escala Likert</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group-comunicacao">
                  <label>📅 Data de Coleta</label>
                  <input
                    type="date"
                    value={av.dataColeta}
                    onChange={(e) => atualizarAvaliacao(av.id, 'dataColeta', e.target.value)}
                  />
                </div>

                <div className="form-group-comunicacao">
                  <label>👥 Participantes</label>
                  <input
                    type="text"
                    value={av.participantes}
                    onChange={(e) => atualizarAvaliacao(av.id, 'participantes', e.target.value)}
                    placeholder="Número de participantes"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group-comunicacao">
                  <label>😄 Nível de Satisfação</label>
                  <select
                    value={av.nivelSatisfacao}
                    onChange={(e) => atualizarAvaliacao(av.id, 'nivelSatisfacao', e.target.value)}
                    style={{ backgroundColor: getSatisfacaoColor(av.nivelSatisfacao), color: 'white' }}
                  >
                    <option value="muito_satisfeito">😄 Muito Satisfeito</option>
                    <option value="satisfeito">🙂 Satisfeito</option>
                    <option value="neutro">😐 Neutro</option>
                    <option value="insatisfeito">🙁 Insatisfeito</option>
                    <option value="muito_insatisfeito">😞 Muito Insatisfeito</option>
                  </select>
                </div>

                <div className="form-group-comunicacao">
                  <label>📊 % Percepção Positiva</label>
                  <input
                    type="text"
                    value={av.percentualPositivo}
                    onChange={(e) => atualizarAvaliacao(av.id, 'percentualPositivo', e.target.value)}
                    placeholder="Ex: 85"
                  />
                </div>
              </div>

              <div className="form-group-comunicacao">
                <label>💡 Principal Insight</label>
                <textarea
                  value={av.principalInsight}
                  onChange={(e) => atualizarAvaliacao(av.id, 'principalInsight', e.target.value)}
                  placeholder="Qual foi o principal aprendizado extraído desta avaliação?"
                  rows={2}
                  style={{ backgroundColor: '#ffffcc' }}
                />
              </div>

              <div className="form-group-comunicacao">
                <label>🎯 Ação Decorrente</label>
                <textarea
                  value={av.acaoDecorrente}
                  onChange={(e) => atualizarAvaliacao(av.id, 'acaoDecorrente', e.target.value)}
                  placeholder="Que ação ou melhoria será implementada com base neste feedback?"
                  rows={2}
                  style={{ backgroundColor: '#ccffcc' }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {avaliacoes.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma avaliação cadastrada. Clique em "Adicionar Avaliação" para começar.</p>
        </div>
      )}
    </div>
  );
};

export default AvaliacaoSatisfacao;
