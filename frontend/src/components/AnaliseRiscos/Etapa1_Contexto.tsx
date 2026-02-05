/**
 * Etapa1_Contexto - Questionario de contexto (Bloco A + B)
 *
 * BLOCO B ESTRUTURADO (v2):
 * - Campos novos (BlocoBEstruturado) coexistem com campos de texto antigos
 * - NAO_SEI e opcao valida (nunca vira NAO)
 * - undefined = nao respondeu, [] = respondeu "nenhum"
 *
 * SEPARACAO DE RESPONSABILIDADES:
 * - blocoB: BlocoBEstruturado → somente campos estruturados NOVOS
 * - estados separados → campos de texto ANTIGOS (retrocompat)
 */
import React, { useState, useEffect } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import type { BlocoBEstruturado } from '../../types/analiseRiscos.types';
import {
  FREQUENCIAS_EXECUCAO,
  AREAS_DECIPEX,
  ContextoEstruturado,
  BlocoBRecurso,
  BlocoBFrequencia,
  BLOCO_B_RECURSOS,
  BLOCO_B_SLA,
  BLOCO_B_DEPENDENCIAS,
  BLOCO_B_INCIDENTES,
} from '../../types/analiseRiscos.types';

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

  // Bloco B - Campos de texto antigos (mantidos para retrocompat)
  const [recursosNecessarios, setRecursosNecessarios] = useState('');
  const [areasAtoresEnvolvidos, setAreasAtoresEnvolvidos] = useState('');
  const [frequenciaExecucao, setFrequenciaExecucao] = useState('');
  const [prazosSlas, setPrazosSlas] = useState('');
  const [dependenciasExternas, setDependenciasExternas] = useState('');
  const [historicoProblemas, setHistoricoProblemas] = useState('');
  const [impactoSeFalhar, setImpactoSeFalhar] = useState('');

  // Bloco B - Campos estruturados NOVOS (usa tipo oficial)
  // Todos os campos sao opcionais em BlocoBEstruturado
  // undefined = nao respondeu, [] = respondeu "nenhum"
  const [blocoB, setBlocoB] = useState<BlocoBEstruturado>({});

  // Carregar dados existentes
  useEffect(() => {
    if (currentAnalise?.contexto_estruturado) {
      const ctx = currentAnalise.contexto_estruturado;

      // Bloco A
      if (ctx.bloco_a) {
        setNomeObjeto(ctx.bloco_a.nome_objeto || '');
        setObjetivoFinalidade(ctx.bloco_a.objetivo_finalidade || '');
        setAreaResponsavel(ctx.bloco_a.area_responsavel || '');
        setDescricaoEscopo(ctx.bloco_a.descricao_escopo || '');
      }

      // Bloco B - campos antigos (texto)
      if (ctx.bloco_b) {
        setRecursosNecessarios(ctx.bloco_b.recursos_necessarios || '');
        setAreasAtoresEnvolvidos(ctx.bloco_b.areas_atores_envolvidos || '');
        setFrequenciaExecucao(ctx.bloco_b.frequencia_execucao || '');
        setPrazosSlas(ctx.bloco_b.prazos_slas || '');
        setDependenciasExternas(ctx.bloco_b.dependencias_externas || '');
        setHistoricoProblemas(ctx.bloco_b.historico_problemas || '');
        setImpactoSeFalhar(ctx.bloco_b.impacto_se_falhar || '');

        // Bloco B - campos estruturados NOVOS (se existirem)
        // Carrega apenas campos que existem no BlocoBEstruturado
        setBlocoB({
          recursos: ctx.bloco_b.recursos,
          recursos_outros: ctx.bloco_b.recursos_outros,
          atores_envolvidos_texto: ctx.bloco_b.atores_envolvidos_texto,
          frequencia: ctx.bloco_b.frequencia,
          sla: ctx.bloco_b.sla,
          sla_detalhe: ctx.bloco_b.sla_detalhe,
          dependencia: ctx.bloco_b.dependencia,
          dependencia_detalhe: ctx.bloco_b.dependencia_detalhe,
          incidentes: ctx.bloco_b.incidentes,
          incidentes_detalhe: ctx.bloco_b.incidentes_detalhe,
          consequencia_texto: ctx.bloco_b.consequencia_texto,
        });
      }
    }
  }, [currentAnalise]);

  // Helpers para atualizar blocoB (usa tipo oficial)
  const updateBlocoB = <K extends keyof BlocoBEstruturado>(campo: K, valor: BlocoBEstruturado[K]) => {
    setBlocoB(prev => ({ ...prev, [campo]: valor }));
  };

  // Handler para checklist de recursos
  const handleRecursoToggle = (recurso: BlocoBRecurso) => {
    setBlocoB(prev => {
      const recursos = prev.recursos ?? [];
      const novaLista = recursos.includes(recurso)
        ? recursos.filter(r => r !== recurso)
        : [...recursos, recurso];
      return { ...prev, recursos: novaLista };
    });
  };

  // Inicializa recursos como [] quando usuario interage (diferente de undefined)
  const iniciarRecursos = () => {
    if (blocoB.recursos === undefined) {
      setBlocoB(prev => ({ ...prev, recursos: [] }));
    }
  };

  const handleAvancar = async () => {
    // Validar campos obrigatorios do Bloco A
    if (!nomeObjeto.trim() || !objetivoFinalidade.trim() || !areaResponsavel.trim()) {
      alert('Preencha os campos obrigatorios do Bloco A (nome, objetivo, area)');
      return;
    }

    // Validar campos obrigatorios do Bloco B
    // REGRA v2: aceita campo antigo OU novo para cada conceito

    // 1. Recursos: texto antigo OU checklist novo ([] conta como respondido)
    const temRecursos = recursosNecessarios.trim() || blocoB.recursos !== undefined;

    // 2. Atores: apenas texto (nao tem equivalente novo)
    const temAtores = areasAtoresEnvolvidos.trim();

    // 3. Frequencia: selecao antiga OU nova
    const temFrequencia = frequenciaExecucao || blocoB.frequencia;

    // 4. SLA: texto antigo OU radio novo (SIM/NAO/NAO_SEI conta)
    const temSla = prazosSlas.trim() || blocoB.sla;

    // 5. Dependencias: texto antigo OU radio novo
    const temDependencia = dependenciasExternas.trim() || blocoB.dependencia;

    // 6. Historico: texto antigo OU radio novo
    const temHistorico = historicoProblemas.trim() || blocoB.incidentes;

    // 7. Impacto: SEMPRE obrigatorio (ancora)
    const temImpacto = impactoSeFalhar.trim();

    // Validar
    if (!temRecursos || !temAtores || !temFrequencia || !temSla ||
        !temDependencia || !temHistorico || !temImpacto) {
      const faltando: string[] = [];
      if (!temRecursos) faltando.push('recursos');
      if (!temAtores) faltando.push('atores envolvidos');
      if (!temFrequencia) faltando.push('frequencia');
      if (!temSla) faltando.push('prazos/SLAs');
      if (!temDependencia) faltando.push('dependencias');
      if (!temHistorico) faltando.push('historico de problemas');
      if (!temImpacto) faltando.push('impacto se falhar');
      alert(`Preencha os campos obrigatorios do Bloco B: ${faltando.join(', ')}`);
      return;
    }

    // Montar contexto: MERGE de campos antigos + novos
    // Preserva contexto atual para nao perder dados
    const contextoAtual = currentAnalise?.contexto_estruturado ?? { bloco_a: {}, bloco_b: {} };

    const contexto: ContextoEstruturado = {
      bloco_a: {
        ...contextoAtual.bloco_a,
        nome_objeto: nomeObjeto,
        objetivo_finalidade: objetivoFinalidade,
        area_responsavel: areaResponsavel,
        descricao_escopo: descricaoEscopo,
      },
      bloco_b: {
        // Preserva campos existentes
        ...contextoAtual.bloco_b,
        // Campos antigos (texto) - SEMPRE envia
        recursos_necessarios: recursosNecessarios,
        areas_atores_envolvidos: areasAtoresEnvolvidos,
        frequencia_execucao: frequenciaExecucao,
        prazos_slas: prazosSlas,
        dependencias_externas: dependenciasExternas,
        historico_problemas: historicoProblemas,
        impacto_se_falhar: impactoSeFalhar,
        // Campos novos estruturados (so envia se usuario respondeu)
        ...(blocoB.recursos !== undefined && { recursos: blocoB.recursos }),
        ...(blocoB.recursos_outros && { recursos_outros: blocoB.recursos_outros }),
        ...(blocoB.frequencia && { frequencia: blocoB.frequencia }),
        ...(blocoB.sla && { sla: blocoB.sla }),
        ...(blocoB.sla_detalhe && { sla_detalhe: blocoB.sla_detalhe }),
        ...(blocoB.dependencia && { dependencia: blocoB.dependencia }),
        ...(blocoB.dependencia_detalhe && { dependencia_detalhe: blocoB.dependencia_detalhe }),
        ...(blocoB.incidentes && { incidentes: blocoB.incidentes }),
        ...(blocoB.incidentes_detalhe && { incidentes_detalhe: blocoB.incidentes_detalhe }),
      },
    };

    const sucesso = await salvarContexto(contexto);
    if (sucesso) {
      onAvancar();
    }
  };

  const inputStyle = { width: '100%', padding: '8px', marginBottom: '15px' };
  const labelStyle = { display: 'block', marginBottom: '5px', fontWeight: 'bold' as const };
  const radioGroupStyle = { display: 'flex', flexDirection: 'column' as const, gap: '8px', marginBottom: '15px' };
  const checkboxGroupStyle = { display: 'flex', flexWrap: 'wrap' as const, gap: '10px', marginBottom: '15px' };

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

        {/* 1. RECURSOS - Checklist + Outros */}
        <label style={labelStyle}>Quais recursos sao necessarios?</label>
        <div style={checkboxGroupStyle} onClick={iniciarRecursos}>
          {BLOCO_B_RECURSOS.map((r) => (
            <label key={r.valor} style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={blocoB.recursos?.includes(r.valor) ?? false}
                onChange={() => handleRecursoToggle(r.valor)}
              />
              {r.label}
            </label>
          ))}
        </div>
        {blocoB.recursos !== undefined && (
          <input
            type="text"
            value={blocoB.recursos_outros ?? ''}
            onChange={(e) => updateBlocoB('recursos_outros', e.target.value)}
            placeholder="Outros recursos (especificar)"
            style={inputStyle}
          />
        )}

        {/* Fallback: textarea antigo (somente leitura se ja tem estruturado) */}
        {recursosNecessarios && blocoB.recursos === undefined && (
          <>
            <label style={{ ...labelStyle, fontSize: '12px', color: '#6b7280' }}>Texto anterior (legado)</label>
            <textarea
              value={recursosNecessarios}
              onChange={(e) => setRecursosNecessarios(e.target.value)}
              placeholder="Pessoas, sistemas, orcamento, equipamentos..."
              rows={2}
              style={{ ...inputStyle, background: '#f3f4f6' }}
            />
          </>
        )}

        {/* 2. ATORES ENVOLVIDOS - Texto livre */}
        <label style={labelStyle}>Quais areas/atores estao envolvidos?</label>
        <input
          type="text"
          value={areasAtoresEnvolvidos}
          onChange={(e) => setAreasAtoresEnvolvidos(e.target.value)}
          placeholder="Liste as areas e papeis envolvidos"
          style={inputStyle}
        />

        {/* 3. FREQUENCIA - Dropdown */}
        <label style={labelStyle}>Com que frequencia ocorre? *</label>
        <select
          value={blocoB.frequencia || frequenciaExecucao}
          onChange={(e) => {
            const valor = e.target.value as BlocoBFrequencia;
            updateBlocoB('frequencia', valor || undefined);
            setFrequenciaExecucao(e.target.value);  // Mantém sync com campo antigo
          }}
          style={inputStyle}
        >
          <option value="">Selecione...</option>
          {FREQUENCIAS_EXECUCAO.map((f) => (
            <option key={f.valor} value={f.valor}>{f.label}</option>
          ))}
        </select>

        {/* 4. SLA / PRAZOS - Radio group + Detalhe */}
        <label style={labelStyle}>Existem prazos legais ou SLAs?</label>
        <div style={radioGroupStyle}>
          {BLOCO_B_SLA.map((opt) => (
            <label key={opt.valor} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="sla"
                checked={blocoB.sla === opt.valor}
                onChange={() => updateBlocoB('sla', opt.valor)}
              />
              {opt.label}
            </label>
          ))}
        </div>
        {blocoB.sla === 'SIM' && (
          <input
            type="text"
            value={blocoB.sla_detalhe ?? ''}
            onChange={(e) => updateBlocoB('sla_detalhe', e.target.value)}
            placeholder="Descreva os prazos/SLAs aplicaveis"
            style={inputStyle}
          />
        )}
        {/* Fallback texto antigo */}
        {prazosSlas && !blocoB.sla && (
          <>
            <label style={{ ...labelStyle, fontSize: '12px', color: '#6b7280' }}>Texto anterior (legado)</label>
            <input
              type="text"
              value={prazosSlas}
              onChange={(e) => setPrazosSlas(e.target.value)}
              style={{ ...inputStyle, background: '#f3f4f6' }}
            />
          </>
        )}

        {/* 5. DEPENDENCIA EXTERNA - Radio group + Detalhe */}
        <label style={labelStyle}>Ha dependencia de sistemas externos ou terceiros?</label>
        <div style={radioGroupStyle}>
          {BLOCO_B_DEPENDENCIAS.map((opt) => (
            <label key={opt.valor} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="dependencia"
                checked={blocoB.dependencia === opt.valor}
                onChange={() => updateBlocoB('dependencia', opt.valor)}
              />
              {opt.label}
            </label>
          ))}
        </div>
        {blocoB.dependencia && blocoB.dependencia !== 'NAO' && blocoB.dependencia !== 'NAO_SEI' && (
          <input
            type="text"
            value={blocoB.dependencia_detalhe ?? ''}
            onChange={(e) => updateBlocoB('dependencia_detalhe', e.target.value)}
            placeholder="Descreva as dependencias"
            style={inputStyle}
          />
        )}
        {/* Fallback texto antigo */}
        {dependenciasExternas && !blocoB.dependencia && (
          <>
            <label style={{ ...labelStyle, fontSize: '12px', color: '#6b7280' }}>Texto anterior (legado)</label>
            <input
              type="text"
              value={dependenciasExternas}
              onChange={(e) => setDependenciasExternas(e.target.value)}
              style={{ ...inputStyle, background: '#f3f4f6' }}
            />
          </>
        )}

        {/* 6. INCIDENTES / HISTORICO - Radio group + Detalhe */}
        <label style={labelStyle}>Ja houve problemas ou incidentes anteriores?</label>
        <div style={radioGroupStyle}>
          {BLOCO_B_INCIDENTES.map((opt) => (
            <label key={opt.valor} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="incidentes"
                checked={blocoB.incidentes === opt.valor}
                onChange={() => updateBlocoB('incidentes', opt.valor)}
              />
              {opt.label}
            </label>
          ))}
        </div>
        {blocoB.incidentes === 'SIM' && (
          <textarea
            value={blocoB.incidentes_detalhe ?? ''}
            onChange={(e) => updateBlocoB('incidentes_detalhe', e.target.value)}
            placeholder="Descreva os incidentes/problemas"
            rows={2}
            style={inputStyle}
          />
        )}
        {/* Fallback texto antigo */}
        {historicoProblemas && !blocoB.incidentes && (
          <>
            <label style={{ ...labelStyle, fontSize: '12px', color: '#6b7280' }}>Texto anterior (legado)</label>
            <textarea
              value={historicoProblemas}
              onChange={(e) => setHistoricoProblemas(e.target.value)}
              rows={2}
              style={{ ...inputStyle, background: '#f3f4f6' }}
            />
          </>
        )}

        {/* 7. IMPACTO / CONSEQUENCIA - Texto livre (ancora) */}
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
