import React, { useState } from 'react';
import './Artefatos.css';

type CategoriaLicao = 'comunicacao' | 'execucao' | 'governanca' | 'stakeholders' | 'riscos' | 'recursos';
type TipoLicao = 'boa_pratica' | 'falha' | 'recomendacao';

interface Licao {
  id: string;
  categoria: CategoriaLicao;
  tipo: TipoLicao;
  licaoAprendida: string;
  contexto: string;
  impacto: string;
  acaoMelhoria: string;
  responsavel: string;
  aplicabilidade: string;
}

export const RelatorioLicoesAprendidas: React.FC = () => {
  const [licoes, setLicoes] = useState<Licao[]>([
    {
      id: '1',
      categoria: 'comunicacao',
      tipo: 'boa_pratica',
      licaoAprendida: 'Atualizar canal oficial semanalmente mantém stakeholders engajados',
      contexto: 'Durante fase de execução, comunicação semanal evitou mal-entendidos',
      impacto: 'Redução de 40% nas dúvidas recorrentes',
      acaoMelhoria: 'Integrar comunicação semanal ao cronograma padrão',
      responsavel: 'Coordenação',
      aplicabilidade: 'Todos os projetos estratégicos'
    },
    {
      id: '2',
      categoria: 'execucao',
      tipo: 'falha',
      licaoAprendida: 'Início sem validação completa do escopo gerou retrabalho',
      contexto: 'Demandas foram alteradas após 2 meses de execução',
      impacto: 'Atraso de 3 semanas no cronograma',
      acaoMelhoria: 'Implementar checklist de pré-início com validação formal',
      responsavel: 'CGRIS',
      aplicabilidade: 'Projetos com múltiplos stakeholders'
    },
    {
      id: '3',
      categoria: 'governanca',
      tipo: 'recomendacao',
      licaoAprendida: 'Comitê executivo mensal aumenta alinhamento estratégico',
      contexto: 'Reuniões mensais permitiram ajustes rápidos de direção',
      impacto: 'Decisões mais ágeis e alinhadas com prioridades institucionais',
      acaoMelhoria: 'Institucionalizar reuniões mensais de governança',
      responsavel: 'Direção',
      aplicabilidade: 'Projetos de alta complexidade'
    }
  ]);

  const [filtroCategoria, setFiltroCategoria] = useState<CategoriaLicao | 'todos'>('todos');
  const [filtroTipo, setFiltroTipo] = useState<TipoLicao | 'todos'>('todos');

  const adicionarLicao = () => {
    const novaLicao: Licao = {
      id: Date.now().toString(),
      categoria: 'comunicacao',
      tipo: 'boa_pratica',
      licaoAprendida: '',
      contexto: '',
      impacto: '',
      acaoMelhoria: '',
      responsavel: '',
      aplicabilidade: ''
    };
    setLicoes([...licoes, novaLicao]);
  };

  const removerLicao = (id: string) => {
    setLicoes(licoes.filter(l => l.id !== id));
  };

  const atualizarLicao = (id: string, campo: keyof Licao, valor: any) => {
    setLicoes(licoes.map(l => l.id === id ? { ...l, [campo]: valor } : l));
  };

  const getCategoriaLabel = (categoria: CategoriaLicao): string => {
    const labels = {
      comunicacao: '📢 Comunicação',
      execucao: '⚙️ Execução',
      governanca: '👥 Governança',
      stakeholders: '🤝 Stakeholders',
      riscos: '⚠️ Riscos',
      recursos: '💰 Recursos'
    };
    return labels[categoria];
  };

  const getCategoriaColor = (categoria: CategoriaLicao): string => {
    const colors = {
      comunicacao: '#0d6efd',
      execucao: '#198754',
      governanca: '#6f42c1',
      stakeholders: '#fd7e14',
      riscos: '#dc3545',
      recursos: '#ffc107'
    };
    return colors[categoria];
  };

  const getTipoIcon = (tipo: TipoLicao): string => {
    const icons = {
      boa_pratica: '✅',
      falha: '❌',
      recomendacao: '💡'
    };
    return icons[tipo];
  };

  const getTipoLabel = (tipo: TipoLicao): string => {
    const labels = {
      boa_pratica: 'Boa Prática',
      falha: 'Falha',
      recomendacao: 'Recomendação'
    };
    return labels[tipo];
  };

  const getTipoColor = (tipo: TipoLicao): string => {
    const colors = {
      boa_pratica: '#198754',
      falha: '#dc3545',
      recomendacao: '#0d6efd'
    };
    return colors[tipo];
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  RELATÓRIO DE LIÇÕES APRENDIDAS\n';
    conteudo += '  Domínio 7 - Impacto e Aprendizado\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    // Agrupar por categoria
    const categorias: CategoriaLicao[] = ['comunicacao', 'execucao', 'governanca', 'stakeholders', 'riscos', 'recursos'];

    categorias.forEach(cat => {
      const licoesCat = licoes.filter(l => l.categoria === cat);
      if (licoesCat.length > 0) {
        conteudo += `\n${getCategoriaLabel(cat).toUpperCase()}\n`;
        conteudo += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

        licoesCat.forEach((licao, index) => {
          conteudo += `${index + 1}. ${getTipoIcon(licao.tipo)} ${getTipoLabel(licao.tipo).toUpperCase()}\n`;
          conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
          conteudo += `   📚 Lição Aprendida:\n`;
          conteudo += `   ${licao.licaoAprendida || '—'}\n\n`;
          conteudo += `   📋 Contexto:\n`;
          conteudo += `   ${licao.contexto || '—'}\n\n`;
          conteudo += `   📊 Impacto:\n`;
          conteudo += `   ${licao.impacto || '—'}\n\n`;
          conteudo += `   🎯 Ação de Melhoria:\n`;
          conteudo += `   ${licao.acaoMelhoria || '—'}\n\n`;
          conteudo += `   👤 Responsável: ${licao.responsavel || '—'}\n`;
          conteudo += `   🔄 Aplicabilidade: ${licao.aplicabilidade || '—'}\n`;
          conteudo += '\n';
        });
      }
    });

    // Estatísticas
    const totalBoas = licoes.filter(l => l.tipo === 'boa_pratica').length;
    const totalFalhas = licoes.filter(l => l.tipo === 'falha').length;
    const totalRecomendacoes = licoes.filter(l => l.tipo === 'recomendacao').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📊 ESTATÍSTICAS\n\n';
    conteudo += `Total de lições: ${licoes.length}\n`;
    conteudo += `Boas Práticas: ${totalBoas}\n`;
    conteudo += `Falhas: ${totalFalhas}\n`;
    conteudo += `Recomendações: ${totalRecomendacoes}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `📄 Documento oficial de encerramento do projeto\n`;
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'relatorio_licoes_aprendidas.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const licoesFiltradas = licoes.filter(l => {
    const categoriaMatch = filtroCategoria === 'todos' || l.categoria === filtroCategoria;
    const tipoMatch = filtroTipo === 'todos' || l.tipo === filtroTipo;
    return categoriaMatch && tipoMatch;
  });

  const totalBoas = licoes.filter(l => l.tipo === 'boa_pratica').length;
  const totalFalhas = licoes.filter(l => l.tipo === 'falha').length;
  const totalRecomendacoes = licoes.filter(l => l.tipo === 'recomendacao').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📝 Relatório de Lições Aprendidas</h2>
          <p className="artefato-descricao">
            Registrar sucessos, falhas e recomendações para o futuro.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas por Tipo */}
      <div className="estatisticas-stakeholders">
        <div className="stat-card stat-concluido">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-value">{totalBoas}</div>
            <div className="stat-label">Boas Práticas</div>
          </div>
        </div>
        <div className="stat-card stat-critico">
          <div className="stat-icon">❌</div>
          <div className="stat-info">
            <div className="stat-value">{totalFalhas}</div>
            <div className="stat-label">Falhas</div>
          </div>
        </div>
        <div className="stat-card stat-analise">
          <div className="stat-icon">💡</div>
          <div className="stat-info">
            <div className="stat-value">{totalRecomendacoes}</div>
            <div className="stat-label">Recomendações</div>
          </div>
        </div>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarLicao}>
          ➕ Adicionar Lição Aprendida
        </button>

        <div className="filtros-container" style={{ display: 'flex', gap: '1rem', marginLeft: 'auto' }}>
          <div className="filtro-status">
            <label>Categoria:</label>
            <select
              value={filtroCategoria}
              onChange={(e) => setFiltroCategoria(e.target.value as CategoriaLicao | 'todos')}
            >
              <option value="todos">Todas</option>
              <option value="comunicacao">📢 Comunicação</option>
              <option value="execucao">⚙️ Execução</option>
              <option value="governanca">👥 Governança</option>
              <option value="stakeholders">🤝 Stakeholders</option>
              <option value="riscos">⚠️ Riscos</option>
              <option value="recursos">💰 Recursos</option>
            </select>
          </div>

          <div className="filtro-status">
            <label>Tipo:</label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value as TipoLicao | 'todos')}
            >
              <option value="todos">Todos</option>
              <option value="boa_pratica">✅ Boa Prática</option>
              <option value="falha">❌ Falha</option>
              <option value="recomendacao">💡 Recomendação</option>
            </select>
          </div>
        </div>
      </div>

      {/* Cards de Lições */}
      <div className="comunicacao-cards-grid">
        {licoesFiltradas.map((licao) => (
          <div key={licao.id} className="comunicacao-card" style={{ borderLeft: `4px solid ${getCategoriaColor(licao.categoria)}` }}>
            <div className="comunicacao-card-header">
              <div className="canal-badge" style={{ backgroundColor: getCategoriaColor(licao.categoria) }}>
                {getCategoriaLabel(licao.categoria)}
              </div>
              <div className="canal-badge" style={{ backgroundColor: getTipoColor(licao.tipo) }}>
                {getTipoIcon(licao.tipo)} {getTipoLabel(licao.tipo)}
              </div>
              <button
                className="btn-remover-card"
                onClick={() => removerLicao(licao.id)}
                title="Remover"
              >
                ✕
              </button>
            </div>

            <div className="comunicacao-form">
              <div className="form-row" style={{ marginBottom: '0.5rem' }}>
                <div className="form-group-comunicacao">
                  <label>📋 Categoria</label>
                  <select
                    value={licao.categoria}
                    onChange={(e) => atualizarLicao(licao.id, 'categoria', e.target.value)}
                  >
                    <option value="comunicacao">📢 Comunicação</option>
                    <option value="execucao">⚙️ Execução</option>
                    <option value="governanca">👥 Governança</option>
                    <option value="stakeholders">🤝 Stakeholders</option>
                    <option value="riscos">⚠️ Riscos</option>
                    <option value="recursos">💰 Recursos</option>
                  </select>
                </div>

                <div className="form-group-comunicacao">
                  <label>🏷️ Tipo</label>
                  <select
                    value={licao.tipo}
                    onChange={(e) => atualizarLicao(licao.id, 'tipo', e.target.value)}
                  >
                    <option value="boa_pratica">✅ Boa Prática</option>
                    <option value="falha">❌ Falha</option>
                    <option value="recomendacao">💡 Recomendação</option>
                  </select>
                </div>
              </div>

              <div className="form-group-comunicacao">
                <label>📚 Lição Aprendida</label>
                <textarea
                  value={licao.licaoAprendida}
                  onChange={(e) => atualizarLicao(licao.id, 'licaoAprendida', e.target.value)}
                  placeholder="Descreva a lição aprendida de forma clara e objetiva..."
                  rows={2}
                  style={{ backgroundColor: '#ffffcc', fontWeight: 'bold' }}
                />
              </div>

              <div className="form-group-comunicacao">
                <label>📋 Contexto</label>
                <textarea
                  value={licao.contexto}
                  onChange={(e) => atualizarLicao(licao.id, 'contexto', e.target.value)}
                  placeholder="Em que situação isso ocorreu?"
                  rows={2}
                />
              </div>

              <div className="form-group-comunicacao">
                <label>📊 Impacto</label>
                <textarea
                  value={licao.impacto}
                  onChange={(e) => atualizarLicao(licao.id, 'impacto', e.target.value)}
                  placeholder="Qual foi o impacto observado?"
                  rows={2}
                />
              </div>

              <div className="form-group-comunicacao">
                <label>🎯 Ação de Melhoria</label>
                <textarea
                  value={licao.acaoMelhoria}
                  onChange={(e) => atualizarLicao(licao.id, 'acaoMelhoria', e.target.value)}
                  placeholder="O que fazer para melhorar ou evitar no futuro?"
                  rows={2}
                  style={{ backgroundColor: '#ccffcc' }}
                />
              </div>

              <div className="form-row">
                <div className="form-group-comunicacao">
                  <label>👤 Responsável</label>
                  <input
                    type="text"
                    value={licao.responsavel}
                    onChange={(e) => atualizarLicao(licao.id, 'responsavel', e.target.value)}
                    placeholder="Área ou pessoa responsável"
                  />
                </div>

                <div className="form-group-comunicacao">
                  <label>🔄 Aplicabilidade</label>
                  <input
                    type="text"
                    value={licao.aplicabilidade}
                    onChange={(e) => atualizarLicao(licao.id, 'aplicabilidade', e.target.value)}
                    placeholder="Onde pode ser aplicado?"
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {licoesFiltradas.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma lição encontrada para os filtros selecionados.</p>
        </div>
      )}
    </div>
  );
};

export default RelatorioLicoesAprendidas;
