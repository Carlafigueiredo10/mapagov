import React, { useState } from 'react';
import { Lock, Edit2, CheckCircle, FileText, Download } from 'lucide-react';

interface InterfaceRevisaoFinalProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceRevisaoFinal: React.FC<InterfaceRevisaoFinalProps> = ({ dados, onConfirm }) => {
  const bloqueados = (dados?.campos_bloqueados as Record<string, string>) || {};
  const editaveisInline = (dados?.campos_editaveis_inline as Record<string, string>) || {};
  const editaveisSecao = (dados?.campos_editaveis_secao as Record<string, unknown>) || {};
  const totalEtapas = (dados?.total_etapas as number) || 0;

  const [editando, setEditando] = useState<string | null>(null);
  const [valorTemp, setValorTemp] = useState('');

  const iniciarEdicao = (campo: string, valorAtual: string) => {
    setEditando(campo);
    setValorTemp(valorAtual || '');
  };

  const salvarInline = (campo: string) => {
    onConfirm(JSON.stringify({ acao: 'editar_inline', campo, valor: valorTemp }));
    setEditando(null);
    setValorTemp('');
  };

  const cancelarEdicao = () => {
    setEditando(null);
    setValorTemp('');
  };

  const editarSecao = (secao: string) => {
    onConfirm(JSON.stringify({ acao: 'editar_secao', secao }));
  };

  const handleFinalizar = () => {
    onConfirm(JSON.stringify({ acao: 'finalizar' }));
  };

  const handleVoltarEtapas = () => {
    onConfirm(JSON.stringify({ acao: 'voltar_etapas' }));
  };

  const labelsInline: Record<string, { label: string; icone: string; tipo: 'input' | 'textarea' }> = {
    nome_processo: { label: 'Atividade', icone: '📝', tipo: 'input' },
    entrega_esperada: { label: 'Entrega Esperada', icone: '🎯', tipo: 'textarea' },
    dispositivos_normativos: { label: 'Dispositivos Normativos', icone: '📜', tipo: 'textarea' },
    pontos_atencao: { label: 'Pontos de Atenção', icone: '⚠️', tipo: 'textarea' },
  };

  const labelsSecao: Record<string, { label: string; icone: string }> = {
    sistemas: { label: 'Sistemas Utilizados', icone: '💻' },
    operadores: { label: 'Operadores', icone: '👥' },
    fluxos_entrada: { label: 'Fluxos de Entrada', icone: '📥' },
    fluxos_saida: { label: 'Fluxos de Saída', icone: '📤' },
    etapas: { label: `Etapas do Processo (${totalEtapas})`, icone: '🔄' },
  };

  const renderValorSecao = (secao: string, valor: unknown): string => {
    if (secao === 'etapas' && Array.isArray(valor)) {
      return valor.map((e: any) => `${e.numero}. ${e.acao_principal || e.descricao || ''}`).join('\n');
    }
    if (Array.isArray(valor)) {
      if (valor.length === 0) return '(Nenhum)';
      return valor.map((v: any) => typeof v === 'string' ? v : JSON.stringify(v)).join(', ');
    }
    return String(valor || '(Nenhum)');
  };

