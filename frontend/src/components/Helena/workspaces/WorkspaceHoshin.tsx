/**
 * Workspace Hoshin Kanri
 * Interface para desdobramento de diretrizes estratégicas
 */
import React, { useState } from 'react';
import Card from '../../ui/Card';
import Button from '../../ui/Button';
import Badge from '../../ui/Badge';
import './WorkspaceHoshin.css';

interface DiretrizHoshin {
  id: string;
  diretriz: string;
  meta: string;
  indicador: string;
  acao: string;
  responsavel: string;
  prazo: string;
  status: 'planejado' | 'em_andamento' | 'concluido' | 'atrasado';
}

interface WorkspaceHoshinProps {
  onFechar?: () => void;
  onSalvar?: (dados: any) => void;
}

export const WorkspaceHoshin: React.FC<WorkspaceHoshinProps> = ({
  onFechar,
  onSalvar
}) => {
  const [diretrizes, setDiretrizes] = useState<DiretrizHoshin[]>([]);
  const [novaDiretriz, setNovaDiretriz] = useState<Partial<DiretrizHoshin>>({
    diretriz: '',
    meta: '',
    indicador: '',
    acao: '',
    responsavel: '',
    prazo: '',
    status: 'planejado'
  });
  const [editando, setEditando] = useState<string | null>(null);

  const adicionarDiretriz = () => {
    if (!novaDiretriz.diretriz || !novaDiretriz.meta) {
      alert('Preencha ao menos a Diretriz e a Meta');
      return;
    }

    const diretriz: DiretrizHoshin = {
      id: Date.now().toString(),
      diretriz: novaDiretriz.diretriz || '',
      meta: novaDiretriz.meta || '',
      indicador: novaDiretriz.indicador || '',
      acao: novaDiretriz.acao || '',
      responsavel: novaDiretriz.responsavel || '',
      prazo: novaDiretriz.prazo || '',
      status: novaDiretriz.status || 'planejado'
    };

    setDiretrizes([...diretrizes, diretriz]);
    setNovaDiretriz({
      diretriz: '',
      meta: '',
      indicador: '',
      acao: '',
      responsavel: '',
      prazo: '',
      status: 'planejado'
    });
  };

  const removerDiretriz = (id: string) => {
    setDiretrizes(diretrizes.filter(d => d.id !== id));
  };

  const atualizarStatus = (id: string, novoStatus: DiretrizHoshin['status']) => {
    setDiretrizes(diretrizes.map(d =>
      d.id === id ? { ...d, status: novoStatus } : d
    ));
  };

  const salvarWorkspace = () => {
    if (onSalvar) {
      onSalvar({ diretrizes });
    }
    alert('Matriz Hoshin Kanri salva com sucesso!');
  };

  const getStatusColor = (status: DiretrizHoshin['status']) => {
    const cores = {
      planejado: '#9E9E9E',
      em_andamento: '#3498DB',
      concluido: '#27AE60',
      atrasado: '#E74C3C'
    };
    return cores[status];
  };

  const getStatusLabel = (status: DiretrizHoshin['status']) => {
    const labels = {
      planejado: 'Planejado',
      em_andamento: 'Em Andamento',
      concluido: 'Concluído',
      atrasado: 'Atrasado'
    };
    return labels[status];
  };

  return (
    <div className="workspace-hoshin">
      {/* Header */}
      <div className="workspace-hoshin-header">
        <div className="workspace-hoshin-title">
          <span className="workspace-hoshin-icon">🧭</span>
          <div>
            <h2>Matriz Hoshin Kanri</h2>
            <p>Desdobramento de Diretrizes Estratégicas</p>
          </div>
        </div>
        <div className="workspace-hoshin-actions">
          <Button variant="outline" onClick={onFechar}>
            Fechar
          </Button>
          <Button variant="primary" onClick={salvarWorkspace}>
            💾 Salvar Matriz
          </Button>
        </div>
      </div>

      {/* Estatísticas */}
      <div className="workspace-hoshin-stats">
        <Card variant="glass" className="hoshin-stat-card">
          <div className="stat-content">
            <span className="stat-icon">📋</span>
            <div>
              <div className="stat-value">{diretrizes.length}</div>
              <div className="stat-label">Diretrizes</div>
            </div>
          </div>
        </Card>
        <Card variant="glass" className="hoshin-stat-card">
          <div className="stat-content">
            <span className="stat-icon">🎯</span>
            <div>
              <div className="stat-value">
                {diretrizes.filter(d => d.status === 'em_andamento').length}
              </div>
              <div className="stat-label">Em Andamento</div>
            </div>
          </div>
        </Card>
        <Card variant="glass" className="hoshin-stat-card">
          <div className="stat-content">
            <span className="stat-icon">✅</span>
            <div>
              <div className="stat-value">
                {diretrizes.filter(d => d.status === 'concluido').length}
              </div>
              <div className="stat-label">Concluídas</div>
            </div>
          </div>
        </Card>
        <Card variant="glass" className="hoshin-stat-card">
          <div className="stat-content">
            <span className="stat-icon">⚠️</span>
            <div>
              <div className="stat-value">
                {diretrizes.filter(d => d.status === 'atrasado').length}
              </div>
              <div className="stat-label">Atrasadas</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Formulário de Nova Diretriz */}
      <Card variant="glass" className="workspace-hoshin-form">
        <h3>➕ Adicionar Nova Diretriz</h3>

        <div className="form-grid">
          <div className="form-group">
            <label>Diretriz Estratégica *</label>
            <input
              type="text"
              value={novaDiretriz.diretriz}
              onChange={(e) => setNovaDiretriz({ ...novaDiretriz, diretriz: e.target.value })}
              placeholder="Ex: Fortalecer a governança digital"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Meta Desdobrada *</label>
            <input
              type="text"
              value={novaDiretriz.meta}
              onChange={(e) => setNovaDiretriz({ ...novaDiretriz, meta: e.target.value })}
              placeholder="Ex: 100% dos sistemas integrados ao DataLake até 2026"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Indicador</label>
            <input
              type="text"
              value={novaDiretriz.indicador}
              onChange={(e) => setNovaDiretriz({ ...novaDiretriz, indicador: e.target.value })}
              placeholder="Ex: % de sistemas integrados"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Ação de Apoio</label>
            <input
              type="text"
              value={novaDiretriz.acao}
              onChange={(e) => setNovaDiretriz({ ...novaDiretriz, acao: e.target.value })}
              placeholder="Ex: Implantar API de integração com SGP"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Responsável</label>
            <input
              type="text"
              value={novaDiretriz.responsavel}
              onChange={(e) => setNovaDiretriz({ ...novaDiretriz, responsavel: e.target.value })}
              placeholder="Ex: Diretoria de TI"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Prazo</label>
            <input
              type="date"
              value={novaDiretriz.prazo}
              onChange={(e) => setNovaDiretriz({ ...novaDiretriz, prazo: e.target.value })}
              className="form-input"
            />
          </div>
        </div>

        <Button variant="primary" onClick={adicionarDiretriz} fullWidth>
          ➕ Adicionar Diretriz
        </Button>
      </Card>

      {/* Lista de Diretrizes */}
      {diretrizes.length > 0 && (
        <div className="workspace-hoshin-list">
          <h3>📊 Matriz de Desdobramento</h3>

          <div className="hoshin-table">
            <div className="hoshin-table-header">
              <div className="hoshin-col-diretriz">Diretriz Estratégica</div>
              <div className="hoshin-col-meta">Meta Desdobrada</div>
              <div className="hoshin-col-indicador">Indicador</div>
              <div className="hoshin-col-acao">Ação de Apoio</div>
              <div className="hoshin-col-responsavel">Responsável</div>
              <div className="hoshin-col-prazo">Prazo</div>
              <div className="hoshin-col-status">Status</div>
              <div className="hoshin-col-actions">Ações</div>
            </div>

            {diretrizes.map((diretriz) => (
              <Card key={diretriz.id} variant="glass" className="hoshin-table-row">
                <div className="hoshin-col-diretriz">
                  <strong>{diretriz.diretriz}</strong>
                </div>
                <div className="hoshin-col-meta">{diretriz.meta}</div>
                <div className="hoshin-col-indicador">{diretriz.indicador || '-'}</div>
                <div className="hoshin-col-acao">{diretriz.acao || '-'}</div>
                <div className="hoshin-col-responsavel">{diretriz.responsavel || '-'}</div>
                <div className="hoshin-col-prazo">
                  {diretriz.prazo ? new Date(diretriz.prazo).toLocaleDateString('pt-BR') : '-'}
                </div>
                <div className="hoshin-col-status">
                  <select
                    value={diretriz.status}
                    onChange={(e) => atualizarStatus(diretriz.id, e.target.value as DiretrizHoshin['status'])}
                    className="status-select"
                    style={{ backgroundColor: getStatusColor(diretriz.status) }}
                  >
                    <option value="planejado">Planejado</option>
                    <option value="em_andamento">Em Andamento</option>
                    <option value="concluido">Concluído</option>
                    <option value="atrasado">Atrasado</option>
                  </select>
                </div>
                <div className="hoshin-col-actions">
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => removerDiretriz(diretriz.id)}
                  >
                    🗑️
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Mensagem se vazio */}
      {diretrizes.length === 0 && (
        <Card variant="glass" className="workspace-hoshin-empty">
          <span className="empty-icon">🧭</span>
          <h3>Nenhuma diretriz cadastrada</h3>
          <p>Comece adicionando sua primeira diretriz estratégica no formulário acima.</p>
        </Card>
      )}
    </div>
  );
};

export default WorkspaceHoshin;
