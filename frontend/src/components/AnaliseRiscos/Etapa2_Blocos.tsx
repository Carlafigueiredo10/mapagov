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
    titulo: 'Dependência de Terceiros',
    perguntas: [
      { id: 'Q1', texto: 'O projeto/processo depende de terceiros para sua execução?', opcoes: ['NAO_EXISTE', 'BAIXA', 'MEDIA', 'ALTA'] },
      { id: 'Q2', texto: 'Qual o nível de formalização da relação com terceiros?', opcoes: ['FORMAL', 'PARCIAL', 'INFORMAL'], condicional: { Q1: ['BAIXA', 'MEDIA', 'ALTA'] } },
      { id: 'Q3', texto: 'Qual a natureza da contratação?', opcoes: ['CONTRATO_VIGENTE', 'CONTRATACAO_FUTURA', 'LICITACAO_NAO_REALIZADA', 'NAO_SE_APLICA'], condicional: { Q1: ['BAIXA', 'MEDIA', 'ALTA'] } },
      { id: 'Q4', texto: 'A entrega do terceiro é crítica para o resultado?', opcoes: ['NAO_CRITICA', 'IMPORTANTE', 'CRITICA_PARA_RESULTADO_FINAL'], condicional: { Q1: ['BAIXA', 'MEDIA', 'ALTA'] } },
    ],
  },
  {
    id: 'BLOCO_2',
    titulo: 'Recursos Humanos e Capacidades',
    perguntas: [
      { id: 'Q1', texto: 'A execução depende de pessoas-chave específicas?', opcoes: ['NAO_EXISTE', 'BAIXA', 'MEDIA', 'ALTA'] },
      { id: 'Q2', texto: 'Qual o tempo e custo de substituição dessas pessoas?', opcoes: ['CURTO', 'MEDIO', 'LONGO'], condicional: { Q1: ['BAIXA', 'MEDIA', 'ALTA'] } },
      { id: 'Q3', texto: 'Há risco de afastamento ou rotatividade?', opcoes: ['NAO', 'MODERADO', 'ELEVADO'] },
      { id: 'Q4', texto: 'O nível de capacitação da equipe é:', opcoes: ['ADEQUADO', 'PARCIAL', 'INSUFICIENTE'] },
    ],
  },
  {
    id: 'BLOCO_3',
    titulo: 'Tecnologia e Sistemas',
    perguntas: [
      { id: 'Q1', texto: 'O processo depende de sistemas de TI?', opcoes: ['NAO_DEPENDE', 'DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] },
      { id: 'Q2', texto: 'Os sistemas são internos, externos ou mistos?', opcoes: ['INTERNO', 'EXTERNO', 'MISTO'], condicional: { Q1: ['DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] } },
      { id: 'Q3', texto: 'Qual o estágio de maturidade dos sistemas?', opcoes: ['ESTAVEL_CONSOLIDADO', 'EM_IMPLANTACAO_OU_EVOLUCAO', 'INSTAVEL_OU_CRITICO'], condicional: { Q1: ['DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] } },
      { id: 'Q4', texto: 'O processo pode continuar manualmente se o sistema falhar?', opcoes: ['SIM_PLENA', 'PARCIAL', 'NAO_EXISTE'], condicional: { Q1: ['DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] } },
      { id: 'Q5', texto: 'Há histórico recente de falhas?', opcoes: ['NAO', 'OCASIONAL', 'RECORRENTE'], condicional: { Q1: ['DEPENDE_PARCIALMENTE', 'DEPENDE_CRITICAMENTE'] } },
    ],
  },
  {
    id: 'BLOCO_4',
    titulo: 'Prazos, SLAs e Pressões Legais',
    perguntas: [
      { id: 'Q1', texto: 'Existem prazos legais ou normativos?', opcoes: ['NAO_EXISTEM', 'EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] },
      { id: 'Q2', texto: 'Qual a origem da obrigação de prazo?', opcoes: ['LEGAL', 'REGULAMENTAR', 'CONTRATUAL', 'ADMINISTRATIVA'], condicional: { Q1: ['EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] } },
      { id: 'Q3', texto: 'O que acontece em caso de descumprimento?', opcoes: ['ADMINISTRATIVA', 'FINANCEIRA', 'RESPONSABILIZACAO_AGENTES', 'JUDICIALIZACAO', 'MULTIPLA'], condicional: { Q1: ['EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] } },
      { id: 'Q4', texto: 'Existe margem para renegociação do prazo?', opcoes: ['SIM_CLARA', 'LIMITADA', 'INEXISTENTE'], condicional: { Q1: ['EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] } },
      { id: 'Q5', texto: 'Há pressão externa associada ao prazo?', opcoes: ['NAO', 'ORGAOS_CONTROLE', 'MIDIA_SOCIEDADE', 'PODER_JUDICIARIO'], condicional: { Q1: ['EXISTEM_COM_MARGEM', 'EXISTEM_CRITICOS'] } },
    ],
  },
  {
    id: 'BLOCO_5',
    titulo: 'Governança e Tomada de Decisão',
    perguntas: [
      { id: 'Q1', texto: 'Existe ato formal que define a instância decisória?', opcoes: ['CLARA_E_FORMAL', 'CLARA_MAS_INFORMAL', 'DIFUSA', 'INEXISTENTE'] },
      { id: 'Q2', texto: 'Existe ato formal de governança (portaria, regimento)?', opcoes: ['EXISTE', 'PARCIAL', 'NAO_EXISTE'] },
      { id: 'Q3', texto: 'Há dependência de instâncias externas para decisão?', opcoes: ['NAO', 'UMA_INSTANCIA', 'MULTIPLAS_INSTANCIAS'] },
      { id: 'Q4', texto: 'O fluxo decisório é previsível?', opcoes: ['PREVISIVEL', 'PARCIALMENTE_PREVISIVEL', 'IMPREVISIVEL'] },
      { id: 'Q5', texto: 'Há risco de conflito de competência?', opcoes: ['NAO', 'POSSIVEL', 'PROVAVEL'] },
    ],
  },
  {
    id: 'BLOCO_6',
    titulo: 'Impacto Desigual e Sensibilidade Social',
    perguntas: [
      { id: 'Q1', texto: 'O projeto pode afetar grupos específicos de forma diferenciada?', opcoes: ['NAO', 'POSSIVEL', 'PROVAVEL'] },
      { id: 'Q2', texto: 'Quais grupos podem ser afetados?', opcoes: ['MULHERES', 'PESSOAS_NEGRAS', 'PESSOAS_COM_DEFICIENCIA', 'POPULACOES_VULNERAVEIS', 'TERRITORIOS_ESPECIFICOS', 'OUTROS'], multipla: true, condicional: { Q1: ['POSSIVEL', 'PROVAVEL'] } },
      { id: 'Q3', texto: 'Qual a natureza do impacto?', opcoes: ['ACESSO', 'QUALIDADE_DO_SERVICO', 'TRATAMENTO_DESIGUAL', 'BARREIRA_TECNOLOGICA', 'EXPOSICAO_A_RISCO'], multipla: true, condicional: { Q1: ['POSSIVEL', 'PROVAVEL'] } },
      { id: 'Q4', texto: 'Qual a escala do impacto?', opcoes: ['PONTUAL', 'RECORRENTE', 'SISTEMICO'], condicional: { Q1: ['POSSIVEL', 'PROVAVEL'] } },
      { id: 'Q5', texto: 'Existem medidas mitigadoras previstas?', opcoes: ['NAO_PREVISTAS', 'PREVISTAS_PARCIALMENTE', 'PREVISTAS_E_FORMALIZADAS'], condicional: { Q1: ['POSSIVEL', 'PROVAVEL'] } },
    ],
  },
];

// Mapeamento de valores internos para labels amigáveis em português
const LABELS_OPCOES: Record<string, string> = {
  // Gerais
  NAO: 'Não',
  SIM: 'Sim',
  NAO_EXISTE: 'Não existe',
  NAO_EXISTEM: 'Não existem',
  NAO_SE_APLICA: 'Não se aplica',
  NAO_DEPENDE: 'Não depende',
  NAO_CRITICA: 'Não crítica',
  NAO_PREVISTAS: 'Não previstas',

  // Níveis
  BAIXA: 'Baixa',
  MEDIA: 'Média',
  ALTA: 'Alta',
  MODERADO: 'Moderado',
  ELEVADO: 'Elevado',
  CURTO: 'Curto',
  MEDIO: 'Médio',
  LONGO: 'Longo',
  ADEQUADO: 'Adequado',
  PARCIAL: 'Parcial',
  INSUFICIENTE: 'Insuficiente',
  PONTUAL: 'Pontual',
  RECORRENTE: 'Recorrente',
  SISTEMICO: 'Sistêmico',
  OCASIONAL: 'Ocasional',

  // Formalização
  FORMAL: 'Formal',
  INFORMAL: 'Informal',
  EXISTE: 'Existe',
  INEXISTENTE: 'Inexistente',
  LIMITADA: 'Limitada',

  // Contratação
  CONTRATO_VIGENTE: 'Contrato vigente',
  CONTRATACAO_FUTURA: 'Contratação futura',
  LICITACAO_NAO_REALIZADA: 'Licitação não realizada',

  // Criticidade
  IMPORTANTE: 'Importante',
  CRITICA_PARA_RESULTADO_FINAL: 'Crítica para resultado final',

  // Tecnologia
  DEPENDE_PARCIALMENTE: 'Depende parcialmente',
  DEPENDE_CRITICAMENTE: 'Depende criticamente',
  INTERNO: 'Interno',
  EXTERNO: 'Externo',
  MISTO: 'Misto',
  ESTAVEL_CONSOLIDADO: 'Estável/Consolidado',
  EM_IMPLANTACAO_OU_EVOLUCAO: 'Em implantação ou evolução',
  INSTAVEL_OU_CRITICO: 'Instável ou crítico',
  SIM_PLENA: 'Sim, plenamente',

  // Prazos
  EXISTEM_COM_MARGEM: 'Existem, com margem',
  EXISTEM_CRITICOS: 'Existem, críticos',
  LEGAL: 'Legal',
  REGULAMENTAR: 'Regulamentar',
  CONTRATUAL: 'Contratual',
  ADMINISTRATIVA: 'Administrativa',
  FINANCEIRA: 'Financeira',
  RESPONSABILIZACAO_AGENTES: 'Responsabilização de agentes',
  JUDICIALIZACAO: 'Judicialização',
  MULTIPLA: 'Múltipla',
  SIM_CLARA: 'Sim, clara',
  ORGAOS_CONTROLE: 'Órgãos de controle',
  MIDIA_SOCIEDADE: 'Mídia/Sociedade',
  PODER_JUDICIARIO: 'Poder Judiciário',

  // Governança
  CLARA_E_FORMAL: 'Clara e formal',
  CLARA_MAS_INFORMAL: 'Clara, mas informal',
  DIFUSA: 'Difusa',
  UMA_INSTANCIA: 'Uma instância',
  MULTIPLAS_INSTANCIAS: 'Múltiplas instâncias',
  PREVISIVEL: 'Previsível',
  PARCIALMENTE_PREVISIVEL: 'Parcialmente previsível',
  IMPREVISIVEL: 'Imprevisível',
  POSSIVEL: 'Possível',
  PROVAVEL: 'Provável',

  // Impacto social
  MULHERES: 'Mulheres',
  PESSOAS_NEGRAS: 'Pessoas negras',
  PESSOAS_COM_DEFICIENCIA: 'Pessoas com deficiência',
  POPULACOES_VULNERAVEIS: 'Populações vulneráveis',
  TERRITORIOS_ESPECIFICOS: 'Territórios específicos',
  OUTROS: 'Outros',
  ACESSO: 'Acesso',
  QUALIDADE_DO_SERVICO: 'Qualidade do serviço',
  TRATAMENTO_DESIGUAL: 'Tratamento desigual',
  BARREIRA_TECNOLOGICA: 'Barreira tecnológica',
  EXPOSICAO_A_RISCO: 'Exposição a risco',
  PREVISTAS_PARCIALMENTE: 'Previstas parcialmente',
  PREVISTAS_E_FORMALIZADAS: 'Previstas e formalizadas',
};

// Helper para obter label amigável
const getLabel = (valor: string): string => LABELS_OPCOES[valor] || valor.replace(/_/g, ' ');

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
      <h3 style={{ marginBottom: '8px' }}>Identificação de Riscos</h3>
      <p style={{ color: '#555', marginBottom: '20px', lineHeight: '1.6' }}>
        As respostas às perguntas abaixo subsidiam a identificação dos riscos associados ao objeto da análise.
        Com base nessas informações, o sistema organiza e registra os riscos identificados.
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
                              {getLabel(opcao)}
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
                            {getLabel(opcao)}
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
