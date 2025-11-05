import React, { useState } from 'react';
import './Artefatos.css';

type StatusIndicador = 'alcancado' | 'parcial' | 'nao_alcancado' | 'em_analise';
type TipoIndicador = 'quantitativo' | 'qualitativo';

interface Indicador {
  id: string;
  indicador: string;
  tipo: TipoIndicador;
  meta: string;
  resultado: string;
  unidade: string;
  fonte: string;
  status: StatusIndicador;
  evidencias: string;
}

export const PainelResultadosImpacto: React.FC = () => {
  const [indicadores, setIndicadores] = useState<Indicador[]>([
    {
      id: '1',
      indicador: '% de metas concluídas',
      tipo: 'quantitativo',
      meta: '100',
      resultado: '95',
      unidade: '%',
      fonte: 'Dashboard Helena',
      status: 'parcial',
      evidencias: 'Relatório mensal de acompanhamento'
    },
    {
      id: '2',
      indicador: 'Economia estimada',
      tipo: 'quantitativo',
      meta: '200000',
      resultado: '215000',
      unidade: 'R$',
      fonte: 'Relatório financeiro',
      status: 'alcancado',
      evidencias: 'Nota técnica N° 15/2025'
    },
    {
      id: '3',
      indicador: 'Satisfação do público',
      tipo: 'quantitativo',
      meta: '80',
      resultado: '87',
      unidade: '%',
      fonte: 'Pesquisa online',
      status: 'alcancado',
      evidencias: 'Formulário Google Forms'
    },
    {
      id: '4',
      indicador: 'Capacidade instalada',
      tipo: 'qualitativo',
      meta: 'Alta',
      resultado: 'Média',
      unidade: '—',
      fonte: 'Avaliação institucional',
      status: 'parcial',
      evidencias: 'Parecer técnico CGRIS'
    }
  ]);

  const adicionarIndicador = () => {
    const novoIndicador: Indicador = {
      id: Date.now().toString(),
      indicador: '',
      tipo: 'quantitativo',
      meta: '',
      resultado: '',
      unidade: '',
      fonte: '',
      status: 'em_analise',
      evidencias: ''
    };
    setIndicadores([...indicadores, novoIndicador]);
  };

  const removerIndicador = (id: string) => {
    setIndicadores(indicadores.filter(i => i.id !== id));
  };

  const atualizarIndicador = (id: string, campo: keyof Indicador, valor: any) => {
    setIndicadores(indicadores.map(i => i.id === id ? { ...i, [campo]: valor } : i));
  };

  const calcularPercentualAlcance = (meta: string, resultado: string, tipo: TipoIndicador): number | null => {
    if (tipo !== 'quantitativo' || !meta || !resultado) return null;
    const metaNum = parseFloat(meta);
    const resultadoNum = parseFloat(resultado);
    if (isNaN(metaNum) || isNaN(resultadoNum) || metaNum === 0) return null;
    return (resultadoNum / metaNum) * 100;
  };

  const getStatusColor = (status: StatusIndicador): string => {
    const colors = {
      alcancado: '#198754',
      parcial: '#ffc107',
      nao_alcancado: '#dc3545',
      em_analise: '#6c757d'
    };
    return colors[status];
  };

  const getStatusLabel = (status: StatusIndicador): string => {
    const labels = {
      alcancado: '✅ Alcançado',
      parcial: '⚠️ Parcial',
      nao_alcancado: '❌ Não Alcançado',
      em_analise: '🔍 Em Análise'
    };
    return labels[status];
  };

  const formatarValor = (valor: string, unidade: string): string => {
    if (!valor) return '—';
    if (unidade === 'R$') {
      const num = parseFloat(valor);
      if (!isNaN(num)) {
        return `R$ ${num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      }
    }
    if (unidade === '%') {
      return `${valor}%`;
    }
    return `${valor} ${unidade}`;
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  PAINEL DE RESULTADOS E IMPACTO\n';
    conteudo += '  Domínio 7 - Impacto e Aprendizado\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📊 INDICADORES DE DESEMPENHO\n\n';

    indicadores.forEach((ind, index) => {
      conteudo += `${index + 1}. ${ind.indicador || '(não identificado)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   📋 Tipo:         ${ind.tipo === 'quantitativo' ? 'Quantitativo' : 'Qualitativo'}\n`;
      conteudo += `   🎯 Meta:         ${formatarValor(ind.meta, ind.unidade)}\n`;
      conteudo += `   📈 Resultado:    ${formatarValor(ind.resultado, ind.unidade)}\n`;

      const percentual = calcularPercentualAlcance(ind.meta, ind.resultado, ind.tipo);
      if (percentual !== null) {
        conteudo += `   📊 Alcance:      ${percentual.toFixed(1)}%\n`;
      }

      conteudo += `   📚 Fonte:        ${ind.fonte || '—'}\n`;
      conteudo += `   ✅ Status:       ${getStatusLabel(ind.status)}\n`;
      conteudo += `   📄 Evidências:   ${ind.evidencias || '—'}\n`;
      conteudo += '\n';
    });

    // Estatísticas gerais
    const totalAlcancado = indicadores.filter(i => i.status === 'alcancado').length;
    const totalParcial = indicadores.filter(i => i.status === 'parcial').length;
    const totalNaoAlcancado = indicadores.filter(i => i.status === 'nao_alcancado').length;
    const totalAnalise = indicadores.filter(i => i.status === 'em_analise').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📊 ESTATÍSTICAS GERAIS\n\n';
    conteudo += `Total de indicadores: ${indicadores.length}\n`;
    conteudo += `Alcançados: ${totalAlcancado} (${((totalAlcancado/indicadores.length)*100).toFixed(1)}%)\n`;
    conteudo += `Parcialmente alcançados: ${totalParcial}\n`;
    conteudo += `Não alcançados: ${totalNaoAlcancado}\n`;
    conteudo += `Em análise: ${totalAnalise}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'painel_resultados_impacto.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const totalAlcancado = indicadores.filter(i => i.status === 'alcancado').length;
  const totalParcial = indicadores.filter(i => i.status === 'parcial').length;
  const totalNaoAlcancado = indicadores.filter(i => i.status === 'nao_alcancado').length;
  const totalAnalise = indicadores.filter(i => i.status === 'em_analise').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📊 Painel de Resultados e Impacto</h2>
          <p className="artefato-descricao">
            Consolidar dados quantitativos e qualitativos sobre o desempenho do projeto.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas por Status */}
      <div className="estatisticas-stakeholders">
        <div className="stat-card stat-concluido">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-value">{totalAlcancado}</div>
            <div className="stat-label">Alcançados</div>
          </div>
        </div>
        <div className="stat-card stat-analise">
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <div className="stat-value">{totalParcial}</div>
            <div className="stat-label">Parciais</div>
          </div>
        </div>
        <div className="stat-card stat-critico">
          <div className="stat-icon">❌</div>
          <div className="stat-info">
            <div className="stat-value">{totalNaoAlcancado}</div>
            <div className="stat-label">Não Alcançados</div>
          </div>
        </div>
        <div className="stat-card stat-pendente">
          <div className="stat-icon">🔍</div>
          <div className="stat-info">
            <div className="stat-value">{totalAnalise}</div>
            <div className="stat-label">Em Análise</div>
          </div>
        </div>
      </div>

      {/* Alerta de Indicadores Não Alcançados */}
      {totalNaoAlcancado > 0 && (
        <div className="alerta-pendencias" style={{ borderLeftColor: '#dc3545' }}>
          <span className="alerta-icon">⚠️</span>
          <strong>Atenção:</strong> {totalNaoAlcancado} indicador(es) não alcançado(s). Revisar ações.
        </div>
      )}

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarIndicador}>
          ➕ Adicionar Indicador
        </button>
      </div>

      {/* Tabela de Indicadores */}
      <div className="tabela-stakeholders">
        <table>
          <thead>
            <tr>
              <th style={{ width: '20%' }}>Indicador</th>
              <th style={{ width: '8%' }}>Tipo</th>
              <th style={{ width: '10%' }}>Meta</th>
              <th style={{ width: '10%' }}>Resultado</th>
              <th style={{ width: '6%' }}>Un.</th>
              <th style={{ width: '8%' }}>Alcance</th>
              <th style={{ width: '12%' }}>Fonte</th>
              <th style={{ width: '10%' }}>Status</th>
              <th style={{ width: '13%' }}>Evidências</th>
              <th style={{ width: '3%' }}></th>
            </tr>
          </thead>
          <tbody>
            {indicadores.map((ind) => {
              const percentual = calcularPercentualAlcance(ind.meta, ind.resultado, ind.tipo);
              return (
                <tr key={ind.id}>
                  <td>
                    <input
                      type="text"
                      value={ind.indicador}
                      onChange={(e) => atualizarIndicador(ind.id, 'indicador', e.target.value)}
                      placeholder="Nome do indicador"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <select
                      value={ind.tipo}
                      onChange={(e) => atualizarIndicador(ind.id, 'tipo', e.target.value)}
                      className="select-inline"
                    >
                      <option value="quantitativo">Quantitativo</option>
                      <option value="qualitativo">Qualitativo</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="text"
                      value={ind.meta}
                      onChange={(e) => atualizarIndicador(ind.id, 'meta', e.target.value)}
                      placeholder="Meta"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={ind.resultado}
                      onChange={(e) => atualizarIndicador(ind.id, 'resultado', e.target.value)}
                      placeholder="Resultado"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={ind.unidade}
                      onChange={(e) => atualizarIndicador(ind.id, 'unidade', e.target.value)}
                      placeholder="Un."
                      className="input-inline"
                      style={{ width: '50px' }}
                    />
                  </td>
                  <td>
                    {percentual !== null ? (
                      <span style={{
                        fontWeight: 'bold',
                        color: percentual >= 100 ? '#198754' : percentual >= 80 ? '#ffc107' : '#dc3545'
                      }}>
                        {percentual.toFixed(1)}%
                      </span>
                    ) : (
                      <span style={{ color: '#6c757d' }}>—</span>
                    )}
                  </td>
                  <td>
                    <input
                      type="text"
                      value={ind.fonte}
                      onChange={(e) => atualizarIndicador(ind.id, 'fonte', e.target.value)}
                      placeholder="Fonte"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <select
                      value={ind.status}
                      onChange={(e) => atualizarIndicador(ind.id, 'status', e.target.value)}
                      className="select-inline"
                      style={{ backgroundColor: getStatusColor(ind.status), color: 'white' }}
                    >
                      <option value="alcancado">✅ Alcançado</option>
                      <option value="parcial">⚠️ Parcial</option>
                      <option value="nao_alcancado">❌ Não Alcançado</option>
                      <option value="em_analise">🔍 Em Análise</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="text"
                      value={ind.evidencias}
                      onChange={(e) => atualizarIndicador(ind.id, 'evidencias', e.target.value)}
                      placeholder="Evidências"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <button
                      className="btn-remover-table"
                      onClick={() => removerIndicador(ind.id)}
                      title="Remover"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {indicadores.length === 0 && (
        <div className="empty-state">
          <p>Nenhum indicador cadastrado. Clique em "Adicionar Indicador" para começar.</p>
        </div>
      )}
    </div>
  );
};

export default PainelResultadosImpacto;
