/**
 * DashboardAreas - Dashboard Operacional das Áreas
 * Helena PE - Gestão de Projetos Estratégicos
 *
 * Interface para coordenações gerenciarem seus projetos
 */

import React, { useState } from 'react';
import { ProjetoEstrategico, AREAS_DISPONIVEIS, FASES_PROJETO } from '../../types/dashboard';
import './DashboardAreas.css';

export interface DashboardAreasProps {
  projetos: ProjetoEstrategico[];
  onAdicionarProjeto: (projeto: ProjetoEstrategico) => void;
  onAtualizarProjeto: (id: string, projeto: Partial<ProjetoEstrategico>) => void;
  onFechar: () => void;
}

export const DashboardAreas: React.FC<DashboardAreasProps> = ({
  projetos,
  onAdicionarProjeto,
  onAtualizarProjeto,
  onFechar
}) => {
  const [areaFiltro, setAreaFiltro] = useState<string>('Todas');
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [projetoSelecionado, setProjetoSelecionado] = useState<ProjetoEstrategico | null>(null);

  // Filtra projetos por área
  const projetosFiltrados = areaFiltro === 'Todas'
    ? projetos
    : projetos.filter(p => p.area === areaFiltro);

  // Abre formulário de edição
  const handleEditarProjeto = (projeto: ProjetoEstrategico) => {
    setProjetoSelecionado(projeto);
    setMostrarFormulario(true);
  };

  // Cria novo projeto
  const handleNovoProjeto = () => {
    setProjetoSelecionado(null);
    setMostrarFormulario(true);
  };

  return (
    <div className="dashboard-areas-overlay">
      <div className="dashboard-areas-container">
        {/* Header */}
        <header className="dashboard-header">
          <div className="header-content">
            <h2>🏢 Dashboard das Áreas</h2>
            <p>Gestão de Projetos Estratégicos</p>
          </div>
          <button className="btn-fechar" onClick={onFechar} aria-label="Fechar dashboard">
            ✕
          </button>
        </header>

        {/* Filtros e Ações */}
        <div className="dashboard-toolbar">
          <div className="toolbar-filters">
            <label htmlFor="area-filter">Filtrar por área:</label>
            <select
              id="area-filter"
              value={areaFiltro}
              onChange={(e) => setAreaFiltro(e.target.value)}
              className="filter-select"
            >
              <option value="Todas">Todas as Áreas</option>
              {AREAS_DISPONIVEIS.map(area => (
                <option key={area} value={area}>{area}</option>
              ))}
            </select>
          </div>

          <button className="btn-primary" onClick={handleNovoProjeto}>
            ➕ Novo Projeto
          </button>
        </div>

        {/* Lista de Projetos */}
        <div className="projetos-grid">
          {projetosFiltrados.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">📂</span>
              <h3>Nenhum projeto encontrado</h3>
              <p>Adicione um novo projeto para começar</p>
            </div>
          ) : (
            projetosFiltrados.map(projeto => (
              <ProjetoCard
                key={projeto.id_projeto}
                projeto={projeto}
                onEditar={() => handleEditarProjeto(projeto)}
              />
            ))
          )}
        </div>

        {/* Formulário Modal */}
        {mostrarFormulario && (
          <FormularioProjeto
            projeto={projetoSelecionado}
            onSalvar={(projeto) => {
              if (projetoSelecionado) {
                onAtualizarProjeto(projetoSelecionado.id_projeto, projeto);
              } else {
                onAdicionarProjeto(projeto as ProjetoEstrategico);
              }
              setMostrarFormulario(false);
              setProjetoSelecionado(null);
            }}
            onCancelar={() => {
              setMostrarFormulario(false);
              setProjetoSelecionado(null);
            }}
          />
        )}
      </div>
    </div>
  );
};

// ============================================================================
// COMPONENTE: Card do Projeto
// ============================================================================

interface ProjetoCardProps {
  projeto: ProjetoEstrategico;
  onEditar: () => void;
}

