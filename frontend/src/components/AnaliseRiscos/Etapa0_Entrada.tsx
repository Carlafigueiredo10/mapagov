/**
 * Etapa0_Entrada - Selecao do tipo de objeto e modo de entrada
 */
import React, { useState, useRef } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import { TIPOS_ORIGEM, TipoOrigem, ModoEntrada } from '../../types/analiseRiscos.types';

interface Props {
  onAvancar: (textoExtraido?: string) => void;
}

const MODOS_ENTRADA = [
  { valor: 'QUESTIONARIO' as ModoEntrada, label: 'Vou explicar a ideia', descricao: 'Preencher manualmente o contexto', icone: '📝' },
  { valor: 'PDF' as ModoEntrada, label: 'Tenho documento', descricao: 'Upload de PDF formalizado', icone: '📄' },
  { valor: 'ID' as ModoEntrada, label: 'Já existe no MapaGov', descricao: 'Buscar por ID no sistema', icone: '🔍' },
];

const Etapa0Entrada: React.FC<Props> = ({ onAvancar }) => {
  const { criarAnaliseV2, loading } = useAnaliseRiscosStore();

  // Etapa interna: 1 = tipo, 2 = modo
  const [etapaInterna, setEtapaInterna] = useState(1);
  const [tipoOrigem, setTipoOrigem] = useState<TipoOrigem | null>(null);
  const [modoEntrada, setModoEntrada] = useState<ModoEntrada | null>(null);

  // Para modo PDF
  const [arquivoPdf, setArquivoPdf] = useState<File | null>(null);
  const [textoExtraido, setTextoExtraido] = useState('');
  const [extraindo, setExtraindo] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Para modo ID
  const [origemId, setOrigemId] = useState('');

  const [erro, setErro] = useState('');

  const handleSelecionarTipo = (tipo: TipoOrigem) => {
    setTipoOrigem(tipo);
    setEtapaInterna(2);
  };

  const handleSelecionarModo = (modo: ModoEntrada) => {
    setModoEntrada(modo);
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setErro('Apenas arquivos PDF sao aceitos');
      return;
    }

    setArquivoPdf(file);
    setErro('');

    // Extrair texto do PDF
    setExtraindo(true);
    try {
      const formData = new FormData();
      formData.append('pdf_file', file);

      const response = await fetch('/api/extract-pdf/', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setTextoExtraido(data.texto || data.text || '');
      } else {
        setErro('Erro ao extrair texto do PDF');
      }
    } catch {
      setErro('Erro ao processar PDF');
    } finally {
      setExtraindo(false);
    }
  };

  const handleIniciar = async () => {
    if (!tipoOrigem || !modoEntrada) return;

    // Validacoes por modo
    if (modoEntrada === 'PDF' && !arquivoPdf) {
      setErro('Selecione um arquivo PDF');
      return;
    }
    if (modoEntrada === 'ID' && !origemId.trim()) {
      setErro('Informe o ID do objeto');
      return;
    }

    setErro('');

    // Aguardar criacao da analise antes de avancar
    const analiseId = await criarAnaliseV2(
      modoEntrada,
      tipoOrigem,
      modoEntrada === 'ID' ? origemId : undefined
    );

    if (!analiseId) {
      setErro('Erro ao criar analise. Tente novamente.');
      return;
    }

    // Avanca somente apos criacao bem-sucedida
    onAvancar(textoExtraido);
  };

  // ETAPA 1: Selecao do tipo de objeto
  if (etapaInterna === 1) {
    return (
      <div>
        <h3>O que voce quer analisar?</h3>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          Selecione o tipo de objeto que sera avaliado quanto a riscos.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
          {TIPOS_ORIGEM.map((tipo) => (
            <button
              key={tipo.valor}
              onClick={() => handleSelecionarTipo(tipo.valor)}
              style={{
                padding: '20px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                background: 'white',
                cursor: 'pointer',
                fontSize: '16px',
                transition: 'all 0.2s',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.borderColor = '#3b82f6';
                e.currentTarget.style.background = '#eff6ff';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.borderColor = '#ddd';
                e.currentTarget.style.background = 'white';
              }}
            >
              {tipo.label}
            </button>
          ))}
        </div>
      </div>
    );
  }

  // ETAPA 2: Selecao do modo de entrada
  return (
    <div>
      <button
        onClick={() => setEtapaInterna(1)}
        style={{ background: 'none', border: 'none', color: '#3b82f6', cursor: 'pointer', marginBottom: '15px' }}
      >
        ← Voltar
      </button>

      <h3>Como voce vai informar sobre o {tipoOrigem?.toLowerCase()}?</h3>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Escolha como deseja fornecer as informacoes para analise.
      </p>

      {/* Selecao do modo */}
      <div style={{ display: 'flex', gap: '15px', marginBottom: '25px' }}>
        {MODOS_ENTRADA.map((modo) => (
          <button
            key={modo.valor}
            onClick={() => handleSelecionarModo(modo.valor)}
            style={{
              flex: 1,
              padding: '20px',
              border: modoEntrada === modo.valor ? '2px solid #3b82f6' : '1px solid #ddd',
              borderRadius: '8px',
              background: modoEntrada === modo.valor ? '#eff6ff' : 'white',
              cursor: 'pointer',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '28px', marginBottom: '10px' }}>{modo.icone}</div>
            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{modo.label}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{modo.descricao}</div>
          </button>
        ))}
      </div>

      {/* Campos condicionais por modo */}
      {modoEntrada === 'PDF' && (
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
            Upload do documento
          </label>
          <div
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: '2px dashed #ccc',
              borderRadius: '8px',
              padding: '30px',
              textAlign: 'center',
              cursor: 'pointer',
              background: arquivoPdf ? '#f0fdf4' : '#fafafa',
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            {extraindo ? (
              <span style={{ color: '#666' }}>Extraindo texto...</span>
            ) : arquivoPdf ? (
              <div>
                <span style={{ color: '#10b981', fontWeight: 'bold' }}>✓ {arquivoPdf.name}</span>
                {textoExtraido && (
                  <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                    {textoExtraido.length} caracteres extraidos
                  </div>
                )}
              </div>
            ) : (
              <div>
                <div style={{ fontSize: '24px', marginBottom: '10px' }}>📄</div>
                <div>Clique para selecionar um PDF</div>
              </div>
            )}
          </div>
        </div>
      )}

      {modoEntrada === 'ID' && (
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
            ID do objeto no MapaGov
          </label>
          <input
            type="text"
            value={origemId}
            onChange={(e) => setOrigemId(e.target.value)}
            placeholder="Ex: 550e8400-e29b-41d4-a716-446655440000"
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              fontSize: '14px',
            }}
          />
        </div>
      )}

      {modoEntrada === 'QUESTIONARIO' && (
        <div style={{ padding: '20px', background: '#f0fdf4', borderRadius: '8px', marginBottom: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '10px' }}>📝</div>
          <div style={{ color: '#166534' }}>
            Voce ira preencher o contexto na proxima etapa.
          </div>
        </div>
      )}

      {erro && (
        <div style={{ padding: '10px', background: '#fee2e2', color: '#dc2626', borderRadius: '4px', marginBottom: '15px' }}>
          {erro}
        </div>
      )}

      {/* Botao iniciar */}
      <div style={{ textAlign: 'right' }}>
        <button
          onClick={handleIniciar}
          disabled={!modoEntrada || loading || extraindo}
          style={{
            padding: '12px 30px',
            background: !modoEntrada || loading || extraindo ? '#9ca3af' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: !modoEntrada || loading || extraindo ? 'not-allowed' : 'pointer',
            fontSize: '16px',
          }}
        >
          {loading ? 'Criando...' : 'Iniciar Analise →'}
        </button>
      </div>
    </div>
  );
};

export default Etapa0Entrada;
