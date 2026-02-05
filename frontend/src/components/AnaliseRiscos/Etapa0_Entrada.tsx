/**
 * Etapa0_Entrada - Selecao do tipo de objeto e modo de entrada
 */
import React, { useState, useRef } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import { TIPOS_ORIGEM, TipoOrigem, ModoEntrada } from '../../types/analiseRiscos.types';

interface Props {
  onAvancar: (textoExtraido?: string) => void;
}

// Ícones SVG inline (azul institucional Gov.br)
const IconeFormulario = () => (
  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1351B4" strokeWidth="1.5">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="8" y1="13" x2="16" y2="13" />
    <line x1="8" y1="17" x2="12" y2="17" />
  </svg>
);

const IconeDocumento = () => (
  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1351B4" strokeWidth="1.5">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <path d="M9 15l2 2 4-4" />
  </svg>
);

const IconeRepositorio = () => (
  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1351B4" strokeWidth="1.5">
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
  </svg>
);

const MODOS_ENTRADA = [
  {
    valor: 'QUESTIONARIO' as ModoEntrada,
    label: 'Preenchimento manual',
    descricao: 'Informar o contexto manualmente',
    texto: 'Utilize esta opção quando o objeto ainda estiver em fase inicial ou quando não houver documentação formal consolidada.',
    Icone: IconeFormulario,
  },
  {
    valor: 'PDF' as ModoEntrada,
    label: 'Tenho documento',
    descricao: 'Utilizar documento formal',
    texto: 'Utilize esta opção quando existir documentação formalizada, como termo de abertura, plano, relatório ou outro documento oficial.',
    Icone: IconeDocumento,
  },
  {
    valor: 'ID' as ModoEntrada,
    label: 'Já existe no MapaGov',
    descricao: 'Buscar registro cadastrado',
    texto: 'Utilize esta opção quando o objeto já estiver registrado no MapaGov. As informações existentes serão recuperadas para apoiar a análise.',
    Icone: IconeRepositorio,
  },
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
      setErro('Erro ao criar análise. Tente novamente.');
      return;
    }

    // Avanca somente apos criacao bem-sucedida
    onAvancar(textoExtraido);
  };

  // ETAPA 1: Selecao do tipo de objeto
  if (etapaInterna === 1) {
    return (
      <div>
        <h3 style={{ marginBottom: '8px' }}>Definição do objeto da análise</h3>
        <p style={{ color: '#555', marginBottom: '24px', lineHeight: '1.6' }}>
          Nesta etapa, selecione o tipo de objeto que será avaliado quanto aos riscos.
          O objeto define o contexto da análise e influencia as etapas seguintes.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '32px' }}>
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

        {/* Exemplos de objetos */}
        <div style={{ padding: '20px', background: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1351B4' }}>
          <p style={{ fontWeight: '600', color: '#333', marginBottom: '12px', fontSize: '14px' }}>
            Exemplos de objetos de análise:
          </p>
          <ul style={{ margin: 0, paddingLeft: '20px', color: '#555', fontSize: '14px', lineHeight: '1.8' }}>
            <li><strong>Projeto</strong> – iniciativa temporária, com início e fim definidos, voltada à entrega de um resultado específico.</li>
            <li><strong>Processo</strong> – conjunto de atividades recorrentes realizadas para cumprir uma função institucional.</li>
            <li><strong>POP / Procedimento</strong> – documento que descreve como uma atividade deve ser executada.</li>
            <li><strong>Política</strong> – diretriz institucional que orienta decisões e comportamentos.</li>
            <li><strong>Norma</strong> – instrumento normativo que estabelece regras ou requisitos formais.</li>
            <li><strong>Plano</strong> – instrumento de planejamento que define objetivos, metas e ações.</li>
          </ul>
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

      <h3 style={{ marginBottom: '8px' }}>Como você vai informar sobre o {tipoOrigem?.toLowerCase()}?</h3>
      <p style={{ color: '#555', marginBottom: '24px', lineHeight: '1.6' }}>
        Selecione a forma mais adequada para fornecer as informações que serão utilizadas na análise.
      </p>

      {/* Selecao do modo */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
        {MODOS_ENTRADA.map((modo) => (
          <button
            key={modo.valor}
            onClick={() => handleSelecionarModo(modo.valor)}
            style={{
              flex: 1,
              padding: '20px',
              border: modoEntrada === modo.valor ? '2px solid #1351B4' : '1px solid #ddd',
              borderRadius: '8px',
              background: modoEntrada === modo.valor ? '#E8F0FE' : 'white',
              cursor: 'pointer',
              textAlign: 'center',
            }}
          >
            <div style={{ marginBottom: '12px', textAlign: 'center' }}><modo.Icone /></div>
            <div style={{ fontWeight: '600', marginBottom: '4px', color: '#333', textAlign: 'center' }}>{modo.label}</div>
            <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px', textAlign: 'center' }}>{modo.descricao}</div>
            <div style={{ fontSize: '12px', color: '#555', lineHeight: '1.5', textAlign: 'center' }}>{modo.texto}</div>
          </button>
        ))}
      </div>

      {/* Microcopy de apoio */}
      <p style={{ fontSize: '13px', color: '#666', marginBottom: '24px', fontStyle: 'italic' }}>
        Escolha a opção que melhor representa a situação atual. As informações poderão ser complementadas nas etapas seguintes.
      </p>

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
          {loading ? 'Criando...' : 'Iniciar Análise →'}
        </button>
      </div>
    </div>
  );
};

export default Etapa0Entrada;