const ProjetoCard: React.FC<ProjetoCardProps> = ({ projeto, onEditar }) => {
  return (
    <div className="projeto-card">
      <div className="projeto-card-header">
        <span className="projeto-area">{projeto.area}</span>
        <span className="projeto-fase">{projeto.fase_atual}</span>
      </div>

      <h3 className="projeto-titulo">{projeto.nome_projeto}</h3>
      <p className="projeto-resultado">{projeto.resultado_esperado}</p>

      <div className="projeto-andamento">
        <div className="andamento-label">
          <span>Andamento</span>
          <span className="andamento-percentual">{projeto.andamento}%</span>
        </div>
        <div className="andamento-barra">
          <div
            className="andamento-preenchimento"
            style={{ width: `${projeto.andamento}%` }}
          />
        </div>
      </div>

      {projeto.pedido_diretor.existe && (
        <div className="projeto-pedido-alerta">
          <span className="alerta-icon">📋</span>
          <span className="alerta-texto">Pedido do Diretor</span>
        </div>
      )}

      <div className="projeto-footer">
        <span className="projeto-responsavel">
          👤 {projeto.ultima_atualizacao.responsavel}
        </span>
        <button className="btn-editar" onClick={onEditar}>
          Editar
        </button>
      </div>
    </div>
  );
};

// ============================================================================
// COMPONENTE: Formulário de Projeto
// ============================================================================

interface FormularioProjetoProps {
  projeto: ProjetoEstrategico | null;
  onSalvar: (projeto: Partial<ProjetoEstrategico>) => void;
  onCancelar: () => void;
}