  return (
    <div className="interface-revisao-final fade-in">
      <div className="rf-header">
        <div className="rf-title">
          <CheckCircle size={24} className="rf-icon-success" />
          <h2>Revisão Final do POP</h2>
        </div>
        <p className="rf-subtitle">
          Revise e edite os dados antes de gerar o documento final
        </p>
      </div>

      {/* Campos bloqueados */}
      <div className="rf-secao">
        <div className="rf-secao-titulo">
          <Lock size={18} />
          <h3>Identificação do Processo</h3>
          <span className="rf-badge-bloqueado">Bloqueado</span>
        </div>
        <div className="rf-campos-bloqueados">
          {bloqueados.codigo_processo && (
            <div className="rf-campo-bloqueado">
              <span className="rf-campo-label">Código CAP:</span>
              <span className="rf-campo-valor-bloqueado">{bloqueados.codigo_processo}</span>
            </div>
          )}
          {bloqueados.area && (
            <div className="rf-campo-bloqueado">
              <span className="rf-campo-label">Área:</span>
              <span className="rf-campo-valor-bloqueado">{bloqueados.area}</span>
            </div>
          )}
          {bloqueados.macroprocesso && (
            <div className="rf-campo-bloqueado">
              <span className="rf-campo-label">Macroprocesso:</span>
              <span className="rf-campo-valor-bloqueado">{bloqueados.macroprocesso}</span>
            </div>
          )}
          {bloqueados.processo_especifico && (
            <div className="rf-campo-bloqueado">
              <span className="rf-campo-label">Processo:</span>
              <span className="rf-campo-valor-bloqueado">{bloqueados.processo_especifico}</span>
            </div>
          )}
          {bloqueados.subprocesso && (
            <div className="rf-campo-bloqueado">
              <span className="rf-campo-label">Subprocesso:</span>
              <span className="rf-campo-valor-bloqueado">{bloqueados.subprocesso}</span>
            </div>
          )}
          {bloqueados.atividade && (
            <div className="rf-campo-bloqueado">
              <span className="rf-campo-label">Atividade:</span>
              <span className="rf-campo-valor-bloqueado">{bloqueados.atividade}</span>
            </div>
          )}
        </div>
      </div>

      {/* Campos editáveis inline */}
      <div className="rf-secao">
        <div className="rf-secao-titulo">
          <Edit2 size={18} />
          <h3>Dados Editáveis</h3>
        </div>

        {Object.entries(labelsInline).map(([campo, meta]) => {
          const valor = editaveisInline[campo] || '';
          const estaEditando = editando === campo;

          return (
            <div key={campo} className="rf-campo-editavel">
              <div className="rf-campo-header">
                <span className="rf-campo-icone">{meta.icone}</span>
                <span className="rf-campo-label">{meta.label}</span>
                {!estaEditando && (
                  <button
                    className="rf-btn-editar-inline"
                    onClick={() => iniciarEdicao(campo, valor)}
                  >
                    <Edit2 size={14} /> Editar
                  </button>
                )}
              </div>

              {estaEditando ? (
                <div className="rf-campo-edicao">
                  {meta.tipo === 'textarea' ? (
                    <textarea
                      value={valorTemp}
                      onChange={(e) => setValorTemp(e.target.value)}
                      className="rf-textarea"
                      rows={3}
                      autoFocus
                    />
                  ) : (
                    <input
                      type="text"
                      value={valorTemp}
                      onChange={(e) => setValorTemp(e.target.value)}
                      className="rf-input"
                      autoFocus
                    />
                  )}
                  <div className="rf-edicao-acoes">
                    <button className="rf-btn-salvar" onClick={() => salvarInline(campo)}>
                      Salvar
                    </button>
                    <button className="rf-btn-cancelar" onClick={cancelarEdicao}>
                      Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <div className={`rf-campo-valor ${!valor ? 'rf-vazio' : ''}`}>
                  {valor || '(Não informado)'}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Campos editáveis por seção */}
      <div className="rf-secao">
        <div className="rf-secao-titulo">
          <FileText size={18} />
          <h3>Seções do Processo</h3>
        </div>

        {Object.entries(labelsSecao).map(([secao, meta]) => {
          const valor = editaveisSecao[secao];
          const preview = renderValorSecao(secao, valor);

          return (
            <div key={secao} className="rf-secao-card">
              <div className="rf-secao-card-header">
                <div className="rf-secao-card-info">
                  <span className="rf-campo-icone">{meta.icone}</span>
                  <span className="rf-secao-card-label">{meta.label}</span>
                </div>
                <button className="rf-btn-editar-secao" onClick={() => editarSecao(secao)}>
                  <Edit2 size={14} /> Editar
                </button>
              </div>
              <div className="rf-secao-card-preview">
                {preview.split('\n').map((linha, i) => (
                  <div key={i}>{linha}</div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Rodapé */}
      <div className="rf-footer">
        <button className="rf-btn rf-btn-voltar" onClick={handleVoltarEtapas}>
          Voltar para Etapas
        </button>
        <button className="rf-btn rf-btn-finalizar" onClick={handleFinalizar}>
          <Download size={18} />
          Finalizar e Gerar PDF
        </button>
      </div>

      <style>{`
        .interface-revisao-final { background: white; border-radius: 12px; padding: 1.5rem; max-height: 75vh; overflow-y: auto; }
        .rf-header { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e9ecef; text-align: center; }
        .rf-title { display: flex; align-items: center; justify-content: center; gap: 0.75rem; margin-bottom: 0.5rem; }
        .rf-title h2 { margin: 0; font-size: 1.4rem; color: #1B4F72; }
        .rf-icon-success { color: #28a745; }
        .rf-subtitle { margin: 0; color: #6c757d; font-size: 0.9rem; }
        .rf-secao { margin-bottom: 1.5rem; background: #f8f9fa; border-radius: 8px; padding: 1rem; border: 1px solid #dee2e6; }
        .rf-secao-titulo { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #dee2e6; color: #1351B4; }
        .rf-secao-titulo h3 { margin: 0; font-size: 1rem; flex: 1; }
        .rf-badge-bloqueado { font-size: 0.7rem; background: #e9ecef; color: #6c757d; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; }
        .rf-campos-bloqueados { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.5rem; }
        .rf-campo-bloqueado { display: flex; flex-direction: column; gap: 0.15rem; padding: 0.5rem; background: #e9ecef; border-radius: 6px; }
        .rf-campo-label { font-size: 0.75rem; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.3px; }
        .rf-campo-valor-bloqueado { font-size: 0.85rem; color: #495057; }
        .rf-campo-editavel { padding: 0.75rem; margin-bottom: 0.5rem; background: white; border-radius: 6px; border: 1px solid #dee2e6; }
        .rf-campo-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }
        .rf-campo-icone { font-size: 1rem; }
        .rf-btn-editar-inline { margin-left: auto; display: flex; align-items: center; gap: 0.3rem; padding: 0.25rem 0.5rem; background: transparent; border: 1px solid #1351B4; color: #1351B4; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; }
        .rf-btn-editar-inline:hover { background: #1351B4; color: white; }
        .rf-campo-valor { font-size: 0.9rem; color: #212529; white-space: pre-wrap; line-height: 1.5; }
        .rf-vazio { color: #adb5bd; font-style: italic; }
        .rf-campo-edicao { display: flex; flex-direction: column; gap: 0.5rem; }
        .rf-textarea, .rf-input { width: 100%; padding: 0.5rem; border: 2px solid #1351B4; border-radius: 6px; font-size: 0.9rem; font-family: inherit; resize: vertical; box-sizing: border-box; }
        .rf-textarea:focus, .rf-input:focus { outline: none; box-shadow: 0 0 0 3px rgba(19, 81, 180, 0.15); }
        .rf-edicao-acoes { display: flex; gap: 0.5rem; justify-content: flex-end; }
        .rf-btn-salvar { padding: 0.4rem 1rem; background: #28a745; color: white; border: none; border-radius: 4px; font-weight: 600; font-size: 0.8rem; cursor: pointer; }
        .rf-btn-salvar:hover { background: #218838; }
        .rf-btn-cancelar { padding: 0.4rem 1rem; background: #6c757d; color: white; border: none; border-radius: 4px; font-weight: 600; font-size: 0.8rem; cursor: pointer; }
        .rf-btn-cancelar:hover { background: #5a6268; }
        .rf-secao-card { margin-bottom: 0.5rem; background: white; border-radius: 6px; border: 1px solid #dee2e6; overflow: hidden; }
        .rf-secao-card-header { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }
        .rf-secao-card-info { display: flex; align-items: center; gap: 0.5rem; }
        .rf-secao-card-label { font-weight: 600; font-size: 0.9rem; color: #212529; }
        .rf-btn-editar-secao { display: flex; align-items: center; gap: 0.3rem; padding: 0.35rem 0.75rem; background: #1351B4; color: white; border: none; border-radius: 4px; font-size: 0.8rem; font-weight: 500; cursor: pointer; transition: all 0.2s; }
        .rf-btn-editar-secao:hover { background: #0c3d8a; transform: translateY(-1px); }
        .rf-secao-card-preview { padding: 0.75rem; font-size: 0.85rem; color: #495057; max-height: 100px; overflow-y: auto; line-height: 1.5; }
        .rf-footer { margin-top: 1.5rem; padding-top: 1rem; border-top: 2px solid #e9ecef; display: flex; gap: 1rem; justify-content: flex-end; }
        .rf-btn { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.2s; font-size: 0.95rem; }
        .rf-btn-voltar { background: #6c757d; color: white; }
        .rf-btn-voltar:hover { background: #5a6268; transform: translateY(-1px); }
        .rf-btn-finalizar { background: #28a745; color: white; }
        .rf-btn-finalizar:hover { background: #218838; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3); }
        .interface-revisao-final::-webkit-scrollbar { width: 8px; }
        .interface-revisao-final::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
        .interface-revisao-final::-webkit-scrollbar-thumb { background: #888; border-radius: 4px; }
        @media (max-width: 768px) {
          .rf-campos-bloqueados { grid-template-columns: 1fr; }
          .rf-footer { flex-direction: column; }
          .rf-btn { width: 100%; justify-content: center; }
        }
      `}</style>
    </div>
  );
};

export default InterfaceRevisaoFinal;
