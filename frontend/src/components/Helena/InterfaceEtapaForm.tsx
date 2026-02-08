import React, { useState } from "react";
import DocumentoSelector, { TipoDocumento } from "./DocumentoSelector";

interface InterfaceEtapaFormProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

/**
 * Formulario completo para coleta de 1 etapa (campos lineares).
 * Condicionais (cenarios/subetapas) sao coletados em etapa separada se toggle ativo.
 *
 * Submit envia: {"etapa": {descricao, operador_nome, sistemas, docs_requeridos,
 *   docs_gerados, detalhes, tempo_estimado, is_condicional}}
 */
const InterfaceEtapaForm: React.FC<InterfaceEtapaFormProps> = ({ dados, onConfirm }) => {
  const numeroEtapa = (dados?.numero_etapa as number) || 1;
  const operadores = (dados?.operadores as string[]) || [];
  const sistemas = (dados?.sistemas as Record<string, string[]>) || {};
  const tiposDocsRequeridos = (dados?.tipos_documentos_requeridos as TipoDocumento[]) || [];
  const tiposDocsGerados = (dados?.tipos_documentos_gerados as TipoDocumento[]) || [];

  // Form state
  const [descricao, setDescricao] = useState('');
  const [operador, setOperador] = useState('');
  const [sistemasSelecionados, setSistemasSelecionados] = useState<string[]>([]);
  const [sistemaManual, setSistemaManual] = useState('');
  const [docsRequeridos, setDocsRequeridos] = useState<string[]>([]);
  const [docsGerados, setDocsGerados] = useState<string[]>([]);
  const [detalhesTexto, setDetalhesTexto] = useState('');
  const [tempoEstimado, setTempoEstimado] = useState('');
  const [isCondicional, setIsCondicional] = useState(false);
  const [erro, setErro] = useState('');

  // Flat list of all systems
  const todosSistemas = Object.values(sistemas).flat();

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

  const handleSubmit = () => {
    // Validar descricao
    if (!descricao.trim()) {
      setErro('A descricao da etapa e obrigatoria.');
      return;
    }
    setErro('');

    // Parse detalhes: 1 por linha
    const detalhes = detalhesTexto
      .split('\n')
      .map(l => l.trim())
      .filter(l => l.length > 0);

    const payload = {
      etapa: {
        descricao: descricao.trim(),
        operador_nome: operador || 'Nao especificado',
        sistemas: sistemasSelecionados,
        docs_requeridos: docsRequeridos,
        docs_gerados: docsGerados,
        detalhes,
        tempo_estimado: tempoEstimado.trim() || null,
        is_condicional: isCondicional,
      }
    };

    onConfirm(JSON.stringify(payload));
  };

  const sectionStyle: React.CSSProperties = {
    marginBottom: '1.25rem',
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

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '0.5rem 0.75rem',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '0.9rem',
    boxSizing: 'border-box',
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title" style={{ fontSize: '1.1rem', color: '#1351B4', marginBottom: '1rem' }}>
        Etapa {numeroEtapa}
      </div>

      {erro && (
        <div style={{ padding: '0.5rem 1rem', background: '#f8d7da', color: '#721c24', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.85rem' }}>
          {erro}
        </div>
      )}

      {/* Descricao */}
      <div style={sectionStyle}>
        <label style={labelStyle}>O que e feito nesta etapa? *</label>
        <textarea
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          placeholder="Ex: Receber documento pelo SEI e analisar conformidade"
          style={{ ...inputStyle, minHeight: '60px', resize: 'vertical' }}
        />
      </div>

      {/* Operador */}
      <div style={sectionStyle}>
        <label style={labelStyle}>Quem executa?</label>
        {operadores.length > 0 ? (
          <select
            value={operador}
            onChange={(e) => setOperador(e.target.value)}
            style={inputStyle}
          >
            <option value="">Selecione...</option>
            {operadores.map(op => (
              <option key={op} value={op}>{op}</option>
            ))}
          </select>
        ) : (
          <input
            type="text"
            value={operador}
            onChange={(e) => setOperador(e.target.value)}
            placeholder="Cargo ou funcao"
            style={inputStyle}
          />
        )}
      </div>

      {/* Sistemas */}
      <div style={sectionStyle}>
        <label style={labelStyle}>Sistemas utilizados</label>
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
      </div>

      {/* Docs Requeridos */}
      <div style={sectionStyle}>
        <DocumentoSelector
          tipos={tiposDocsRequeridos}
          value={docsRequeridos}
          onChange={setDocsRequeridos}
          titulo="Documentos analisados/requeridos"
        />
      </div>

      {/* Docs Gerados */}
      <div style={sectionStyle}>
        <DocumentoSelector
          tipos={tiposDocsGerados}
          value={docsGerados}
          onChange={setDocsGerados}
          titulo="Documentos produzidos/gerados"
        />
      </div>

      {/* Detalhes */}
      <div style={sectionStyle}>
        <label style={labelStyle}>Detalhes / sub-acoes (opcional)</label>
        <textarea
          value={detalhesTexto}
          onChange={(e) => setDetalhesTexto(e.target.value)}
          placeholder={"Uma por linha. Ex:\nVerificar documentacao\nConferir dados no SIAPE\nEncaminhar despacho"}
          style={{ ...inputStyle, minHeight: '60px', resize: 'vertical' }}
        />
        <div style={{ fontSize: '0.75rem', color: '#6c757d', marginTop: '0.25rem' }}>
          Cada linha vira um sub-item da etapa.
        </div>
      </div>

      {/* Tempo estimado */}
      <div style={sectionStyle}>
        <label style={labelStyle}>Tempo estimado (opcional)</label>
        <input
          type="text"
          value={tempoEstimado}
          onChange={(e) => setTempoEstimado(e.target.value)}
          placeholder="Ex: 30 minutos, 2 horas, 1 dia util"
          style={inputStyle}
        />
      </div>

      {/* Condicional toggle */}
      <div style={{ ...sectionStyle, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <label style={{ ...labelStyle, marginBottom: 0, flex: 1 }}>
          Esta etapa tem uma decisao condicional?
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
      {isCondicional && (
        <div style={{ padding: '0.75rem 1rem', background: '#fff3cd', borderRadius: '6px', fontSize: '0.8rem', color: '#856404', marginBottom: '1rem', marginTop: '-0.75rem' }}>
          Apos confirmar, a Helena vai guiar voce nos cenarios e sub-etapas desta decisao.
        </div>
      )}

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
        }}
      >
        Confirmar Etapa {numeroEtapa}
      </button>
    </div>
  );
};

export default InterfaceEtapaForm;