const FormularioProjeto: React.FC<FormularioProjetoProps> = ({
  projeto,
  onSalvar,
  onCancelar
}) => {
  const [formData, setFormData] = useState({
    id_projeto: projeto?.id_projeto || `proj_${Date.now()}`,
    area: projeto?.area || AREAS_DISPONIVEIS[0],
    nome_projeto: projeto?.nome_projeto || '',
    resultado_esperado: projeto?.resultado_esperado || '',
    fases_detalhadas: projeto?.fases_detalhadas || [],
    fase_atual: projeto?.fase_atual || FASES_PROJETO[0],
    proximos_encaminhamentos: projeto?.proximos_encaminhamentos || '',
    andamento: projeto?.andamento || 0,
    dependencia: projeto?.dependencia || '',
    pedido_diretor: projeto?.pedido_diretor || {
      existe: false
    },
    ultima_atualizacao: {
      data: new Date().toISOString().split('T')[0],
      responsavel: ''
    },
    historico_atualizacoes: projeto?.historico_atualizacoes || []
  });

  const [detalharFases, setDetalharFases] = useState(
    projeto?.fases_detalhadas && projeto.fases_detalhadas.length > 0
  );

  const [fasesConfirmadas, setFasesConfirmadas] = useState<Set<number>>(new Set());

  // Funções de manipulação de fases
  const adicionarFase = () => {
    const novaFase = {
      numero: (formData.fases_detalhadas?.length || 0) + 1,
      descricao: '',
      resultados: ''
    };
    setFormData({
      ...formData,
      fases_detalhadas: [...(formData.fases_detalhadas || []), novaFase]
    });
  };

  const removerFase = (index: number) => {
    const novasFases = formData.fases_detalhadas?.filter((_, i) => i !== index) || [];
    // Renumerar fases
    const fasesRenumeradas = novasFases.map((fase, i) => ({
      ...fase,
      numero: i + 1
    }));
    setFormData({
      ...formData,
      fases_detalhadas: fasesRenumeradas
    });
  };

  const atualizarFase = (index: number, campo: 'descricao' | 'resultados', valor: string) => {
    const novasFases = [...(formData.fases_detalhadas || [])];
    novasFases[index] = { ...novasFases[index], [campo]: valor };
    setFormData({
      ...formData,
      fases_detalhadas: novasFases
    });
    // Remove confirmação quando o usuário edita
    setFasesConfirmadas(prev => {
      const newSet = new Set(prev);
      newSet.delete(index);
      return newSet;
    });
  };

  const toggleConfirmacaoFase = (index: number) => {
    setFasesConfirmadas(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSalvar(formData);
  };

  return (
    <div className="formulario-overlay" onClick={onCancelar}>
      <div className="formulario-container" onClick={(e) => e.stopPropagation()}>
        <div className="formulario-header">
          <h3>{projeto ? 'Editar Projeto' : 'Novo Projeto'}</h3>
          <button className="btn-fechar" onClick={onCancelar}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="formulario-body">
          <div className="form-group">
            <label htmlFor="area">Área Responsável *</label>
            <select
              id="area"
              value={formData.area}
              onChange={(e) => setFormData({ ...formData, area: e.target.value })}
              required
            >
              {AREAS_DISPONIVEIS.map(area => (
                <option key={area} value={area}>{area}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="nome">Nome do Projeto *</label>
            <input
              id="nome"
              type="text"
              value={formData.nome_projeto}
              onChange={(e) => setFormData({ ...formData, nome_projeto: e.target.value })}
              required
              placeholder="Ex: Gestão de Indícios Baseada em Dados"
            />
          </div>

          <div className="form-group">
            <label htmlFor="resultado">Resultado Esperado *</label>
            <textarea
              id="resultado"
              value={formData.resultado_esperado}
              onChange={(e) => setFormData({ ...formData, resultado_esperado: e.target.value })}
              required
              rows={3}
              placeholder="Descreva o impacto esperado do projeto"
            />
          </div>

          {/* Detalhamento de Fases */}
          <div className="form-group" style={{ marginTop: '24px', paddingTop: '24px', borderTop: '2px solid #e5e7eb' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <input
                type="checkbox"
                checked={detalharFases}
                onChange={(e) => {
                  setDetalharFases(e.target.checked);
                  if (!e.target.checked) {
                    setFormData({ ...formData, fases_detalhadas: [] });
                  }
                }}
              />
              <span style={{ fontWeight: 600 }}>Você quer detalhar as fases do seu projeto?</span>
            </label>

            {detalharFases && (
              <div style={{ marginTop: '16px' }}>
                {formData.fases_detalhadas && formData.fases_detalhadas.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {formData.fases_detalhadas.map((fase, index) => {
                      const fasePreenchida = fase.descricao.trim() !== '' && fase.resultados.trim() !== '';
                      const faseConfirmada = fasesConfirmadas.has(index);

                      return (
                        <div key={index} style={{
                          display: 'grid',
                          gridTemplateColumns: '40px 1fr 1fr 88px',
                          gap: '8px',
                          alignItems: 'start',
                          padding: '12px',
                          backgroundColor: '#f9fafb',
                          borderRadius: '6px',
                          border: faseConfirmada ? '2px solid #10b981' : '2px solid transparent'
                        }}>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '40px',
                            fontWeight: 600,
                            color: '#6366f1'
                          }}>
                            {fase.numero}
                          </div>

                          <div>
                            <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>
                              Descrição da Fase *
                            </label>
                            <input
                              type="text"
                              value={fase.descricao}
                              onChange={(e) => atualizarFase(index, 'descricao', e.target.value)}
                              required={detalharFases}
                              placeholder="Ex: Planejamento inicial"
                              style={{ width: '100%' }}
                            />
                          </div>

                          <div>
                            <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>
                              Resultados Esperados *
                            </label>
                            <input
                              type="text"
                              value={fase.resultados}
                              onChange={(e) => atualizarFase(index, 'resultados', e.target.value)}
                              required={detalharFases}
                              placeholder="Ex: Cronograma aprovado"
                              style={{ width: '100%' }}
                            />
                          </div>

                          <div style={{ display: 'flex', gap: '4px' }}>
                            <button
                              type="button"
                              onClick={() => toggleConfirmacaoFase(index)}
                              disabled={!fasePreenchida}
                              style={{
                                height: '40px',
                                width: '40px',
                                backgroundColor: faseConfirmada ? '#d1fae5' : (fasePreenchida ? '#fee2e2' : '#f3f4f6'),
                                color: faseConfirmada ? '#059669' : (fasePreenchida ? '#dc2626' : '#9ca3af'),
                                border: 'none',
                                borderRadius: '4px',
                                fontSize: '18px',
                                fontWeight: 'bold',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'all 0.2s',
                                cursor: fasePreenchida ? 'pointer' : 'not-allowed',
                                opacity: fasePreenchida ? 1 : 0.5
                              }}
                              title={
                                faseConfirmada
                                  ? 'Fase confirmada - clique para desconfirmar'
                                  : fasePreenchida
                                    ? 'Clique para confirmar a fase'
                                    : 'Preencha todos os campos primeiro'
                              }
                            >
                              ✓
                            </button>

                            <button
                              type="button"
                              onClick={() => removerFase(index)}
                              style={{
                                height: '40px',
                                width: '40px',
                                backgroundColor: '#fee2e2',
                                color: '#dc2626',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '18px',
                                fontWeight: 'bold'
                              }}
                              title="Remover fase"
                            >
                              ✕
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p style={{ color: '#6b7280', fontSize: '14px', fontStyle: 'italic' }}>
                    Nenhuma fase adicionada ainda. Clique no botão abaixo para adicionar.
                  </p>
                )}

                <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                  <button
                    type="button"
                    onClick={adicionarFase}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#6366f1',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: 500,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    ➕ Adicionar Fase
                  </button>

                  {formData.fases_detalhadas && formData.fases_detalhadas.length > 0 && (
                    <button
                      type="button"
                      onClick={() => {
                        // Verifica se todas as fases estão preenchidas
                        const todasPreenchidas = formData.fases_detalhadas?.every(
                          fase => fase.descricao.trim() !== '' && fase.resultados.trim() !== ''
                        );

                        if (!todasPreenchidas) {
                          alert('Preencha todas as fases antes de concluir!');
                          return;
                        }

                        // Verifica se todas estão confirmadas
                        const todasConfirmadas = formData.fases_detalhadas?.every(
                          (_, index) => fasesConfirmadas.has(index)
                        );

                        if (!todasConfirmadas) {
                          alert('Confirme todas as fases (clique no ✓ verde) antes de concluir!');
                          return;
                        }

                        // Desativa o modo de detalhamento
                        setDetalharFases(false);
                      }}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 500,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}
                    >
                      ✓ Concluir
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="fase">Fase Atual *</label>
              <select
                id="fase"
                value={formData.fase_atual}
                onChange={(e) => {
                  const novaFase = e.target.value;
                  setFormData({ ...formData, fase_atual: novaFase });

                  // Calcular percentual automaticamente se fases detalhadas
                  if (detalharFases && formData.fases_detalhadas && formData.fases_detalhadas.length > 0) {
                    const faseAtualObj = formData.fases_detalhadas.find(f => f.descricao === novaFase);
                    if (faseAtualObj) {
                      const percentualCalculado = Math.round((faseAtualObj.numero / formData.fases_detalhadas.length) * 100);
                      setFormData(prev => ({ ...prev, fase_atual: novaFase, andamento: percentualCalculado }));
                    }
                  }
                }}
                required
              >
                {detalharFases && formData.fases_detalhadas && formData.fases_detalhadas.length > 0 ? (
                  formData.fases_detalhadas.map(fase => (
                    <option key={fase.numero} value={fase.descricao}>
                      Fase {fase.numero}: {fase.descricao}
                    </option>
                  ))
                ) : (
                  FASES_PROJETO.map(fase => (
                    <option key={fase} value={fase}>{fase}</option>
                  ))
                )}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="andamento">
                Andamento (%) *
                {detalharFases && formData.fases_detalhadas && formData.fases_detalhadas.length > 0 && (
                  <span style={{ fontSize: '12px', color: '#6b7280', fontWeight: 'normal', marginLeft: '8px' }}>
                    (calculado automaticamente)
                  </span>
                )}
              </label>
              <input
                id="andamento"
                type="number"
                min="0"
                max="100"
                value={formData.andamento}
                onChange={(e) => setFormData({ ...formData, andamento: parseInt(e.target.value) })}
                required
                disabled={detalharFases && formData.fases_detalhadas && formData.fases_detalhadas.length > 0}
                style={{
                  backgroundColor: detalharFases && formData.fases_detalhadas && formData.fases_detalhadas.length > 0 ? '#f3f4f6' : 'white',
                  cursor: detalharFases && formData.fases_detalhadas && formData.fases_detalhadas.length > 0 ? 'not-allowed' : 'text'
                }}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="encaminhamentos">Próximos Encaminhamentos *</label>
            <textarea
              id="encaminhamentos"
              value={formData.proximos_encaminhamentos}
              onChange={(e) => setFormData({ ...formData, proximos_encaminhamentos: e.target.value })}
              required
              rows={2}
              placeholder="Descreva as próximas ações previstas"
            />
          </div>

          <div className="form-group">
            <label htmlFor="dependencia">Dependências</label>
            <input
              id="dependencia"
              type="text"
              value={formData.dependencia}
              onChange={(e) => setFormData({ ...formData, dependencia: e.target.value })}
              placeholder="Ex: CGTEC (integração SIGA), Dataprev"
            />
          </div>

          {/* Pedido do Diretor */}
          <div className="form-group" style={{ marginTop: '24px', paddingTop: '24px', borderTop: '2px solid #e5e7eb' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <input
                type="checkbox"
                checked={formData.pedido_diretor.existe}
                onChange={(e) => setFormData({
                  ...formData,
                  pedido_diretor: {
                    ...formData.pedido_diretor,
                    existe: e.target.checked
                  }
                })}
              />
              <span style={{ fontWeight: 600 }}>Existe Pedido do Diretor?</span>
            </label>

            {formData.pedido_diretor.existe && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="data_pedido">Data do Pedido *</label>
                    <input
                      id="data_pedido"
                      type="date"
                      value={formData.pedido_diretor.data_pedido || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        pedido_diretor: { ...formData.pedido_diretor, data_pedido: e.target.value }
                      })}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="prazo_retorno">Prazo de Retorno *</label>
                    <input
                      id="prazo_retorno"
                      type="date"
                      value={formData.pedido_diretor.prazo_retorno || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        pedido_diretor: { ...formData.pedido_diretor, prazo_retorno: e.target.value }
                      })}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="canal">Canal *</label>
                  <select
                    id="canal"
                    value={formData.pedido_diretor.canal || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      pedido_diretor: { ...formData.pedido_diretor, canal: e.target.value }
                    })}
                    required
                  >
                    <option value="">Selecione o canal</option>
                    <option value="SEI">SEI (Despacho/Processo)</option>
                    <option value="E-mail">E-mail</option>
                    <option value="WhatsApp">WhatsApp</option>
                    <option value="Telefone">Telefone</option>
                    <option value="Reunião presencial">Reunião presencial</option>
                    <option value="Reunião virtual">Reunião virtual (Teams/Meet)</option>
                    <option value="Ofício">Ofício</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="descricao_pedido">Descrição do Pedido *</label>
                  <textarea
                    id="descricao_pedido"
                    value={formData.pedido_diretor.descricao_pedido || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      pedido_diretor: { ...formData.pedido_diretor, descricao_pedido: e.target.value }
                    })}
                    required
                    rows={2}
                    placeholder="O que foi solicitado pelo diretor"
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="retorno_esperado">Retorno Esperado *</label>
                    <input
                      id="retorno_esperado"
                      type="text"
                      value={formData.pedido_diretor.retorno_esperado || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        pedido_diretor: { ...formData.pedido_diretor, retorno_esperado: e.target.value }
                      })}
                      required
                      placeholder="Ex: Relatório validado até 05/11/2025"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="status_pedido">Status do Pedido *</label>
                    <select
                      id="status_pedido"
                      value={formData.pedido_diretor.status_pedido || 'Pendente'}
                      onChange={(e) => setFormData({
                        ...formData,
                        pedido_diretor: { ...formData.pedido_diretor, status_pedido: e.target.value as any }
                      })}
                      required
                    >
                      <option value="Pendente">Pendente</option>
                      <option value="Em andamento">Em andamento</option>
                      <option value="Atendido">Atendido</option>
                      <option value="Aguardando resposta">Aguardando resposta</option>
                    </select>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="responsavel">Responsável pela Atualização *</label>
            <input
              id="responsavel"
              type="text"
              value={formData.ultima_atualizacao.responsavel}
              onChange={(e) => setFormData({
                ...formData,
                ultima_atualizacao: { ...formData.ultima_atualizacao, responsavel: e.target.value }
              })}
              required
              placeholder="Seu nome"
            />
          </div>

          <div className="formulario-actions">
            <button type="button" className="btn-secondary" onClick={onCancelar}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary">
              Salvar Projeto
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DashboardAreas;
