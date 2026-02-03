/**
 * Etapa2_Blocos - 6 Blocos de identificacao orientada de riscos
 */
import React, { useState, useEffect } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';

interface Props {
  onAvancar: () => void;
  onVoltar: () => void;
}

// Schema simplificado dos blocos (espelha backend)
const BLOCOS = [
  {
    id: 'BLOCO_1',
    titulo: 'Dependencia de Terceiros',
    perguntas: [
      { id: 'Q1', texto: 'O projeto/processo depende de terceiros para sua execucao?', opcoes: ['NAO_EXISTE', 'BAIXA', 'MEDIA', 'ALTA'] },
      { id: 'Q2', texto: 'Qual o nivel de formalizacao da relacao com terceiros?', opcoes: ['FORMAL', 'PARCIAL', 'INFORMAL'], condicional: { Q1: ['BAIXA', 'MEDIA', 'ALTA'] } },
      { id: 'Q3', texto: 'Qual a natureza da contratacao?', opcoes: ['CONTRATO_VIGENTE', 'CONTRATACAO_FUTURA', 'LICITACAO_NAO_REALIZADA', 'NAO_SE_APLICA'], condicional: { Q1: ['BAIXA', 'MEDIA', 'ALTA'] } },
      { id: 'Q4', texto: 'A entrega do terceiro e critica para o resultado?', opcoes: ['NAO_CRITICA', 'IMPORTANTE', 'CRITICA_PARA_RESULTADO_FINAL'], condicional: { Q1: ['BAIXA', 'MEDIA', 'ALTA'] } },
    ],
  },
  {
    id: 'BLOCO_2',
    titulo: 'Recursos Humanos e Capacidades',
    perguntas: [
      { id: 'Q1', texto: 'A execucao depende de pessoas-chave especificas?', opcoes: ['NAO_EXISTE', 'BAIXA', 'MEDIA', 'ALTA'] },
      { id: 'Q2', texto: 'Qual o tempo e custo de substituicao dessas pessoas?', opcoes: ['CURTO', 'MEDIO', 'LONGO'], condicional: { Q1: ['BAIXA', 'MEDIA', 'ALTA'] } },
      { id: 'Q3', texto: 'Ha risco de afastamento ou rotatividade?', opcoes: ['NAO', 'MODERADO', 'ELEVADO'] },
      { id: 'Q4', texto: 'O nivel de capacitacao da equipe e:', opcoes: ['ADEQUADO', 'PARCIAL', 'INSUFICIENTE'] },
    ],
  },
  {
    id: 'BLOCO_3',
    titulo: 'Tecnologia e Sistemas',
    perguntas: [
      { id: 'Q1', texto: 'O processo depende de sistemas de TI?', opcoes: ['NAO_DEPENDE', 'DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] },
      { id: 'Q2', texto: 'Os sistemas sao internos, externos ou mistos?', opcoes: ['INTERNO', 'EXTERNO', 'MISTO'], condicional: { Q1: ['DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] } },
      { id: 'Q3', texto: 'Qual o estagio de maturidade dos sistemas?', opcoes: ['ESTAVEL_CONSOLIDADO', 'EM_IMPLANTACAO_OU_EVOLUCAO', 'INSTAVEL_OU_CRITICO'], condicional: { Q1: ['DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] } },
      { id: 'Q4', texto: 'O processo pode continuar manualmente se sistema falhar?', opcoes: ['SIM_PLENA', 'PARCIAL', 'NAO_EXISTE'], condicional: { Q1: ['DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] } },
      { id: 'Q5', texto: 'Ha historico recente de falhas?', opcoes: ['NAO', 'OCASIONAL', 'RECORRENTE'], condicional: { Q1: ['DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] } },
    ],
  },
  {
    id: 'BLOCO_4',
    titulo: 'Prazos, SLAs e Pressoes Legais',
    perguntas: [
      { id: 'Q1', texto: 'Existem prazos legais ou normativos?', opcoes: ['NAO_EXISTEM', 'EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] },
      { id: 'Q2', texto: 'Qual a origem da obrigacao de prazo?', opcoes: ['LEGAL', 'REGULAMENTAR', 'CONTRATUAL', 'ADMINISTRATIVA'], condicional: { Q1: ['EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] } },
      { id: 'Q3', texto: 'O que acontece em caso de descumprimento?', opcoes: ['ADMINISTRATIVA', 'FINANCEIRA', 'RESPONSABILIZACAO_AGENTES', 'JUDICIALIZACAO', 'MULTIPLA'], condicional: { Q1: ['EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] } },
      { id: 'Q4', texto: 'Existe margem para renegociacao do prazo?', opcoes: ['SIM_CLARA', 'LIMITADA', 'INEXISTENTE'], condicional: { Q1: ['EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] } },
      { id: 'Q5', texto: 'Ha pressao externa associada ao prazo?', opcoes: ['NAO', 'ORGAOS_CONTROLE', 'MIDIA_SOCIEDADE', 'PODER_JUDICIARIO'], condicional: { Q1: ['EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] } },
    ],
  },
  {
    id: 'BLOCO_5',
    titulo: 'Governanca e Tomada de Decisao',
    perguntas: [
      { id: 'Q1', texto: 'Existe ato formal que define a instancia decisoria?', opcoes: ['CLARA_E_FORMAL', 'CLARA_MAS_INFORMAL', 'DIFUSA', 'INEXISTENTE'] },
      { id: 'Q2', texto: 'Existe ato formal de governanca (portaria, regimento)?', opcoes: ['EXISTE', 'PARCIAL', 'NAO_EXISTE'] },
      { id: 'Q3', texto: 'Ha dependencia de instancias externas para decisao?', opcoes: ['NAO', 'UMA_INSTANCIA', 'MULTIPLAS_INSTANCIAS'] },
      { id: 'Q4', texto: 'O fluxo decisorio e previsivel?', opcoes: ['PREVISIVEL', 'PARCIALMENTE_PREVISIVEL', 'IMPREVISIVEL'] },
      { id: 'Q5', texto: 'Ha risco de conflito de competencia?', opcoes: ['NAO', 'POSSIVEL', 'PROVAVEL'] },
    ],
  },
  {
    id: 'BLOCO_6',
    titulo: 'Impacto Desigual e Sensibilidade Social',
    perguntas: [
      { id: 'Q1', texto: 'O projeto pode afetar grupos especificos de forma diferenciada?', opcoes: ['NAO', 'POSSIVEL', 'PROVAVEL'] },
      { id: 'Q2', texto: 'Quais grupos podem ser afetados?', opcoes: ['MULHERES', 'PESSOAS_NEGRAS', 'PESSOAS_COM_DEFICIENCIA', 'POPULACOES_VULNERAVEIS', 'TERRITORIOS_ESPECIFICOS', 'OUTROS'], multipla: true, condicional: { Q1: ['POSSIVEL', 'PROVAVEL'] } },
      { id: 'Q3', texto: 'Qual a natureza do impacto?', opcoes: ['ACESSO', 'QUALIDADE_DO_SERVICO', 'TRATAMENTO_DESIGUAL', 'BARREIRA_TECNOLOGICA', 'EXPOSICAO_A_RISCO'], multipla: true, condicional: { Q1: ['POSSIVEL', 'PROVAVEL'] } },
      { id: 'Q4', texto: 'Qual a escala do impacto?', opcoes: ['PONTUAL', 'RECORRENTE', 'SISTEMICO'], condicional: { Q1: ['POSSIVEL', 'PROVAVEL'] } },
      { id: 'Q5', texto: 'Existem medidas mitigadoras previstas?', opcoes: ['NAO_PREVISTAS', 'PREVISTAS_PARCIALMENTE', 'PREVISTAS_E_FORMALIZADAS'], condicional: { Q1: ['POSSIVEL', 'PROVAVEL'] } },
    ],
  },
];

const Etapa2Blocos: React.FC<Props> = ({ onAvancar, onVoltar }) => {
  const { currentAnalise, salvarBlocos, inferirRiscos, loading, error } = useAnaliseRiscosStore();

  const [respostas, setRespostas] = useState<Record<string, Record<string, string | string[]>>>({});
  const [blocoAberto, setBlocoAberto] = useState<string | null>('BLOCO_1');

  // Carregar respostas existentes
  useEffect(() => {
    if (currentAnalise?.respostas_blocos) {
      setRespostas(currentAnalise.respostas_blocos);
    }
  }, [currentAnalise]);

  const setResposta = (blocoId: string, perguntaId: string, valor: string | string[]) => {
    setRespostas((prev) => ({
      ...prev,
      [blocoId]: {
        ...prev[blocoId],
        [perguntaId]: valor,
      },
    }));
  };

  const deveExibir = (bloco: typeof BLOCOS[0], pergunta: typeof BLOCOS[0]['perguntas'][0]) => {
    if (!pergunta.condicional) return true;
    const respostasBloco = respostas[bloco.id] || {};
    for (const [refPergunta, valoresAtivadores] of Object.entries(pergunta.condicional)) {
      const respostaRef = respostasBloco[refPergunta];
      if (!respostaRef || !valoresAtivadores.includes(respostaRef as string)) {
        return false;
      }
    }
    return true;
  };

  const handleAvancar = async () => {
    // Verificar se respondeu ao menos Q1 de cada bloco
    for (const bloco of BLOCOS) {
      if (!respostas[bloco.id]?.Q1) {
        alert(`Responda ao menos a primeira pergunta do bloco "${bloco.titulo}"`);
        setBlocoAberto(bloco.id);
        return;
      }
    }

    const sucesso = await salvarBlocos(respostas);
    if (sucesso) {
      // Inferir riscos automaticamente
      const riscosInferidos = await inferirRiscos();
      if (riscosInferidos > 0) {
        alert(`${riscosInferidos} risco(s) identificado(s) automaticamente!`);
      }
      onAvancar();
    }
  };

  return (
    <div>
      <h3>Identificacao de Riscos</h3>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Responda as perguntas abaixo. O sistema identificara riscos automaticamente.
      </p>

      {BLOCOS.map((bloco) => (
        <div
          key={bloco.id}
          style={{
            marginBottom: '15px',
            border: '1px solid #ddd',
            borderRadius: '8px',
            overflow: 'hidden',
          }}
        >
          {/* Header do bloco */}
          <button
            onClick={() => setBlocoAberto(blocoAberto === bloco.id ? null : bloco.id)}
            style={{
              width: '100%',
              padding: '15px',
              background: blocoAberto === bloco.id ? '#3b82f6' : '#f9fafb',
              color: blocoAberto === bloco.id ? 'white' : '#333',
              border: 'none',
              textAlign: 'left',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <span>{bloco.titulo}</span>
            <span>{blocoAberto === bloco.id ? '▼' : '▶'}</span>
          </button>

          {/* Conteudo do bloco */}
          {blocoAberto === bloco.id && (
            <div style={{ padding: '15px', background: 'white' }}>
              {bloco.perguntas.map((pergunta) => {
                if (!deveExibir(bloco, pergunta)) return null;
                const respostaAtual = respostas[bloco.id]?.[pergunta.id];

                return (
                  <div key={pergunta.id} style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                      {pergunta.texto}
                    </label>
                    {pergunta.multipla ? (
                      // Multipla escolha (checkboxes)
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                        {pergunta.opcoes.map((opcao) => {
                          const selecionadas = Array.isArray(respostaAtual) ? respostaAtual : [];
                          const checked = selecionadas.includes(opcao);
                          return (
                            <label key={opcao} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={() => {
                                  const novas = checked
                                    ? selecionadas.filter((v) => v !== opcao)
                                    : [...selecionadas, opcao];
                                  setResposta(bloco.id, pergunta.id, novas);
                                }}
                              />
                              {opcao.replace(/_/g, ' ')}
                            </label>
                          );
                        })}
                      </div>
                    ) : (
                      // Escolha unica (radio buttons em grid)
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                        {pergunta.opcoes.map((opcao) => (
                          <button
                            key={opcao}
                            onClick={() => setResposta(bloco.id, pergunta.id, opcao)}
                            style={{
                              padding: '8px 12px',
                              border: respostaAtual === opcao ? '2px solid #3b82f6' : '1px solid #ddd',
                              borderRadius: '4px',
                              background: respostaAtual === opcao ? '#eff6ff' : 'white',
                              cursor: 'pointer',
                              fontSize: '14px',
                            }}
                          >
                            {opcao.replace(/_/g, ' ')}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ))}

      {error && (
        <div style={{ padding: '10px', background: '#fee2e2', color: '#dc2626', borderRadius: '4px', marginBottom: '15px' }}>
          {error.erro}
        </div>
      )}

      {/* Navegacao */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
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
            background: loading ? '#9ca3af' : '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Processando...' : 'Identificar Riscos →'}
        </button>
      </div>
    </div>
  );
};

export default Etapa2Blocos;
