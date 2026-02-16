// No arquivo: InterfaceDinamica.tsx

import React, { useState, useEffect } from 'react';
import { useChatStore } from '../../store/chatStore';

// Importando todos os componentes filhos de seus respectivos arquivos (sem duplicatas)
import AreasSelector from './AreasSelector';
import SubareasSelector from './SubareasSelector';
import DropdownArquitetura from './DropdownArquitetura';
import ModalAjudaHelena from './ModalAjudaHelena';
import InterfaceSistemas from './InterfaceSistemas';
import InterfaceNormas from './InterfaceNormas';
import InterfaceDocumentos from './InterfaceDocumentos';
import InterfaceEntradaProcesso from './InterfaceEntradaProcesso';
import BadgeTrofeu from './BadgeTrofeu';
import RoadTrip from './RoadTrip';
import InterfaceOperadores from './InterfaceOperadores';
import InterfaceOperadoresEtapa from './InterfaceOperadoresEtapa';
import InterfaceCondicionais from './InterfaceCondicionais';
import InterfaceCondicionaisAjuda from './InterfaceCondicionaisAjuda';
import InterfaceTipoCondicional from './InterfaceTipoCondicional';
import InterfaceValidacaoDocumentos from './InterfaceValidacaoDocumentos';
import InterfaceCenariosBinario from './InterfaceCenariosBinario';
import InterfaceCenariosMultiplosQuantidade from './InterfaceCenariosMultiplosQuantidade';
import InterfaceSubetapasCenario from './InterfaceSubetapasCenario';
import InterfaceEtapasTempoReal from './InterfaceEtapasTempoReal';
import InterfaceFluxosEntrada from './InterfaceFluxosEntrada';
import InterfaceFluxosSaida from './InterfaceFluxosSaida';
import InterfaceRevisao from './InterfaceRevisao';
import InterfaceEditarEtapas from './InterfaceEditarEtapas';
import InterfaceDocumentosEtapa from './InterfaceDocumentosEtapa';
import InterfaceEtapaForm from './InterfaceEtapaForm';
import InterfaceConfirmacaoArquitetura from './InterfaceConfirmacaoArquitetura';
import InterfaceCaixinhaReconhecimento from './InterfaceCaixinhaReconhecimento';
import InterfaceFinal from './InterfaceFinal';
import InterfaceTransicaoEpica from './InterfaceTransicaoEpica';
import InterfaceConfirmacaoDupla from './InterfaceConfirmacaoDupla';
import InterfaceArquiteturaHierarquica from './InterfaceArquiteturaHierarquica';
import BadgeCompromisso from './BadgeCompromisso';
import InterfaceSugestaoAtividade from './InterfaceSugestaoAtividade';
import InterfaceSelecaoManualHierarquica from './InterfaceSelecaoManualHierarquica';
import InterfaceRagPerguntaAtividade from './InterfaceRagPerguntaAtividade';
import InterfaceSugestaoEntregaEsperada from './InterfaceSugestaoEntregaEsperada';
import TransitionLoadingState from './TransitionLoadingState';
import LoadingAnaliseAtividade from './LoadingAnaliseAtividade';
import InterfaceFallback from './InterfaceFallback';
import InterfaceRevisaoFinal from './InterfaceRevisaoFinal';
import { validateInterfaceData } from '../../schemas/validate';

// TIPOS E INTERFACES GLOBAIS (sem duplicatas)
interface InterfaceData {
  tipo: string;
  dados?: Record<string, unknown> | null;
  schema_version?: string;
}

interface InterfaceDinamicaProps {
  interfaceData: InterfaceData | null;
  onRespond: (resposta: string) => void;
}

// Wrapper que ativa fullscreen no chat enquanto o componente estiver montado
const FullscreenChat: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const setFullscreenChat = useChatStore((s) => s.setFullscreenChat);
  useEffect(() => {
    setFullscreenChat(true);
    return () => setFullscreenChat(false);
  }, [setFullscreenChat]);
  return <>{children}</>;
};

