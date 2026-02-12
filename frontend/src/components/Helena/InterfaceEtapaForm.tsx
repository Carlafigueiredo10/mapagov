import React, { useState, useCallback } from "react";
import DocumentoSelector, { TipoDocumento } from "./DocumentoSelector";

interface CenarioInput {
  condicao: string;
  acao: string;
}

interface InterfaceEtapaFormProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

/**
 * Formulario guiado por blocos para coleta de 1 etapa.
 * 3 blocos cognitivos: Acao principal → Verificacoes → Encerramento/Caminhos
 * + secao colapsavel: Responsabilidade, Entradas/Saidas, Recursos, Tempo
 *
 * Submit envia: {"etapa": {acao_principal, verificacoes, operador_nome, sistemas,
 *   docs_requeridos, docs_gerados, tempo_estimado, is_condicional, cenarios_input}}
 */
const InterfaceEtapaForm: React.FC<InterfaceEtapaFormProps> = ({ dados, onConfirm }) => {
  const numeroEtapa = (dados?.numero_etapa as number) || 1;
  const operadores = (dados?.operadores as string[]) || [];
  const sistemas = (dados?.sistemas as Record<string, string[]>) || {};
  const tiposDocsRequeridos = (dados?.tipos_documentos_requeridos as TipoDocumento[]) || [];
  const tiposDocsGerados = (dados?.tipos_documentos_gerados as TipoDocumento[]) || [];

  // Pre-fill para edicao (Step 11 — dados.etapa_preenchida)
  const prefill = (dados?.etapa_preenchida as Record<string, unknown>) || {};

  // ── Bloco 1 — Acao principal ──
  const [acaoPrincipal, setAcaoPrincipal] = useState(
    (prefill.acao_principal as string) || (prefill.descricao as string) || ''
  );

  // ── Bloco 2 — Verificacoes (lista incremental) ──
  const prefillVerificacoes = (prefill.verificacoes as string[]) || (prefill.detalhes as string[]) || [];
  const [verificacoes, setVerificacoes] = useState<string[]>(
    prefillVerificacoes.length > 0 ? prefillVerificacoes : ['']
  );

  // ── Bloco 3 — Encerramento / Caminhos (default: Sim, usuario marca Nao) ──
  const [isCondicional, setIsCondicional] = useState(
    prefill.id
      ? (prefill.tipo === 'condicional' || (prefill.is_condicional as boolean) || false)
      : true
  );
  const prefillCenarios = (prefill.cenarios as Array<{ descricao?: string; condicao?: string }>) || [];
  const [cenarios, setCenarios] = useState<CenarioInput[]>(
    prefillCenarios.length > 0
      ? prefillCenarios.map(c => ({
          condicao: c.condicao || c.descricao?.split('→')[0]?.replace(/^Se\s*/i, '').trim() || '',
          acao: c.descricao?.split('→')[1]?.trim() || '',
        }))
      : [{ condicao: '', acao: '' }, { condicao: '', acao: '' }]
  );

  // ── Campos complementares (secao colapsavel) ──
  const [operador, setOperador] = useState((prefill.operador_nome as string) || '');
  const [sistemasSelecionados, setSistemasSelecionados] = useState<string[]>(
    (prefill.sistemas as string[]) || []
  );
  const [sistemaManual, setSistemaManual] = useState('');
  const [docsRequeridos, setDocsRequeridos] = useState<string[]>(
    (prefill.docs_requeridos as string[]) || []
  );
  const [docsGerados, setDocsGerados] = useState<string[]>(
    (prefill.docs_gerados as string[]) || []
  );
  const [tempoEstimado, setTempoEstimado] = useState(
    (prefill.tempo_estimado as string) || ''
  );

  // ── Modo avancado (sintese) ──
  const [modoAvancado, setModoAvancado] = useState(false);
  const [descricaoManual, setDescricaoManual] = useState('');
  const [foiEditadoManual, setFoiEditadoManual] = useState(false);

  // ── UI state ──
  const [complementaresAberto, setComplementaresAberto] = useState(true);
  const [erro, setErro] = useState('');

  // Scroll suave para o primeiro campo com erro
  const scrollParaErro = useCallback((primeiroErro: string) => {
    const erroParaId: Record<string, string> = {
      'Acao principal': 'ef-bloco-acao',
      'Pelo menos 1 verificacao': 'ef-bloco-verificacoes',
      'Pelo menos 2 cenarios com condicao': 'ef-bloco-cenarios',
      'Responsavel': 'ef-campo-operador',
      'Pelo menos 1 sistema': 'ef-campo-sistemas',
      'Pelo menos 1 documento consultado/recebido': 'ef-campo-docs-req',
      'Pelo menos 1 documento gerado': 'ef-campo-docs-ger',
      'Tempo estimado': 'ef-campo-tempo',
    };
    const targetId = erroParaId[primeiroErro];
    if (!targetId) return;
    setTimeout(() => {
      const el = document.getElementById(targetId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.style.boxShadow = '0 0 0 3px rgba(220, 53, 69, 0.4)';
        el.style.borderRadius = '8px';
        setTimeout(() => { el.style.boxShadow = ''; }, 2500);
      }
    }, 150);
  }, []);

  const todosSistemas = Object.values(sistemas).flat();

  // ── Handlers: Verificacoes ──
  const atualizarVerificacao = (idx: number, valor: string) => {
    setVerificacoes(prev => prev.map((v, i) => i === idx ? valor : v));
  };

  const adicionarVerificacao = () => {
    setVerificacoes(prev => [...prev, '']);
  };

  const removerVerificacao = (idx: number) => {
    if (verificacoes.length <= 1) return;
    setVerificacoes(prev => prev.filter((_, i) => i !== idx));
  };

  // ── Handlers: Cenarios ──
  const atualizarCenario = (idx: number, campo: 'condicao' | 'acao', valor: string) => {
    setCenarios(prev => prev.map((c, i) => i === idx ? { ...c, [campo]: valor } : c));
  };

  const adicionarCenario = () => {
    setCenarios(prev => [...prev, { condicao: '', acao: '' }]);
  };

  const removerCenario = (idx: number) => {
    if (cenarios.length <= 2) return;
    setCenarios(prev => prev.filter((_, i) => i !== idx));
  };

  // ── Handlers: Sistemas ──
  const toggleSistema = (s: string) => {
    setSistemasSelecionados(prev =>
      prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]
    );
  };

  const adicionarSistemaManual = () => {
    const s = sistemaManual.trim();
    if (s && !sistemasSelecionados.includes(s)) {
      setSistemasSelecionados(prev => [...prev, s]);
      setSistemaManual('');
    }
  };

  // ── Sintese automatica ──
  const gerarSintese = (): string => {
    const partes: string[] = [];
    if (acaoPrincipal.trim()) {
      partes.push(acaoPrincipal.trim());
    }
    const verifLimpas = verificacoes.map(v => v.trim()).filter(v => v);
    if (verifLimpas.length > 0) {
      partes.push(verifLimpas.join('. '));
    }
    if (isCondicional) {
      const cenariosValidos = cenarios.filter(c => c.condicao.trim());
      if (cenariosValidos.length > 0) {
        const resumo = cenariosValidos
          .map(c => `Se ${c.condicao.trim()} → ${c.acao.trim() || '...'}`)
          .join('; ');
        partes.push(resumo);
      }
    }
    return partes.join('. ') + (partes.length > 0 ? '.' : '');
  };

  const handleAbrirModoAvancado = () => {
    if (!modoAvancado) {
      // Preencher com sintese ao abrir pela primeira vez
      if (!foiEditadoManual) {
        setDescricaoManual(gerarSintese());
      }
    }
    setModoAvancado(!modoAvancado);
  };

  const handleDescricaoManualChange = (valor: string) => {
    setDescricaoManual(valor);
    setFoiEditadoManual(true);
  };

  // ── Submit (todos os campos obrigatorios) ──
  const handleSubmit = () => {
    const erros: string[] = [];

    if (!acaoPrincipal.trim()) erros.push('Acao principal');

    const verifPreenchidas = verificacoes.filter(v => v.trim().length > 0);
    if (verifPreenchidas.length === 0) erros.push('Pelo menos 1 verificacao');

    if (isCondicional) {
      const cenariosPreenchidos = cenarios.filter(c => c.condicao.trim());
      if (cenariosPreenchidos.length < 2) erros.push('Pelo menos 2 cenarios com condicao');
    }

    if (!operador.trim()) erros.push('Responsavel');
    if (sistemasSelecionados.length === 0) erros.push('Pelo menos 1 sistema');
    if (docsRequeridos.length === 0) erros.push('Pelo menos 1 documento consultado/recebido');
    if (docsGerados.length === 0) erros.push('Pelo menos 1 documento gerado');
    if (!tempoEstimado.trim()) erros.push('Tempo estimado');

    if (erros.length > 0) {
      setErro(`Campos obrigatorios: ${erros.join(', ')}.`);
      // Abrir complementares se algum erro e de la
      if (!operador.trim() || sistemasSelecionados.length === 0 || docsRequeridos.length === 0 || docsGerados.length === 0 || !tempoEstimado.trim()) {
        setComplementaresAberto(true);
      }
      scrollParaErro(erros[0]);
      return;
    }
    setErro('');

    const verificacoesLimpas = verificacoes
      .map(v => v.trim())
      .filter(v => v.length > 0);

    // descricao: se editou manualmente usa manual, senao gera sintese
    const descricaoFinal = foiEditadoManual && descricaoManual.trim()
      ? descricaoManual.trim()
      : gerarSintese();

    const payload: Record<string, unknown> = {
      etapa: {
        acao_principal: acaoPrincipal.trim(),
        descricao: descricaoFinal, // sintese ou manual (alias retrocompat)
        operador_nome: operador || 'Nao especificado',
        sistemas: sistemasSelecionados,
        docs_requeridos: docsRequeridos,
        docs_gerados: docsGerados,
        verificacoes: verificacoesLimpas,
        detalhes: verificacoesLimpas, // alias retrocompat
        tempo_estimado: tempoEstimado.trim() || null,
        is_condicional: isCondicional,
        ...(isCondicional && {
          cenarios_input: cenarios
            .filter(c => c.condicao.trim() || c.acao.trim())
            .map(c => ({
              condicao: c.condicao.trim(),
              acao: c.acao.trim(),
            })),
        }),
        // Preservar id se editando
        ...(prefill.id ? { id: prefill.id } : {}),
      }
    };

    onConfirm(JSON.stringify(payload));
  };

  // ── Styles ──
  const sectionStyle: React.CSSProperties = {
    marginBottom: '0.75rem',
    padding: '1rem',
    background: '#f8f9fa',
    borderRadius: '8px',
    border: '1px solid #dee2e6',
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    fontWeight: 600,
    color: '#333',
    fontSize: '0.9rem',
    marginBottom: '0.4rem',
  };

  const helperStyle: React.CSSProperties = {
    fontSize: '0.75rem',
    color: '#6c757d',
    marginTop: '0.3rem',
    lineHeight: 1.4,
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '0.5rem 0.75rem',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '0.9rem',
    boxSizing: 'border-box',
  };

  const blocoHeaderStyle: React.CSSProperties = {
    fontSize: '0.8rem',
    fontWeight: 700,
    color: '#1351B4',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: '0.5rem',
    marginTop: '1.25rem',
  };

  const miniButtonStyle: React.CSSProperties = {
    padding: '0.25rem 0.5rem',
    border: 'none',
    borderRadius: '4px',
    fontSize: '0.75rem',
    cursor: 'pointer',
    fontWeight: 500,
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title" style={{ fontSize: '1.1rem', color: '#1351B4', marginBottom: '0.5rem' }}>
        {prefill.id ? `Editar Etapa ${numeroEtapa}` : `Etapa ${numeroEtapa}`}
      </div>

      <div style={{
        padding: '0.5rem 0.75rem',
        background: '#e8f4fd',
        borderRadius: '6px',
        fontSize: '0.78rem',
        color: '#1351B4',
        marginBottom: '1rem',
        lineHeight: 1.4,
      }}>
        Todos os campos sao obrigatorios. Preencha cada secao antes de confirmar.
      </div>

      {erro && (
        <div style={{ padding: '0.5rem 1rem', background: '#f8d7da', color: '#721c24', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.85rem' }}>
          {erro}
        </div>
      )}

      {/* ════════════════════════════════════════════
          BLOCO 1 — ACAO PRINCIPAL
          ════════════════════════════════════════════ */}
      <div style={blocoHeaderStyle}>O que e feito</div>

      <div id="ef-bloco-acao" style={sectionStyle}>
        <label style={labelStyle}>O que e feito nesta etapa? *</label>
        <input
          type="text"
          value={acaoPrincipal}
          onChange={(e) => setAcaoPrincipal(e.target.value)}
          placeholder="Analisar requerimento recebido no sistema"
          maxLength={150}
          style={inputStyle}
        />
        <div style={helperStyle}>
          Uma frase curta com a acao concreta. Use verbo no infinitivo + objeto.
        </div>
      </div>

      {/* ════════════════════════════════════════════
          BLOCO 2 — VERIFICACOES
          ════════════════════════════════════════════ */}
      <div style={blocoHeaderStyle}>O que e verificado / conferido</div>

      <div id="ef-bloco-verificacoes" style={sectionStyle}>
        <label style={labelStyle}>Quais verificacoes sao feitas nesta etapa? *</label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {verificacoes.map((v, idx) => (
            <div key={idx} style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
              <span style={{ color: '#6c757d', fontSize: '0.8rem', minWidth: '1.2rem' }}>{idx + 1}.</span>
              <input
                type="text"
                value={v}
                onChange={(e) => atualizarVerificacao(idx, e.target.value)}
                placeholder={idx === 0 ? 'Conferir dados no sistema' : 'Outra verificacao...'}
                style={{ ...inputStyle, flex: 1 }}
              />
              {verificacoes.length > 1 && (
                <button
                  type="button"
                  onClick={() => removerVerificacao(idx)}
                  style={{
                    ...miniButtonStyle,
                    background: 'transparent',
                    color: '#dc3545',
                    fontSize: '1rem',
                    padding: '0.1rem 0.4rem',
                  }}
                  title="Remover"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={adicionarVerificacao}
          style={{
            ...miniButtonStyle,
            background: '#e8f0fe',
            color: '#1351B4',
            marginTop: '0.5rem',
          }}
        >
          + Adicionar verificacao
        </button>
        <div style={helperStyle}>
          Cada item e algo que o responsavel confere, valida ou registra nesta etapa.
          Se nao ha verificacoes, pode deixar em branco.
        </div>
      </div>

      {/* ════════════════════════════════════════════
          BLOCO 3 — ENCERRAMENTO / CAMINHOS
          ════════════════════════════════════════════ */}
      <div style={blocoHeaderStyle}>Encerramento da etapa</div>

      <div id="ef-bloco-cenarios" style={sectionStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <label style={{ ...labelStyle, marginBottom: 0, flex: 1 }}>
            Pode ter caminhos diferentes dependendo da situacao? *
          </label>
          <button
            type="button"
            onClick={() => setIsCondicional(!isCondicional)}
            style={{
              padding: '0.4rem 1rem',
              borderRadius: '20px',
              border: 'none',
              background: isCondicional ? '#1351B4' : '#dee2e6',
              color: isCondicional ? 'white' : '#495057',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '0.85rem',
              transition: 'all 0.2s',
            }}
          >
            {isCondicional ? 'Sim' : 'Nao'}
          </button>
        </div>

        {!isCondicional && (
          <div style={helperStyle}>
            A etapa segue sempre o mesmo caminho — fluxo linear.
          </div>
        )}

        {isCondicional && (
          <div style={{ marginTop: '0.75rem' }}>
            <div style={{
              padding: '0.5rem 0.75rem',
              background: '#fff3cd',
              borderRadius: '6px',
              fontSize: '0.8rem',
              color: '#856404',
              marginBottom: '0.75rem',
            }}>
              Defina os cenarios possiveis. A Helena vai detalhar as sub-etapas de cada caminho depois.
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {cenarios.map((c, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  gap: '0.4rem',
                  alignItems: 'center',
                  padding: '0.5rem',
                  background: '#fff',
                  borderRadius: '6px',
                  border: '1px solid #e9ecef',
                }}>
                  <span style={{ color: '#6c757d', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>Se</span>
                  <input
                    type="text"
                    value={c.condicao}
                    onChange={(e) => atualizarCenario(idx, 'condicao', e.target.value)}
                    placeholder={idx === 0 ? 'documentacao completa' : 'outra situacao'}
                    style={{ ...inputStyle, flex: 1, fontSize: '0.85rem' }}
                  />
                  <span style={{ color: '#6c757d', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>→</span>
                  <input
                    type="text"
                    value={c.acao}
                    onChange={(e) => atualizarCenario(idx, 'acao', e.target.value)}
                    placeholder={idx === 0 ? 'registrar no sistema' : 'acao correspondente'}
                    style={{ ...inputStyle, flex: 1, fontSize: '0.85rem' }}
                  />
                  {cenarios.length > 2 && (
                    <button
                      type="button"
                      onClick={() => removerCenario(idx)}
                      style={{
                        ...miniButtonStyle,
                        background: 'transparent',
                        color: '#dc3545',
                        fontSize: '1rem',
                        padding: '0.1rem 0.4rem',
                      }}
                      title="Remover cenario"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>

            <button
              type="button"
              onClick={adicionarCenario}
              style={{
                ...miniButtonStyle,
                background: '#e8f0fe',
                color: '#1351B4',
                marginTop: '0.5rem',
              }}
            >
              + Adicionar cenario
            </button>
          </div>
        )}
      </div>

      {/* ════════════════════════════════════════════
          MODO AVANCADO — Descricao sintetizada
          ════════════════════════════════════════════ */}
      <div style={{ marginTop: '0.75rem', textAlign: 'right' }}>
        <button
          type="button"
          onClick={handleAbrirModoAvancado}
          style={{
            background: 'none',
            border: 'none',
            color: '#6c757d',
            fontSize: '0.78rem',
            cursor: 'pointer',
            textDecoration: 'underline',
            padding: 0,
          }}
        >
          {modoAvancado ? 'Fechar modo avancado' : 'Modo avancado: editar descricao completa'}
        </button>
      </div>

      {modoAvancado && (
        <div style={{
          ...sectionStyle,
          background: foiEditadoManual ? '#fff8e1' : '#f8f9fa',
          borderColor: foiEditadoManual ? '#ffc107' : '#dee2e6',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <label style={labelStyle}>Descricao completa da etapa</label>
            {foiEditadoManual && (
              <span style={{
                fontSize: '0.65rem',
                background: '#ffc107',
                color: '#333',
                padding: '0.1rem 0.4rem',
                borderRadius: '8px',
                fontWeight: 500,
              }}>
                editado
              </span>
            )}
          </div>
          <textarea
            value={descricaoManual}
            onChange={(e) => handleDescricaoManualChange(e.target.value)}
            rows={4}
            style={{ ...inputStyle, resize: 'vertical', fontSize: '0.85rem' }}
          />
          <div style={helperStyle}>
            Gerado automaticamente a partir dos blocos acima. Edite apenas se necessario.
          </div>
        </div>
      )}

      {/* ════════════════════════════════════════════
          CAMPOS COMPLEMENTARES (colapsavel)
          ════════════════════════════════════════════ */}
      <div
        style={{
          marginTop: '1rem',
          borderTop: '1px solid #dee2e6',
          paddingTop: '0.75rem',
        }}
      >
        <button
          type="button"
          onClick={() => setComplementaresAberto(!complementaresAberto)}
          style={{
            background: 'none',
            border: 'none',
            color: '#1351B4',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            padding: '0.25rem 0',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          {complementaresAberto ? '\u25BC' : '\u25B6'} Responsavel, sistemas, documentos e tempo
          {!complementaresAberto && (operador || sistemasSelecionados.length > 0 || docsRequeridos.length > 0 || docsGerados.length > 0 || tempoEstimado) && (
            <span style={{
              fontSize: '0.7rem',
              background: '#e8f0fe',
              color: '#1351B4',
              padding: '0.15rem 0.5rem',
              borderRadius: '10px',
              fontWeight: 500,
            }}>
              preenchido
            </span>
          )}
        </button>

        {complementaresAberto && (
          <div style={{ marginTop: '0.75rem' }}>
            {/* Responsavel */}
            <div id="ef-campo-operador" style={sectionStyle}>
              <label style={labelStyle}>Quem executa esta etapa? *</label>
              {operadores.length > 0 ? (
                <select
                  value={operador}
                  onChange={(e) => setOperador(e.target.value)}
                  style={inputStyle}
                >
                  <option value="">Selecione o responsavel...</option>
                  {operadores.map(op => (
                    <option key={op} value={op}>{op}</option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={operador}
                  onChange={(e) => setOperador(e.target.value)}
                  placeholder="Cargo ou funcao responsavel"
                  style={inputStyle}
                />
              )}
              <div style={helperStyle}>
                Selecione o papel responsavel pela execucao direta da etapa.
              </div>
            </div>

            {/* Docs consultados/recebidos */}
            <div id="ef-campo-docs-req" style={sectionStyle}>
              <DocumentoSelector
                tipos={tiposDocsRequeridos}
                value={docsRequeridos}
                onChange={setDocsRequeridos}
                titulo="O que e consultado ou recebido nesta etapa? *"
              />
              <div style={helperStyle}>
                Marque os documentos ou dados usados como entrada para executar a etapa.
              </div>
            </div>

            {/* Docs produzidos */}
            <div id="ef-campo-docs-ger" style={sectionStyle}>
              <DocumentoSelector
                tipos={tiposDocsGerados}
                value={docsGerados}
                onChange={setDocsGerados}
                titulo="O que e gerado como resultado desta etapa? *"
              />
              <div style={helperStyle}>
                Marque os documentos ou registros produzidos como resultado da execucao.
              </div>
            </div>

            {/* Sistemas */}
            <div id="ef-campo-sistemas" style={sectionStyle}>
              <label style={labelStyle}>Quais sistemas sao utilizados? *</label>
              {todosSistemas.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '0.5rem' }}>
                  {todosSistemas.map(s => {
                    const ativo = sistemasSelecionados.includes(s);
                    return (
                      <button
                        key={s}
                        type="button"
                        onClick={() => toggleSistema(s)}
                        style={{
                          padding: '0.3rem 0.6rem',
                          borderRadius: '4px',
                          border: ativo ? '1px solid #1351B4' : '1px solid #ced4da',
                          background: ativo ? '#e8f0fe' : 'white',
                          color: ativo ? '#1351B4' : '#495057',
                          fontSize: '0.8rem',
                          cursor: 'pointer',
                          fontWeight: ativo ? 600 : 400,
                        }}
                      >
                        {ativo ? '\u2713 ' : ''}{s}
                      </button>
                    );
                  })}
                </div>
              )}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  value={sistemaManual}
                  onChange={(e) => setSistemaManual(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); adicionarSistemaManual(); } }}
                  placeholder="Outro sistema..."
                  style={{ ...inputStyle, flex: 1 }}
                />
                <button
                  type="button"
                  onClick={adicionarSistemaManual}
                  disabled={!sistemaManual.trim()}
                  style={{
                    padding: '0.5rem 0.75rem',
                    background: sistemaManual.trim() ? '#1351B4' : '#adb5bd',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: sistemaManual.trim() ? 'pointer' : 'not-allowed',
                    fontSize: '0.8rem',
                  }}
                >
                  + Adicionar
                </button>
              </div>
              <div style={helperStyle}>
                Selecione os sistemas usados diretamente na execucao da etapa.
              </div>
            </div>

            {/* Tempo estimado */}
            <div id="ef-campo-tempo" style={sectionStyle}>
              <label style={labelStyle}>Tempo estimado de execucao *</label>
              <input
                type="text"
                value={tempoEstimado}
                onChange={(e) => setTempoEstimado(e.target.value)}
                placeholder="Ex: 30 minutos, 2 horas, 1 dia util"
                style={inputStyle}
              />
              <div style={helperStyle}>
                Informe uma estimativa media de duracao desta etapa.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        style={{
          width: '100%',
          padding: '0.85rem',
          background: '#1351B4',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontWeight: 600,
          fontSize: '1rem',
          cursor: 'pointer',
          transition: 'background 0.2s',
          marginTop: '1rem',
        }}
      >
        {prefill.id ? `Salvar Etapa ${numeroEtapa}` : `Confirmar Etapa ${numeroEtapa}`}
      </button>
    </div>
  );
};

export default InterfaceEtapaForm;
