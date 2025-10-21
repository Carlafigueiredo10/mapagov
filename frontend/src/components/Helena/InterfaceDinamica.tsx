// No arquivo: InterfaceDinamica.tsx

import React, { useState } from 'react';

// Importando todos os componentes filhos de seus respectivos arquivos (sem duplicatas)
import AreasSelector from './AreasSelector';
import DropdownArquitetura from './DropdownArquitetura';
import ModalAjudaHelena from './ModalAjudaHelena';
import InterfaceSistemas from './InterfaceSistemas';
import InterfaceNormas from './InterfaceNormas';
import InterfaceDocumentos from './InterfaceDocumentos';
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
import InterfaceSelecaoEdicao from './InterfaceSelecaoEdicao';
import InterfaceEditarEtapas from './InterfaceEditarEtapas';
import InterfaceFinal from './InterfaceFinal';

// TIPOS E INTERFACES GLOBAIS (sem duplicatas)
interface InterfaceData {
  tipo: string;
  dados?: Record<string, unknown> | null;
}

interface InterfaceDinamicaProps {
  interfaceData: InterfaceData | null;
  onRespond: (resposta: string) => void;
}

// COMPONENTE PRINCIPAL (Roteador de Interfaces)
const InterfaceDinamica: React.FC<InterfaceDinamicaProps> = ({ interfaceData, onRespond }) => {
  const [modalAjudaAberto, setModalAjudaAberto] = useState(false);
  const [carregandoAjuda, setCarregandoAjuda] = useState(false);
  const [nivelAtual, setNivelAtual] = useState<'macro' | 'processo' | 'subprocesso' | 'atividade' | 'resultado'>('macro');

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

  const handleConfirm = (resposta: string) => {
    if (!resposta || resposta.trim() === '') {
      console.warn('⚠️ Resposta vazia bloqueada.');
      return;
    }
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
    case 'areas':
      return <AreasSelector data={dados as { opcoes_areas: Record<string, { codigo: string; nome: string }> }} onConfirm={handleConfirm} />;

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

    case 'documentos':
      return <InterfaceDocumentos dados={dados || undefined} onConfirm={handleConfirm} />;

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

    case 'fluxos_entrada':
      return <InterfaceFluxosEntrada dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'fluxos_saida':
      return <InterfaceFluxosSaida dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'revisao':
      return <InterfaceRevisao dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'selecao_edicao':
      return <InterfaceSelecaoEdicao dados={dados || undefined} onConfirm={handleConfirm} />;

    case 'editar_etapas':
      return <InterfaceEditarEtapas dados={dados || undefined} onConfirm={handleConfirm} />;

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
                  onClick={() => handleConfirm('USAR_DROPDOWNS')}
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

    case 'confirmacao_arquitetura': {
      // Interface de confirmação da sugestão Helena
      const sugestao = (dados as { sugestao?: any })?.sugestao;
      const botoes = (dados as { botoes?: string[] })?.botoes || ['✅ Confirmar e Continuar', '✏️ Ajustar Manualmente'];

      if (!sugestao) {
        return null;
      }

      return (
        <div className="interface-container fade-in">
          <div className="confirmacao-arquitetura-container">
            <div className="sugestao-card">
              <div className="sugestao-header">
                <span className="icone-check">✨</span>
                <h3>Sugestão Helena</h3>
              </div>

              <div className="sugestao-detalhes">
                <div className="item">
                  <span className="label">📋 Macroprocesso:</span>
                  <span className="valor">{sugestao.macroprocesso}</span>
                </div>
                <div className="item">
                  <span className="label">📋 Processo:</span>
                  <span className="valor">{sugestao.processo}</span>
                </div>
                <div className="item">
                  <span className="label">📋 Subprocesso:</span>
                  <span className="valor">{sugestao.subprocesso}</span>
                </div>
                <div className="item">
                  <span className="label">📋 Atividade:</span>
                  <span className="valor">{sugestao.atividade}</span>
                </div>
                {sugestao.codigo_sugerido && (
                  <div className="item codigo">
                    <span className="label">🔢 CPF:</span>
                    <span className="valor codigo-valor">{sugestao.codigo_sugerido}</span>
                  </div>
                )}
                {sugestao.resultado_final && (
                  <div className="item">
                    <span className="label">🎯 Resultado Final:</span>
                    <span className="valor">{sugestao.resultado_final}</span>
                  </div>
                )}
                {sugestao.justificativa && (
                  <div className="justificativa">
                    <span className="label">💡 Justificativa:</span>
                    <p>{sugestao.justificativa}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="action-buttons">
              {botoes.map((botao, index) => (
                <button
                  key={index}
                  className={`btn-interface ${index === 0 ? 'btn-success' : 'btn-secondary-outline'}`}
                  onClick={() => {
                    if (index === 0) {
                      // Confirmar - enviar comando de preenchimento
                      const comando = JSON.stringify({
                        acao: 'preencher_arquitetura_completa',
                        sugestao: sugestao
                      });
                      handleConfirm(comando);
                    } else {
                      // Ajustar manualmente - usar dropdowns
                      handleConfirm('USAR_DROPDOWNS');
                    }
                  }}
                >
                  {botao}
                </button>
              ))}
            </div>
          </div>

          <style>{`
            .confirmacao-arquitetura-container {
              width: 100%;
              max-width: 700px;
              margin: 0 auto;
            }

            .sugestao-card {
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              border-radius: 12px;
              padding: 1.5rem;
              color: white;
              box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
              margin-bottom: 1.5rem;
            }

            .sugestao-header {
              display: flex;
              align-items: center;
              gap: 0.75rem;
              margin-bottom: 1.25rem;
              padding-bottom: 1rem;
              border-bottom: 1px solid rgba(255, 255, 255, 0.3);
            }

            .icone-check {
              font-size: 1.75rem;
            }

            .sugestao-header h3 {
              margin: 0;
              font-size: 1.25rem;
              font-weight: 600;
            }

            .sugestao-detalhes {
              display: flex;
              flex-direction: column;
              gap: 0.75rem;
            }

            .item {
              display: flex;
              gap: 0.5rem;
              align-items: baseline;
            }

            .item .label {
              font-weight: 600;
              min-width: 140px;
              opacity: 0.9;
            }

            .item .valor {
              flex: 1;
              font-weight: 400;
            }

            .item.codigo {
              background: rgba(255, 255, 255, 0.15);
              padding: 0.5rem;
              border-radius: 6px;
              margin-top: 0.25rem;
            }

            .codigo-valor {
              font-family: 'Courier New', monospace;
              font-weight: 600;
              font-size: 1.05rem;
            }

            .justificativa {
              margin-top: 1rem;
              padding-top: 1rem;
              border-top: 1px solid rgba(255, 255, 255, 0.3);
            }

            .justificativa .label {
              display: block;
              font-weight: 600;
              margin-bottom: 0.5rem;
            }

            .justificativa p {
              margin: 0;
              line-height: 1.6;
              opacity: 0.95;
            }

            .action-buttons {
              display: flex;
              gap: 1rem;
            }

            .action-buttons button {
              flex: 1;
              padding: 0.875rem 1.5rem;
              border: none;
              border-radius: 8px;
              font-weight: 600;
              cursor: pointer;
              transition: all 0.2s;
              font-size: 1rem;
            }

            .btn-success {
              background: #28a745;
              color: white;
            }

            .btn-success:hover {
              background: #218838;
              transform: translateY(-2px);
              box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
            }
          `}</style>
        </div>
      );
    }

    default:
      return (
        <div className="interface-container fade-in">
          <div className="interface-title">{`⚠️ Interface não implementada para o tipo: ${tipo}`}</div>
        </div>
      );
  }
};

export default InterfaceDinamica;