// COMPONENTE PRINCIPAL (Roteador de Interfaces)
const InterfaceDinamica: React.FC<InterfaceDinamicaProps> = ({ interfaceData, onRespond }) => {
  const [modalAjudaAberto, setModalAjudaAberto] = useState(false);
  const [carregandoAjuda, setCarregandoAjuda] = useState(false);
  const [nivelAtual, setNivelAtual] = useState<'macro' | 'processo' | 'subprocesso' | 'atividade' | 'resultado'>('macro');

  // 🔒 PATCH 2: Salvaguarda contra interfaces vazias/incompletas
  if (!interfaceData || typeof interfaceData !== "object" || !interfaceData.tipo) {
    console.debug("⏸️ Ignorando interface incompleta:", interfaceData);
    return null;
  }

  // Versioning: detectar schemas desconhecidos (ADR-001 §2.10)
  const SUPPORTED_VERSIONS = ['1.0', '0.0'];
  if (interfaceData.schema_version && !SUPPORTED_VERSIONS.includes(interfaceData.schema_version)) {
    console.warn(`[InterfaceDinamica] Versão desconhecida: ${interfaceData.schema_version}`);
  }

  // ✅ Seu console.log está aqui, no lugar certo!
  console.log("PROPS RECEBIDAS PELA INTERFACE DINÂMICA:", interfaceData);

  // Bloco de verificação (sem duplicatas)
  if (!interfaceData) {
    return (
      <div className="interface-container fade-in">
        <div className="interface-title">Aguardando...</div>
      </div>
    );
  }

  const { tipo, dados } = interfaceData;

  if (!tipo) {
    console.error('❌ InterfaceDinamica: a propriedade "tipo" é ausente.', interfaceData);
    return (
      <div className="interface-container fade-in">
        <div className="interface-title">⚠️ Erro: Tipo de Interface Desconhecido</div>
      </div>
    );
  }

  // Validação de schema: fallback UI se dados inválidos
  const validation = validateInterfaceData(tipo, dados as Record<string, unknown> | null);
  if (!validation.valid) {
    return <InterfaceFallback tipo={tipo} errors={validation.errors} schemaVersion={interfaceData.schema_version} />;
  }

  const handleConfirm = (resposta: string) => {
    console.log('🟢 InterfaceDinamica.handleConfirm recebeu:', resposta);
    console.log('🟢 Tipo:', typeof resposta);
    console.log('🟢 Tamanho:', resposta?.length);

    if (!resposta || resposta.trim() === '') {
      console.warn('⚠️ Resposta vazia bloqueada.');
      return;
    }

    console.log('🟢 Chamando onRespond com:', resposta);
    onRespond(resposta);
  };

  const handlePedirAjuda = () => {
    // Detectar nível baseado no tipo de interface
    let nivel: 'macro' | 'processo' | 'subprocesso' | 'atividade' | 'resultado' = 'macro';
    if (tipo.includes('processo')) nivel = 'processo';
    else if (tipo.includes('subprocesso')) nivel = 'subprocesso';
    else if (tipo.includes('atividade')) nivel = 'atividade';

    setNivelAtual(nivel);
    setModalAjudaAberto(true);
  };

  const handleEnviarDescricao = async (descricao: string) => {
    setCarregandoAjuda(true);

    try {
      // TODO: Extrair contexto do chatStore
      const contexto = {}; // Por enquanto vazio

      const response = await fetch('http://localhost:8000/api/helena-ajuda-arquitetura/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          descricao,
          nivel_atual: nivelAtual,
          contexto,
          session_id: localStorage.getItem('session_id') || 'default'
        })
      });

      const resultado = await response.json();

      if (resultado.success) {
        // Fechar modal
        setModalAjudaAberto(false);

        // Montar mensagem de confirmação formatada
        const sugestaoTexto = `Helena sugeriu:

📍 Macroprocesso: ${resultado.sugestao.macroprocesso}
📍 Processo: ${resultado.sugestao.processo}
📍 Subprocesso: ${resultado.sugestao.subprocesso}
📍 Atividade: ${resultado.sugestao.atividade}
📍 Resultado Final: ${resultado.sugestao.resultado_final}

💡 Justificativa: ${resultado.justificativa}

Se você concorda com minhas sugestões, me dê o OK que preencho todos os campos até o resultado final da atividade.`;

        const confirmacao = window.confirm(sugestaoTexto + "\n\n✅ Confirmar e preencher todos os campos?");

        if (confirmacao) {
          // Enviar comando especial para preencher TODOS os campos
          const comandoPreenchimento = JSON.stringify({
            acao: 'preencher_arquitetura_completa',
            sugestao: resultado.sugestao
          });
          onRespond(comandoPreenchimento);
        }
      } else {
        alert('Erro ao analisar: ' + resultado.erro);
      }
    } catch (erro) {
      console.error('Erro ao chamar Helena:', erro);
      alert('Erro ao conectar com Helena. Tente novamente.');
    } finally {
      setCarregandoAjuda(false);
    }
  };

  switch (tipo) {
    case 'badge_compromisso':
      return (
        <BadgeCompromisso
          nomeCompromisso={dados?.nome_compromisso as string}
          emoji={dados?.emoji as string}
          descricao={dados?.descricao as string}
          onContinuar={() => handleConfirm('sim')}
        />
      );

    case 'loading_analise_atividade':
    case 'explicacao_classificacao':
      return (
        <LoadingAnaliseAtividade
          onEntendi={() => useChatStore.getState().sinalizarEntendi()}
        />
      );

    case 'sugestao_atividade': {
      const origem = dados?.origem as 'match_exato' | 'match_fuzzy' | 'semantic' | 'rag_nova_atividade';
      return (
        <InterfaceSugestaoAtividade
          atividade={dados?.atividade as any}
          cap={dados?.cap as string}
          origem={origem}
          score={dados?.score as number}
          podeEditar={dados?.pode_editar as boolean}
          onConcordar={() => handleConfirm('concordar')}
          onSelecionarManual={() => handleConfirm(origem === 'rag_nova_atividade' ? 'prefiro_digitar' : 'selecionar_manual')}
        />
      );
    }

    case 'selecao_manual_hierarquica':
      return (
        <InterfaceSelecaoManualHierarquica
          hierarquia={dados?.hierarquia as any}
          mensagem={dados?.mensagem as string}
          onConfirmar={(selecao) => handleConfirm(JSON.stringify({ acao: 'confirmar', selecao }))}
          onNaoEncontrei={(selecao) => handleConfirm(JSON.stringify({ acao: 'nao_encontrei', selecao }))}
        />
      );

    case 'rag_pergunta_atividade':
      return (
        <InterfaceRagPerguntaAtividade
          hierarquiaHerdada={dados?.hierarquia_herdada as any}
          onEnviar={(descricao) => handleConfirm(JSON.stringify({ acao: 'enviar_descricao', descricao }))}
        />
      );

    case 'transition_loading':
      return (
        <TransitionLoadingState
          title={(dados?.title as string) || 'Processando...'}
          subtitle={(dados?.subtitle as string) || 'Aguarde um momento.'}
          skeleton={(dados?.skeleton as 'sugestao_entrega' | 'lista' | 'card') || 'card'}
        />
      );

    case 'sugestao_entrega_esperada':
      return (
        <InterfaceSugestaoEntregaEsperada
          sugestao={dados?.sugestao as string}
          onConcordar={() => handleConfirm('concordar')}
          onEditarManual={() => handleConfirm('editar_manual')}
        />
      );

    case 'areas':
      // ✅ Usa validation.data (normalizado pelo z.preprocess: Array→Record)
      return <AreasSelector data={validation.data as { opcoes_areas: Record<string, { codigo: string; nome: string }> }} onConfirm={handleConfirm} />;

    case 'subareas':
      return <SubareasSelector
        data={dados as {
          area_pai: { codigo: string; nome: string };
          subareas: Array<{ codigo: string; nome: string; nome_completo: string; prefixo: string }>
        }}
        onConfirm={handleConfirm}
      />;

    case 'dropdown_macro':
    case 'dropdown_processo':
    case 'dropdown_subprocesso':
    case 'dropdown_atividade':
    case 'dropdown_processo_com_texto_livre':
    case 'dropdown_subprocesso_com_texto_livre':
    case 'dropdown_atividade_com_texto_livre':
      return (
        <>
          <DropdownArquitetura
            tipo={tipo}
            dados={{ ...(dados || {}), onPedirAjuda: handlePedirAjuda }}
            onConfirm={handleConfirm}
          />
          {modalAjudaAberto && (
            <ModalAjudaHelena
              nivelAtual={nivelAtual}
              contextoJaSelecionado={{}}
              onFechar={() => setModalAjudaAberto(false)}
              onEnviar={handleEnviarDescricao}
              carregando={carregandoAjuda}
            />
          )}
        </>
      );

    case 'texto_livre': {
      // Interface sem caixa de texto - usuário digita no chat normal
      const placeholder = (dados as { placeholder?: string })?.placeholder || 'Digite sua resposta...';

      return (
        <div className="interface-container fade-in" style={{ width: '100%' }}>
          <div style={{
            padding: '1rem',
            background: '#f8f9fa',
            borderRadius: '8px',
            borderLeft: '4px solid #1351B4',
            marginBottom: '1rem'
          }}>
            <p style={{ margin: 0, color: '#495057', fontSize: '0.95rem' }}>
              💬 <strong>Digite sua resposta na barra de chat abaixo</strong>
            </p>
            <p style={{ margin: '0.5rem 0 0 0', color: '#6c757d', fontSize: '0.85rem', fontStyle: 'italic' }}>
              Exemplo: {placeholder}
            </p>
          </div>
        </div>
      );
    }

    case 'texto_com_exemplos': {
      // Interface só com botão "Ver exemplos" - usuário digita no chat normal
      const exemplos = (dados as { exemplos?: string[] })?.exemplos || [];
      const [mostrarExemplos, setMostrarExemplos] = React.useState(false);

      return (
        <div className="interface-container fade-in" style={{ width: '100%' }}>
          {exemplos.length > 0 && (
            <button
              className="btn-ver-exemplos"
              onClick={() => setMostrarExemplos(!mostrarExemplos)}
              type="button"
              style={{
                marginBottom: '1rem',
                padding: '0.5rem 1rem',
                background: 'transparent',
                color: '#1351B4',
                border: '1px solid #1351B4',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '500',
                textAlign: 'center',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%'
              }}
            >
              💡 {mostrarExemplos ? 'Ocultar exemplos' : 'Eu separei uns exemplos pra te ajudar, se quiser ver clique aqui.'}
            </button>
          )}

          {mostrarExemplos && exemplos.length > 0 && (
            <div
              className="exemplos-container"
              style={{
                marginBottom: '1rem',
                padding: '1rem',
                background: '#f8f9fa',
                borderRadius: '8px',
                border: '2px solid #1351B4',
                animation: 'fadeIn 0.3s ease-in'
              }}
            >
              <div style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#1351B4' }}>
                💡 Exemplos:
              </div>
              {exemplos.map((exemplo, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '0.75rem',
                    background: 'white',
                    borderRadius: '6px',
                    marginBottom: '0.5rem',
                    fontSize: '0.9rem',
                    lineHeight: '1.5'
                  }}
                >
                  • {exemplo}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    case 'texto': {
      // Detectar se tem sugestão de IA para resultado final
      const sugestaoIA = (dados as { sugestao_ia?: string })?.sugestao_ia;
      const contexto = (dados as { contexto?: string })?.contexto;

      if (sugestaoIA && contexto === 'resultado_final') {
        // Interface especial com sugestão de IA
        return (
          <div className="interface-container fade-in">
            <div className="interface-title">🎯 Resultado Final da Atividade</div>

            <div className="sugestao-ia-section">
              <div className="sugestao-header">
                <span className="icone-ia">🧠</span>
                <h3>Com base no que você descreveu até agora, minha sugestão de resultado final é:</h3>
              </div>
              <div className="sugestao-conteudo">
                👉 "{sugestaoIA}"
              </div>
              <p className="sugestao-info">
                Você pode usar essa sugestão se ela fizer sentido — ou ajustar manualmente para refletir melhor o que é entregue no seu trabalho.
              </p>
            </div>

            <div className="action-buttons">
              <button
                className="btn-interface btn-success"
                onClick={() => handleConfirm(sugestaoIA)}
              >
                ✓ Usar esta sugestão
              </button>
              <button
                className="btn-interface btn-secondary"
                onClick={() => {
                  const customResposta = prompt('Digite o resultado final da atividade:', sugestaoIA);
                  if (customResposta && customResposta.trim()) {
                    handleConfirm(customResposta.trim());
                  }
                }}
              >
                ✏️ Editar manualmente
              </button>
            </div>

            <style>{`
              .sugestao-ia-section {
                margin: 1.5rem 0;
                padding: 1.5rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                color: white;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
              }

              .sugestao-header {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1rem;
              }

              .icone-ia {
                font-size: 1.5rem;
              }

              .sugestao-header h3 {
                margin: 0;
                font-size: 1.1rem;
                font-weight: 600;
              }

              .sugestao-conteudo {
                background: rgba(255, 255, 255, 0.2);
                padding: 1rem;
                border-radius: 8px;
                font-size: 1.05rem;
                line-height: 1.6;
                border-left: 4px solid rgba(255, 255, 255, 0.5);
              }

              .sugestao-info {
                margin-top: 1rem;
                font-size: 0.85rem;
                opacity: 0.9;
                margin-bottom: 0;
              }

              .btn-success {
                background: #28a745;
                color: white;
              }

              .btn-success:hover {
                background: #218838;
              }
            `}</style>
          </div>
        );
      }

      // Verificar se há botões para renderizar
      const botoes = (dados as { botoes?: string[] })?.botoes;

      if (botoes && Array.isArray(botoes) && botoes.length > 0) {
        // Renderizar botões
        return (
          <div className="interface-container fade-in">
            <div className="action-buttons" style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              {botoes.map((botao, index) => (
                <button
                  key={index}
                  className={`btn-interface ${index === 0 ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => handleConfirm(botao)}
                  style={{
                    flex: 1,
                    padding: '0.75rem 1.5rem',
                    border: 'none',
                    borderRadius: '6px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    background: index === 0 ? '#007bff' : '#6c757d',
                    color: 'white'
                  }}
                >
                  {botao}
                </button>
              ))}
            </div>
          </div>
        );
      }

      // Mensagens de texto sem botões: não renderizar (já estão na mensagem da Helena)
      return null;
    }

    case 'sistemas':
      return <InterfaceSistemas dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'normas':
      return <InterfaceNormas dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'roadtrip':
      return <RoadTrip onContinue={() => handleConfirm('continuar')} />;

    case 'badge_sistemas':
      return (
        <BadgeTrofeu
          nomeBadge={dados?.nome_badge as string}
          onContinuar={() => handleConfirm('continuar')}
        />
      );

    case 'badge_cartografo':
      return (
        <BadgeTrofeu
          nomeBadge={dados?.titulo as string || "Cartógrafo de Processos"}
          emoji={dados?.emoji as string || "🗺️"}
          descricao={dados?.descricao as string}
          onContinuar={() => handleConfirm('continuar')}
        />
      );

    case 'documentos':
      return <InterfaceDocumentos dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'entrada_processo':
      return <InterfaceEntradaProcesso dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'fluxos_entrada':
      return <InterfaceFluxosEntrada dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'operadores':
      return <InterfaceOperadores dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'operadores_etapa':
      return <InterfaceOperadoresEtapa dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'condicionais':
    case 'condicionais_etapa':
      return <InterfaceCondicionais dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'condicionais_ajuda':
      return <InterfaceCondicionaisAjuda dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'tipo_condicional':
      return <InterfaceTipoCondicional dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'validacao_documentos':
      return <InterfaceValidacaoDocumentos dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'cenarios_binario':
      return <InterfaceCenariosBinario dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'cenarios_multiplos_quantidade':
      return <InterfaceCenariosMultiplosQuantidade dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'subetapas_cenario':
      return <InterfaceSubetapasCenario dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'etapas_tempo_real':
      return <InterfaceEtapasTempoReal dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'fluxos_saida':
      return <InterfaceFluxosSaida dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'revisao':
      return <InterfaceRevisao dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'revisao_final':
      return <FullscreenChat><InterfaceRevisaoFinal dados={dados || undefined} onConfirm={handleConfirm} /></FullscreenChat>;

    case 'editar_etapas':
      return <FullscreenChat><InterfaceEditarEtapas dados={dados || undefined} onConfirm={handleConfirm} /></FullscreenChat>;

    case 'docs_requeridos_etapa':
    case 'docs_gerados_etapa':
      return <InterfaceDocumentosEtapa dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'etapa_form':
      return <InterfaceEtapaForm dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'final':
      return <InterfaceFinal dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'texto_com_alternativa': {
      // Interface híbrida: texto livre COM botão para dropdowns
      const placeholder = (dados as { placeholder?: string })?.placeholder || 'Digite sua resposta...';
      const hint = (dados as { hint?: string })?.hint;
      const botaoAlternativo = (dados as { botao_alternativo?: { label: string; acao: string } })?.botao_alternativo;

      return (
        <div className="interface-container fade-in">
          <div className="texto-com-alternativa-container">
            {/* Campo de texto livre */}
            <div className="input-group">
              <input
                type="text"
                className="form-control"
                placeholder={placeholder}
                id="input-texto-livre"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    const valor = (e.target as HTMLInputElement).value.trim();
                    if (valor) {
                      handleConfirm(valor);
                    }
                  }
                }}
              />
              <button
                className="btn-interface btn-primary"
                onClick={() => {
                  const input = document.getElementById('input-texto-livre') as HTMLInputElement;
                  const valor = input?.value.trim();
                  if (valor) {
                    handleConfirm(valor);
                  }
                }}
              >
                Enviar
              </button>
            </div>

            {hint && (
              <div className="hint-text">
                {hint}
              </div>
            )}

            {/* Botão alternativo (navegar manualmente) */}
            {botaoAlternativo && (
              <div className="alternativa-section">
                <div className="divider">
                  <span>OU</span>
                </div>
                <button
                  className="btn-interface btn-secondary-outline"
                  onClick={() => handleConfirm(botaoAlternativo.acao)}
                >
                  {botaoAlternativo.label}
                </button>
              </div>
            )}
          </div>

          <style>{`
            .texto-com-alternativa-container {
              width: 100%;
              max-width: 600px;
              margin: 0 auto;
            }

            .input-group {
              display: flex;
              gap: 0.5rem;
              margin-bottom: 1rem;
            }

            .form-control {
              flex: 1;
              padding: 0.75rem 1rem;
              border: 2px solid #e0e0e0;
              border-radius: 8px;
              font-size: 1rem;
              transition: border-color 0.2s;
            }

            .form-control:focus {
              outline: none;
              border-color: #007bff;
            }

            .btn-primary {
              background: #007bff;
              color: white;
              padding: 0.75rem 1.5rem;
              border: none;
              border-radius: 8px;
              font-weight: 500;
              cursor: pointer;
              transition: background 0.2s;
            }

            .btn-primary:hover {
              background: #0056b3;
            }

            .hint-text {
              font-size: 0.9rem;
              color: #666;
              margin-bottom: 1.5rem;
              padding: 0.5rem;
              background: #f8f9fa;
              border-radius: 6px;
              border-left: 3px solid #007bff;
            }

            .alternativa-section {
              margin-top: 2rem;
            }

            .divider {
              text-align: center;
              position: relative;
              margin: 1.5rem 0;
            }

            .divider span {
              background: white;
              padding: 0 1rem;
              color: #999;
              font-weight: 500;
              font-size: 0.9rem;
              position: relative;
              z-index: 1;
            }

            .divider::before {
              content: '';
              position: absolute;
              top: 50%;
              left: 0;
              right: 0;
              height: 1px;
              background: #e0e0e0;
              z-index: 0;
            }

            .btn-secondary-outline {
              width: 100%;
              padding: 0.75rem 1.5rem;
              border: 2px solid #6c757d;
              background: white;
              color: #6c757d;
              border-radius: 8px;
              font-weight: 500;
              cursor: pointer;
              transition: all 0.2s;
            }

            .btn-secondary-outline:hover {
              background: #6c757d;
              color: white;
            }
          `}</style>
        </div>
      );
    }

    case 'confirmacao_arquitetura':
      return <InterfaceConfirmacaoArquitetura dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'caixinha_reconhecimento':
      return <InterfaceCaixinhaReconhecimento dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'transicao_epica':
      return <InterfaceTransicaoEpica dados={dados as any || {}} onEnviar={handleConfirm} />;

    case 'confirmacao_dupla':
      return <InterfaceConfirmacaoDupla dados={dados || {}} onEnviar={handleConfirm} />;

    case 'confirmacao_explicacao':
      return <InterfaceConfirmacaoDupla dados={{
        botao_confirmar: 'Continuar',
        botao_editar: 'Ver detalhes do mapeamento',
        valor_confirmar: 'sim',
        valor_editar: 'detalhes'
      }} onEnviar={handleConfirm} />;

    case 'arquitetura_hierarquica':
      return <InterfaceArquiteturaHierarquica dados={dados || {}} onEnviar={handleConfirm} />;

    default:
      return (
        <div className="interface-container fade-in">
          <div className="interface-title">{`⚠️ Interface não implementada para o tipo: ${tipo}`}</div>
        </div>
      );
  }
};

export default InterfaceDinamica;