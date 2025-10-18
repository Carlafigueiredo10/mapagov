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

    case 'final':
      return <InterfaceFinal dados={dados || undefined} onConfirm={handleConfirm} />;

    default:
      return (
        <div className="interface-container fade-in">
          <div className="interface-title">{`⚠️ Interface não implementada para o tipo: ${tipo}`}</div>
        </div>
      );
  }
};

export default InterfaceDinamica;