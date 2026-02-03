/**
 * Etapa1_Contexto - Questionario de contexto (Bloco A + B)
 */
import React, { useState, useEffect } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import { FREQUENCIAS_EXECUCAO, AREAS_DECIPEX, ContextoEstruturado } from '../../types/analiseRiscos.types';

interface Props {
  onAvancar: () => void;
  onVoltar: () => void;
  textoExtraido?: string;
}

const Etapa1Contexto: React.FC<Props> = ({ onAvancar, onVoltar, textoExtraido }) => {
  const { currentAnalise, salvarContexto, loading, error } = useAnaliseRiscosStore();

  // Bloco A - Identificacao
  const [nomeObjeto, setNomeObjeto] = useState('');
  const [objetivoFinalidade, setObjetivoFinalidade] = useState('');
  const [areaResponsavel, setAreaResponsavel] = useState('');
  const [descricaoEscopo, setDescricaoEscopo] = useState('');

  // Bloco B - Contexto Operacional
  const [recursosNecessarios, setRecursosNecessarios] = useState('');
  const [areasAtoresEnvolvidos, setAreasAtoresEnvolvidos] = useState('');
  const [frequenciaExecucao, setFrequenciaExecucao] = useState('');
  const [prazosSlas, setPrazosSlas] = useState('');
  const [dependenciasExternas, setDependenciasExternas] = useState('');
  const [historicoProblemas, setHistoricoProblemas] = useState('');
  const [impactoSeFalhar, setImpactoSeFalhar] = useState('');

  // Carregar dados existentes
  useEffect(() => {
    if (currentAnalise?.contexto_estruturado) {
      const ctx = currentAnalise.contexto_estruturado;
      if (ctx.bloco_a) {
        setNomeObjeto(ctx.bloco_a.nome_objeto || '');
        setObjetivoFinalidade(ctx.bloco_a.objetivo_finalidade || '');
        setAreaResponsavel(ctx.bloco_a.area_responsavel || '');
        setDescricaoEscopo(ctx.bloco_a.descricao_escopo || '');
      }
      if (ctx.bloco_b) {
        setRecursosNecessarios(ctx.bloco_b.recursos_necessarios || '');
        setAreasAtoresEnvolvidos(ctx.bloco_b.areas_atores_envolvidos || '');
        setFrequenciaExecucao(ctx.bloco_b.frequencia_execucao || '');
        setPrazosSlas(ctx.bloco_b.prazos_slas || '');
        setDependenciasExternas(ctx.bloco_b.dependencias_externas || '');
        setHistoricoProblemas(ctx.bloco_b.historico_problemas || '');
        setImpactoSeFalhar(ctx.bloco_b.impacto_se_falhar || '');
      }
    }
  }, [currentAnalise]);

  const handleAvancar = async () => {
    // Validar campos obrigatorios
    if (!nomeObjeto.trim() || !objetivoFinalidade.trim() || !areaResponsavel.trim()) {
      alert('Preencha os campos obrigatorios do Bloco A');
      return;
    }
    if (!recursosNecessarios.trim() || !frequenciaExecucao || !impactoSeFalhar.trim()) {
      alert('Preencha os campos obrigatorios do Bloco B');
      return;
    }

    const contexto: ContextoEstruturado = {
      bloco_a: {
        nome_objeto: nomeObjeto,
        objetivo_finalidade: objetivoFinalidade,
        area_responsavel: areaResponsavel,
        descricao_escopo: descricaoEscopo,
      },
      bloco_b: {
        recursos_necessarios: recursosNecessarios,
        areas_atores_envolvidos: areasAtoresEnvolvidos,
        frequencia_execucao: frequenciaExecucao,
        prazos_slas: prazosSlas,
        dependencias_externas: dependenciasExternas,
        historico_problemas: historicoProblemas,
        impacto_se_falhar: impactoSeFalhar,
      },
    };

    const sucesso = await salvarContexto(contexto);
    if (sucesso) {
      onAvancar();
    }
  };

  const inputStyle = { width: '100%', padding: '8px', marginBottom: '15px' };
  const labelStyle = { display: 'block', marginBottom: '5px', fontWeight: 'bold' as const };

  return (
    <div>
      <h3>Contexto do Objeto</h3>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Descreva o {currentAnalise?.tipo_origem?.toLowerCase() || 'objeto'} que sera analisado.
      </p>

      {/* Texto extraido do PDF */}
      {textoExtraido && (
        <div style={{ padding: '15px', background: '#fef3c7', borderRadius: '8px', marginBottom: '20px' }}>
          <h4 style={{ marginTop: 0, color: '#92400e' }}>Conteudo extraido do PDF</h4>
          <div style={{ maxHeight: '200px', overflow: 'auto', fontSize: '13px', whiteSpace: 'pre-wrap', background: 'white', padding: '10px', borderRadius: '4px' }}>
            {textoExtraido.slice(0, 2000)}{textoExtraido.length > 2000 ? '...' : ''}
          </div>
          <p style={{ fontSize: '12px', color: '#92400e', marginBottom: 0, marginTop: '10px' }}>
            Use o conteudo acima para preencher os campos abaixo.
          </p>
        </div>
      )}

      {/* Bloco A - Identificacao */}
      <div style={{ padding: '15px', background: '#f9fafb', borderRadius: '8px', marginBottom: '20px' }}>
        <h4 style={{ marginTop: 0, color: '#3b82f6' }}>Bloco A - Identificacao</h4>

        <label style={labelStyle}>Nome do objeto *</label>
        <input
          type="text"
          value={nomeObjeto}
          onChange={(e) => setNomeObjeto(e.target.value)}
          placeholder="Ex: Processo de contratacao de TI"
          style={inputStyle}
        />

        <label style={labelStyle}>Objetivo / Finalidade *</label>
        <textarea
          value={objetivoFinalidade}
          onChange={(e) => setObjetivoFinalidade(e.target.value)}
          placeholder="Para que serve este projeto/processo?"
          rows={3}
          style={inputStyle}
        />

        <label style={labelStyle}>Area responsavel *</label>
        <select
          value={areaResponsavel}
          onChange={(e) => setAreaResponsavel(e.target.value)}
          style={inputStyle}
        >
          <option value="">Selecione a area...</option>
          {AREAS_DECIPEX.map((area) => (
            <option key={area.codigo} value={area.codigo}>
              {area.prefixo} - {area.nome} - {area.codigo}
            </option>
          ))}
        </select>

        <label style={labelStyle}>Descricao do escopo</label>
        <textarea
          value={descricaoEscopo}
          onChange={(e) => setDescricaoEscopo(e.target.value)}
          placeholder="Descreva brevemente o que faz este processo/projeto"
          rows={3}
          style={inputStyle}
        />
      </div>

      {/* Bloco B - Contexto Operacional */}
      <div style={{ padding: '15px', background: '#f9fafb', borderRadius: '8px', marginBottom: '20px' }}>
        <h4 style={{ marginTop: 0, color: '#3b82f6' }}>Bloco B - Contexto Operacional</h4>

        <label style={labelStyle}>Quais recursos sao necessarios? *</label>
        <textarea
          value={recursosNecessarios}
          onChange={(e) => setRecursosNecessarios(e.target.value)}
          placeholder="Pessoas, sistemas, orcamento, equipamentos..."
          rows={2}
          style={inputStyle}
        />

        <label style={labelStyle}>Quais areas/atores estao envolvidos?</label>
        <input
          type="text"
          value={areasAtoresEnvolvidos}
          onChange={(e) => setAreasAtoresEnvolvidos(e.target.value)}
          placeholder="Liste as areas e papeis envolvidos"
          style={inputStyle}
        />

        <label style={labelStyle}>Com que frequencia ocorre? *</label>
        <select
          value={frequenciaExecucao}
          onChange={(e) => setFrequenciaExecucao(e.target.value)}
          style={inputStyle}
        >
          <option value="">Selecione...</option>
          {FREQUENCIAS_EXECUCAO.map((f) => (
            <option key={f.valor} value={f.valor}>{f.label}</option>
          ))}
        </select>

        <label style={labelStyle}>Existem prazos legais ou SLAs?</label>
        <input
          type="text"
          value={prazosSlas}
          onChange={(e) => setPrazosSlas(e.target.value)}
          placeholder="Descreva prazos e obrigacoes, ou 'Nao ha'"
          style={inputStyle}
        />

        <label style={labelStyle}>Ha dependencia de sistemas externos ou terceiros?</label>
        <input
          type="text"
          value={dependenciasExternas}
          onChange={(e) => setDependenciasExternas(e.target.value)}
          placeholder="Liste dependencias ou 'Nao ha'"
          style={inputStyle}
        />

        <label style={labelStyle}>Ja houve problemas ou incidentes anteriores?</label>
        <textarea
          value={historicoProblemas}
          onChange={(e) => setHistoricoProblemas(e.target.value)}
          placeholder="Descreva historico ou 'Nao ha registro'"
          rows={2}
          style={inputStyle}
        />

        <label style={labelStyle}>O que acontece se isso nao funcionar? *</label>
        <textarea
          value={impactoSeFalhar}
          onChange={(e) => setImpactoSeFalhar(e.target.value)}
          placeholder="Descreva as consequencias de falha"
          rows={2}
          style={inputStyle}
        />
      </div>

      {error && (
        <div style={{ padding: '10px', background: '#fee2e2', color: '#dc2626', borderRadius: '4px', marginBottom: '15px' }}>
          {error.erro}
        </div>
      )}

      {/* Navegacao */}
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <button
          onClick={onVoltar}
          style={{
            padding: '10px 20px',
            background: '#e5e7eb',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          ← Voltar
        </button>
        <button
          onClick={handleAvancar}
          disabled={loading}
          style={{
            padding: '12px 30px',
            background: loading ? '#9ca3af' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Salvando...' : 'Avancar →'}
        </button>
      </div>
    </div>
  );
};

export default Etapa1Contexto;
