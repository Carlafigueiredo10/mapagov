import React, { useState } from 'react';
import './Artefatos.css';

type TipoOcorrencia = 'risco_materializado' | 'oportunidade' | 'problema' | 'melhoria';
type GrauImpacto = 'baixo' | 'medio' | 'alto';

interface OcorrenciaLicao {
  id: string;
  data: string;
  tipo: TipoOcorrencia;
  ocorrencia: string;
  acaoTomada: string;
  resultado: string;
  grauImpacto: GrauImpacto;
  licaoAprendida: string;
  recomendacao: string;
}

export const RegistroLicoesAprendidas: React.FC = () => {
  const [ocorrencias, setOcorrencias] = useState<OcorrenciaLicao[]>([
    {
      id: '1',
      data: '2025-05-20',
      tipo: 'risco_materializado',
      ocorrencia: 'Sistema instável durante pico de acesso',
      acaoTomada: 'Migração emergencial para servidor backup',
      resultado: 'Sistema normalizado em 2 horas',
      grauImpacto: 'alto',
      licaoAprendida: 'Necessidade de monitoramento proativo de carga',
      recomendacao: 'Implementar rotina preventiva de balanceamento'
    },
    {
      id: '2',
      data: '2025-06-10',
      tipo: 'problema',
      ocorrencia: 'Atraso na entrega de parceiro externo',
      acaoTomada: 'Revisão de contrato e renegociação de prazos',
      resultado: 'Parcialmente resolvido - 15 dias de atraso',
      grauImpacto: 'medio',
      licaoAprendida: 'Importância de cláusulas de penalidade em contratos',
      recomendacao: 'Exigir cronograma validado antes da contratação'
    },
    {
      id: '3',
      data: '2025-06-25',
      tipo: 'oportunidade',
      ocorrencia: 'Nova ferramenta de automação disponibilizada gratuitamente',
      acaoTomada: 'Testes e integração com sistema atual',
      resultado: 'Redução de 40% no tempo de processamento',
      grauImpacto: 'alto',
      licaoAprendida: 'Benefícios da abertura para novas tecnologias',
      recomendacao: 'Manter monitoramento ativo de inovações'
    }
  ]);

  const [filtroTipo, setFiltroTipo] = useState<TipoOcorrencia | 'todos'>('todos');

  const adicionarOcorrencia = () => {
    const novaOcorrencia: OcorrenciaLicao = {
      id: Date.now().toString(),
      data: new Date().toISOString().split('T')[0],
      tipo: 'problema',
      ocorrencia: '',
      acaoTomada: '',
      resultado: '',
      grauImpacto: 'medio',
      licaoAprendida: '',
      recomendacao: ''
    };
    setOcorrencias([...ocorrencias, novaOcorrencia]);
  };

  const removerOcorrencia = (id: string) => {
    setOcorrencias(ocorrencias.filter(o => o.id !== id));
  };

  const atualizarOcorrencia = (id: string, campo: keyof OcorrenciaLicao, valor: any) => {
    setOcorrencias(ocorrencias.map(o => o.id === id ? { ...o, [campo]: valor } : o));
  };

  const getTipoIcon = (tipo: TipoOcorrencia): string => {
    const icons = {
      risco_materializado: '⚠️',
      oportunidade: '✨',
      problema: '🔧',
      melhoria: '📈'
    };
    return icons[tipo];
  };

  const getTipoLabel = (tipo: TipoOcorrencia): string => {
    const labels = {
      risco_materializado: 'Risco Materializado',
      oportunidade: 'Oportunidade',
      problema: 'Problema',
      melhoria: 'Melhoria'
    };
    return labels[tipo];
  };

  const getTipoColor = (tipo: TipoOcorrencia): string => {
    const colors = {
      risco_materializado: '#dc3545',
      oportunidade: '#198754',
      problema: '#fd7e14',
      melhoria: '#0d6efd'
    };
    return colors[tipo];
  };

  const getImpactoColor = (impacto: GrauImpacto): string => {
    const colors = {
      baixo: '#6c757d',
      medio: '#ffc107',
      alto: '#dc3545'
    };
    return colors[impacto];
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  REGISTRO DE OCORRÊNCIAS E LIÇÕES APRENDIDAS\n';
    conteudo += '  Domínio 6 - Incerteza e Contexto\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📚 HISTÓRICO DE OCORRÊNCIAS E APRENDIZADOS\n\n';

    ocorrencias
      .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
      .forEach((ocorrencia, index) => {
        conteudo += `${index + 1}. ${new Date(ocorrencia.data).toLocaleDateString('pt-BR')} - ${getTipoLabel(ocorrencia.tipo)}\n`;
        conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        conteudo += `   📋 Ocorrência:       ${ocorrencia.ocorrencia || '—'}\n`;
        conteudo += `   🎯 Ação Tomada:      ${ocorrencia.acaoTomada || '—'}\n`;
        conteudo += `   📊 Resultado:        ${ocorrencia.resultado || '—'}\n`;
        conteudo += `   ⚡ Grau de Impacto:  ${ocorrencia.grauImpacto}\n`;
        conteudo += `   💡 Lição Aprendida:  ${ocorrencia.licaoAprendida || '—'}\n`;
        conteudo += `   📝 Recomendação:     ${ocorrencia.recomendacao || '—'}\n`;
        conteudo += '\n';
      });

    // Estatísticas
    const totalRiscos = ocorrencias.filter(o => o.tipo === 'risco_materializado').length;
    const totalOportunidades = ocorrencias.filter(o => o.tipo === 'oportunidade').length;
    const totalProblemas = ocorrencias.filter(o => o.tipo === 'problema').length;
    const totalMelhorias = ocorrencias.filter(o => o.tipo === 'melhoria').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📊 ESTATÍSTICAS\n\n';
    conteudo += `Total de ocorrências registradas: ${ocorrencias.length}\n`;
    conteudo += `Riscos materializados: ${totalRiscos}\n`;
    conteudo += `Oportunidades aproveitadas: ${totalOportunidades}\n`;
    conteudo += `Problemas resolvidos: ${totalProblemas}\n`;
    conteudo += `Melhorias implementadas: ${totalMelhorias}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'registro_licoes_aprendidas.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const ocorrenciasFiltradas = filtroTipo === 'todos'
    ? ocorrencias
    : ocorrencias.filter(o => o.tipo === filtroTipo);

  const totalRiscos = ocorrencias.filter(o => o.tipo === 'risco_materializado').length;
  const totalOportunidades = ocorrencias.filter(o => o.tipo === 'oportunidade').length;
  const totalProblemas = ocorrencias.filter(o => o.tipo === 'problema').length;
  const totalMelhorias = ocorrencias.filter(o => o.tipo === 'melhoria').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📚 Registro de Ocorrências e Lições Aprendidas</h2>
          <p className="artefato-descricao">
            Documentar eventos reais, respostas e aprendizados para prevenir repetição de falhas.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas por Tipo */}
      <div className="estatisticas-stakeholders">
        <div className="stat-card" style={{ borderLeftColor: '#dc3545' }}>
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <div className="stat-value">{totalRiscos}</div>
            <div className="stat-label">Riscos Materializados</div>
          </div>
        </div>
        <div className="stat-card" style={{ borderLeftColor: '#198754' }}>
          <div className="stat-icon">✨</div>
          <div className="stat-info">
            <div className="stat-value">{totalOportunidades}</div>
            <div className="stat-label">Oportunidades</div>
          </div>
        </div>
        <div className="stat-card" style={{ borderLeftColor: '#fd7e14' }}>
          <div className="stat-icon">🔧</div>
          <div className="stat-info">
            <div className="stat-value">{totalProblemas}</div>
            <div className="stat-label">Problemas</div>
          </div>
        </div>
        <div className="stat-card" style={{ borderLeftColor: '#0d6efd' }}>
          <div className="stat-icon">📈</div>
          <div className="stat-info">
            <div className="stat-value">{totalMelhorias}</div>
            <div className="stat-label">Melhorias</div>
          </div>
        </div>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarOcorrencia}>
          ➕ Registrar Nova Ocorrência
        </button>

        <div className="filtro-status">
          <label>Filtrar por tipo:</label>
          <select
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value as TipoOcorrencia | 'todos')}
          >
            <option value="todos">Todos</option>
            <option value="risco_materializado">Risco Materializado</option>
            <option value="oportunidade">Oportunidade</option>
            <option value="problema">Problema</option>
            <option value="melhoria">Melhoria</option>
          </select>
        </div>
      </div>

      {/* Timeline de Ocorrências */}
      <div className="timeline-ocorrencias">
        {ocorrenciasFiltradas
          .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
          .map((ocorrencia) => (
            <div key={ocorrencia.id} className="timeline-item">
              <div className="timeline-marker" style={{ backgroundColor: getTipoColor(ocorrencia.tipo) }}>
                {getTipoIcon(ocorrencia.tipo)}
              </div>

              <div className="timeline-content">
                <div className="timeline-header">
                  <div className="timeline-date">
                    📅 {new Date(ocorrencia.data).toLocaleDateString('pt-BR')}
                  </div>
                  <div className="timeline-tipo" style={{ backgroundColor: getTipoColor(ocorrencia.tipo) }}>
                    {getTipoIcon(ocorrencia.tipo)} {getTipoLabel(ocorrencia.tipo)}
                  </div>
                  <button
                    className="btn-remover-small"
                    onClick={() => removerOcorrencia(ocorrencia.id)}
                    title="Remover"
                  >
                    ✕
                  </button>
                </div>

                <div className="timeline-form">
                  <div className="form-group-timeline">
                    <label>📋 Ocorrência</label>
                    <textarea
                      value={ocorrencia.ocorrencia}
                      onChange={(e) => atualizarOcorrencia(ocorrencia.id, 'ocorrencia', e.target.value)}
                      placeholder="Descreva o que aconteceu..."
                      rows={2}
                    />
                  </div>

                  <div className="form-row-timeline">
                    <div className="form-group-timeline">
                      <label>📅 Data</label>
                      <input
                        type="date"
                        value={ocorrencia.data}
                        onChange={(e) => atualizarOcorrencia(ocorrencia.id, 'data', e.target.value)}
                      />
                    </div>

                    <div className="form-group-timeline">
                      <label>🏷️ Tipo</label>
                      <select
                        value={ocorrencia.tipo}
                        onChange={(e) => atualizarOcorrencia(ocorrencia.id, 'tipo', e.target.value)}
                      >
                        <option value="risco_materializado">⚠️ Risco Materializado</option>
                        <option value="oportunidade">✨ Oportunidade</option>
                        <option value="problema">🔧 Problema</option>
                        <option value="melhoria">📈 Melhoria</option>
                      </select>
                    </div>

                    <div className="form-group-timeline">
                      <label>⚡ Grau de Impacto</label>
                      <select
                        value={ocorrencia.grauImpacto}
                        onChange={(e) => atualizarOcorrencia(ocorrencia.id, 'grauImpacto', e.target.value)}
                        style={{ backgroundColor: getImpactoColor(ocorrencia.grauImpacto), color: 'white' }}
                      >
                        <option value="baixo">Baixo</option>
                        <option value="medio">Médio</option>
                        <option value="alto">Alto</option>
                      </select>
                    </div>
                  </div>

                  <div className="form-group-timeline">
                    <label>🎯 Ação Tomada</label>
                    <textarea
                      value={ocorrencia.acaoTomada}
                      onChange={(e) => atualizarOcorrencia(ocorrencia.id, 'acaoTomada', e.target.value)}
                      placeholder="O que foi feito para resolver?"
                      rows={2}
                    />
                  </div>

                  <div className="form-group-timeline">
                    <label>📊 Resultado Obtido</label>
                    <textarea
                      value={ocorrencia.resultado}
                      onChange={(e) => atualizarOcorrencia(ocorrencia.id, 'resultado', e.target.value)}
                      placeholder="Qual foi o resultado da ação tomada?"
                      rows={2}
                    />
                  </div>

                  <div className="licao-aprendida-section">
                    <div className="form-group-timeline">
                      <label>💡 Lição Aprendida</label>
                      <textarea
                        value={ocorrencia.licaoAprendida}
                        onChange={(e) => atualizarOcorrencia(ocorrencia.id, 'licaoAprendida', e.target.value)}
                        placeholder="Qual foi o principal aprendizado?"
                        rows={2}
                        className="licao-destaque"
                      />
                    </div>

                    <div className="form-group-timeline">
                      <label>📝 Recomendação para o Futuro</label>
                      <textarea
                        value={ocorrencia.recomendacao}
                        onChange={(e) => atualizarOcorrencia(ocorrencia.id, 'recomendacao', e.target.value)}
                        placeholder="O que deve ser feito diferente no futuro?"
                        rows={2}
                        className="recomendacao-destaque"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
      </div>

      {ocorrenciasFiltradas.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma ocorrência registrada para o filtro selecionado.</p>
        </div>
      )}

      <style>{`
        .timeline-ocorrencias {
          margin-top: 30px;
          position: relative;
        }

        .timeline-ocorrencias::before {
          content: '';
          position: absolute;
          left: 20px;
          top: 0;
          bottom: 0;
          width: 2px;
          background: #dee2e6;
        }

        .timeline-item {
          position: relative;
          margin-bottom: 30px;
          padding-left: 60px;
        }

        .timeline-marker {
          position: absolute;
          left: 8px;
          top: 20px;
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          border: 3px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .timeline-content {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .timeline-header {
          display: flex;
          align-items: center;
          gap: 15px;
          margin-bottom: 20px;
          flex-wrap: wrap;
        }

        .timeline-date {
          font-weight: 600;
          color: #495057;
          font-size: 14px;
        }

        .timeline-tipo {
          padding: 6px 12px;
          border-radius: 16px;
          color: white;
          font-size: 13px;
          font-weight: 600;
        }

        .timeline-form {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .form-group-timeline {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .form-group-timeline label {
          font-weight: 600;
          font-size: 13px;
          color: #495057;
        }

        .form-group-timeline input,
        .form-group-timeline select,
        .form-group-timeline textarea {
          padding: 10px;
          border: 1px solid #ced4da;
          border-radius: 6px;
          font-size: 14px;
          font-family: inherit;
        }

        .form-group-timeline textarea {
          resize: vertical;
        }

        .form-row-timeline {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 15px;
        }

        .licao-aprendida-section {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 6px;
          border-left: 4px solid #0d6efd;
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .licao-destaque {
          background: #fff3cd !important;
          border: 1px solid #ffc107 !important;
        }

        .recomendacao-destaque {
          background: #d1e7dd !important;
          border: 1px solid #198754 !important;
        }

        @media (max-width: 768px) {
          .form-row-timeline {
            grid-template-columns: 1fr;
          }

          .timeline-item {
            padding-left: 50px;
          }
        }
      `}</style>
    </div>
  );
};

export default RegistroLicoesAprendidas;
