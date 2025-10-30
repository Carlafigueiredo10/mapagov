/**
 * Painel de Desenvolvedor - Visualiza TODAS as funcionalidades do backend
 *
 * Mostra:
 * - Todos os 21 estados da máquina
 * - Todas as interfaces dinâmicas disponíveis
 * - Todos os handlers implementados
 * - Estado atual completo (session_data)
 * - Formulário POP em tempo real
 * - Metadados e badges
 * - Progresso detalhado
 * - Logs de requisições
 */

import React, { useState, useEffect } from 'react';
import { useChatStore } from '../../store/chatStore';
import './PainelDesenvolvedor.css';

interface PainelDesenvolvedorProps {
  isOpen: boolean;
  onClose: () => void;
}

const PainelDesenvolvedor: React.FC<PainelDesenvolvedorProps> = ({ isOpen, onClose }) => {
  const { dadosPOP, messages } = useChatStore();
  const [abaAtiva, setAbaAtiva] = useState<string>('estados');
  const [filtro, setFiltro] = useState<string>('');

  // Todos os 21 estados da máquina
  const TODOS_ESTADOS = [
    { id: 'nome_usuario', nome: 'NOME_USUARIO', ordem: 1, descricao: 'Coleta do primeiro nome do usuário' },
    { id: 'confirma_nome', nome: 'CONFIRMA_NOME', ordem: 2, descricao: 'Confirmação do nome fornecido' },
    { id: 'escolha_tipo_explicacao', nome: 'ESCOLHA_TIPO_EXPLICACAO', ordem: 3, descricao: 'Escolher explicação curta ou longa' },
    { id: 'explicacao_longa', nome: 'EXPLICACAO_LONGA', ordem: 4, descricao: 'Explicação detalhada do processo' },
    { id: 'pedido_compromisso', nome: 'PEDIDO_COMPROMISSO', ordem: 5, descricao: 'Pedido de compromisso de documentação' },
    { id: 'area_decipex', nome: 'AREA_DECIPEX', ordem: 6, descricao: 'Seleção da área do DECIPEX' },
    { id: 'subarea_decipex', nome: 'SUBAREA_DECIPEX', ordem: 7, descricao: 'Seleção da subárea (se aplicável)' },
    { id: 'arquitetura', nome: 'ARQUITETURA', ordem: 8, descricao: 'IA sugere macro/processo/subprocesso/atividade' },
    { id: 'confirmacao_arquitetura', nome: 'CONFIRMACAO_ARQUITETURA', ordem: 9, descricao: 'Confirma ou edita classificação IA' },
    { id: 'selecao_hierarquica', nome: 'SELECAO_HIERARQUICA', ordem: 10, descricao: 'Seleção manual hierárquica (dropdowns)' },
    { id: 'nome_processo', nome: 'NOME_PROCESSO', ordem: 11, descricao: 'Nome descritivo do processo' },
    { id: 'entrega_esperada', nome: 'ENTREGA_ESPERADA', ordem: 12, descricao: 'Resultado final esperado' },
    { id: 'confirmacao_entrega', nome: 'CONFIRMACAO_ENTREGA', ordem: 13, descricao: 'Confirma entrega sugerida' },
    { id: 'reconhecimento_entrega', nome: 'RECONHECIMENTO_ENTREGA', ordem: 14, descricao: 'Reconhece importância da entrega' },
    { id: 'dispositivos_normativos', nome: 'DISPOSITIVOS_NORMATIVOS', ordem: 15, descricao: 'Normas que fundamentam o processo' },
    { id: 'operadores', nome: 'OPERADORES', ordem: 16, descricao: 'Papéis envolvidos (executor, revisor, etc)' },
    { id: 'sistemas', nome: 'SISTEMAS', ordem: 17, descricao: 'Sistemas informatizados utilizados' },
    { id: 'fluxos', nome: 'FLUXOS', ordem: 18, descricao: 'Fluxos de entrada e saída' },
    { id: 'pontos_atencao', nome: 'PONTOS_ATENCAO', ordem: 19, descricao: 'Pontos de atenção e cuidados' },
    { id: 'revisao_pre_delegacao', nome: 'REVISAO_PRE_DELEGACAO', ordem: 20, descricao: 'Revisão antes de delegar para etapas' },
    { id: 'transicao_epica', nome: 'TRANSICAO_EPICA', ordem: 21, descricao: '🏆 Badge de conquista + transição motivacional' },
    { id: 'delegacao_etapas', nome: 'DELEGACAO_ETAPAS', ordem: 22, descricao: 'Handoff para Helena Etapas' },
  ];

  // Todas as interfaces dinâmicas implementadas
  const TODAS_INTERFACES = [
    { tipo: 'compromisso_cartografo', descricao: 'Botão animado de compromisso com emoji 🤝', estado: 'PEDIDO_COMPROMISSO' },
    { tipo: 'confirmacao_dupla', descricao: 'Dois botões: Confirmar / Editar', estado: 'CONFIRMA_NOME, ESCOLHA_TIPO_EXPLICACAO' },
    { tipo: 'areas', descricao: 'Cards de áreas do DECIPEX', estado: 'AREA_DECIPEX' },
    { tipo: 'subareas', descricao: 'Cards de subáreas (DIGEP-RO, etc)', estado: 'SUBAREA_DECIPEX' },
    { tipo: 'arquitetura_hierarquica', descricao: 'Seleção hierárquica com dropdowns', estado: 'SELECAO_HIERARQUICA' },
    { tipo: 'transicao_epica', descricao: '🏆 Badge animado + botão VAMOS / PAUSA', estado: 'TRANSICAO_EPICA' },
    { tipo: 'caixinha_reconhecimento', descricao: 'Caixinha de reconhecimento da entrega', estado: 'RECONHECIMENTO_ENTREGA' },
    { tipo: 'transicao', descricao: 'Transição genérica entre estados', estado: 'DELEGACAO_ETAPAS' },
    { tipo: 'normas', descricao: 'Interface de dispositivos normativos', estado: 'DISPOSITIVOS_NORMATIVOS' },
    { tipo: 'operadores', descricao: 'Seleção múltipla de operadores', estado: 'OPERADORES' },
    { tipo: 'sistemas', descricao: 'Seleção múltipla de sistemas', estado: 'SISTEMAS' },
    { tipo: 'cards_sistemas', descricao: 'Cards de sistemas com ícones', estado: 'SISTEMAS' },
    { tipo: 'fluxos', descricao: 'Interface de fluxos entrada/saída', estado: 'FLUXOS' },
  ];

  // Todos os handlers implementados
  const TODOS_HANDLERS = [
    '_processar_nome_usuario',
    '_processar_confirma_nome',
    '_processar_escolha_tipo_explicacao',
    '_processar_explicacao_longa',
    '_processar_duvidas_explicacao',
    '_processar_explicacao',
    '_processar_pedido_compromisso',
    '_processar_area_decipex',
    '_processar_subarea_decipex',
    '_processar_arquitetura',
    '_processar_confirmacao_arquitetura',
    '_processar_selecao_hierarquica',
    '_processar_nome_processo',
    '_processar_entrega_esperada',
    '_processar_confirmacao_entrega',
    '_processar_reconhecimento_entrega',
    '_processar_dispositivos_normativos',
    '_processar_operadores',
    '_processar_sistemas',
    '_processar_fluxos',
    '_processar_pontos_atencao',
    '_processar_revisao_pre_delegacao',
    '_processar_transicao_epica',
    '_processar_selecao_edicao',
    '_processar_delegacao_etapas',
  ];

  // Funcionalidades especiais
  const FUNCIONALIDADES_ESPECIAIS = [
    { nome: 'IA para Arquitetura', descricao: 'Busca no CSV oficial + Fallback para helena_ajuda_inteligente', arquivo: 'helena_ajuda_inteligente.py' },
    { nome: 'TF-IDF Fuzzy Matching', descricao: 'Similaridade textual ≥85% para sugestões', lib: 'scikit-learn' },
    { nome: 'Badge de Conquista', descricao: 'Badge animado com confetti (2 badges: Cartógrafo + Fase Prévia)', componente: 'BadgeTrofeu.tsx' },
    { nome: 'Edição Granular', descricao: 'Permite editar qualquer campo já coletado', estado: 'SELECAO_EDICAO' },
    { nome: 'Geração de CAP', descricao: 'Código na Arquitetura de Processos (oficial ou provisório)', metodo: '_gerar_codigo_processo()' },
    { nome: 'PDF Profissional', descricao: 'Geração de PDF com ReportLab (cores GOVBR)', arquivo: 'pdf_generator.py' },
    { nome: 'Preview HTML', descricao: 'Pré-visualização antes do download', endpoint: '/api/preview-pdf/' },
    { nome: 'Persistência de Sessão', descricao: 'Django session + Redis cache (15min) + DB (2 semanas)', modelo: 'ChatSession' },
    { nome: 'Auditoria Completa', descricao: 'AuditLog com rastreabilidade', modelo: 'AuditLog' },
    { nome: 'Idempotência', descricao: 'req_uuid previne duplicação de mensagens', modelo: 'ChatMessage' },
    { nome: 'Multi-tenancy', descricao: 'Isolamento por Orgao', modelo: 'ChatSession.orgao' },
    { nome: 'Progresso Detalhado', descricao: 'Cálculo automático de percentual + estados completos', metodo: 'obter_progresso()' },
    { nome: 'Consolidação com Etapas', descricao: 'Merge de dados POP + Etapas', metodo: 'consolidar_com_etapas()' },
    { nome: 'Base Legal Contextual', descricao: 'Sugestão de normas baseada no contexto', metodo: '_sugerir_base_legal_contextual()' },
  ];

  const estadosFiltrados = TODOS_ESTADOS.filter(e =>
    e.nome.toLowerCase().includes(filtro.toLowerCase()) ||
    e.descricao.toLowerCase().includes(filtro.toLowerCase())
  );

  const interfacesFiltradas = TODAS_INTERFACES.filter(i =>
    i.tipo.toLowerCase().includes(filtro.toLowerCase()) ||
    i.descricao.toLowerCase().includes(filtro.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="painel-desenvolvedor-overlay">
      <div className="painel-desenvolvedor">
        {/* Header */}
        <div className="painel-header">
          <h2>🔧 Painel de Desenvolvedor - Helena POP v2.0</h2>
          <button className="btn-fechar" onClick={onClose}>✕</button>
        </div>

        {/* Filtro */}
        <div className="painel-filtro">
          <input
            type="text"
            placeholder="🔍 Filtrar..."
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
            className="input-filtro"
          />
        </div>

        {/* Abas */}
        <div className="painel-abas">
          <button
            className={abaAtiva === 'estados' ? 'aba-ativa' : ''}
            onClick={() => setAbaAtiva('estados')}
          >
            Estados ({TODOS_ESTADOS.length})
          </button>
          <button
            className={abaAtiva === 'interfaces' ? 'aba-ativa' : ''}
            onClick={() => setAbaAtiva('interfaces')}
          >
            Interfaces ({TODAS_INTERFACES.length})
          </button>
          <button
            className={abaAtiva === 'handlers' ? 'aba-ativa' : ''}
            onClick={() => setAbaAtiva('handlers')}
          >
            Handlers ({TODOS_HANDLERS.length})
          </button>
          <button
            className={abaAtiva === 'funcionalidades' ? 'aba-ativa' : ''}
            onClick={() => setAbaAtiva('funcionalidades')}
          >
            Funcionalidades ({FUNCIONALIDADES_ESPECIAIS.length})
          </button>
          <button
            className={abaAtiva === 'dados' ? 'aba-ativa' : ''}
            onClick={() => setAbaAtiva('dados')}
          >
            Dados Atuais
          </button>
          <button
            className={abaAtiva === 'logs' ? 'aba-ativa' : ''}
            onClick={() => setAbaAtiva('logs')}
          >
            Logs ({messages.length})
          </button>
        </div>

        {/* Conteúdo */}
        <div className="painel-conteudo">

          {/* ABA: ESTADOS */}
          {abaAtiva === 'estados' && (
            <div className="aba-estados">
              <h3>📊 Todos os {TODOS_ESTADOS.length} Estados da Máquina</h3>
              <div className="lista-estados">
                {estadosFiltrados.map((estado) => (
                  <div key={estado.id} className="card-estado">
                    <div className="estado-header">
                      <span className="estado-ordem">#{estado.ordem}</span>
                      <span className="estado-nome">{estado.nome}</span>
                    </div>
                    <div className="estado-descricao">{estado.descricao}</div>
                    <div className="estado-id">ID: <code>{estado.id}</code></div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ABA: INTERFACES */}
          {abaAtiva === 'interfaces' && (
            <div className="aba-interfaces">
              <h3>🎨 Todas as {TODAS_INTERFACES.length} Interfaces Dinâmicas</h3>
              <div className="lista-interfaces">
                {interfacesFiltradas.map((interface_, idx) => (
                  <div key={idx} className="card-interface">
                    <div className="interface-tipo">
                      <code>{interface_.tipo}</code>
                    </div>
                    <div className="interface-descricao">{interface_.descricao}</div>
                    <div className="interface-estado">
                      Usado em: <strong>{interface_.estado}</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ABA: HANDLERS */}
          {abaAtiva === 'handlers' && (
            <div className="aba-handlers">
              <h3>⚙️ Todos os {TODOS_HANDLERS.length} Handlers Implementados</h3>
              <div className="lista-handlers">
                {TODOS_HANDLERS.map((handler, idx) => (
                  <div key={idx} className="card-handler">
                    <code>{handler}</code>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ABA: FUNCIONALIDADES */}
          {abaAtiva === 'funcionalidades' && (
            <div className="aba-funcionalidades">
              <h3>✨ Funcionalidades Especiais ({FUNCIONALIDADES_ESPECIAIS.length})</h3>
              <div className="lista-funcionalidades">
                {FUNCIONALIDADES_ESPECIAIS.map((func, idx) => (
                  <div key={idx} className="card-funcionalidade">
                    <div className="func-nome">{func.nome}</div>
                    <div className="func-descricao">{func.descricao}</div>
                    {func.arquivo && <div className="func-meta">📄 {func.arquivo}</div>}
                    {func.componente && <div className="func-meta">🎨 {func.componente}</div>}
                    {func.metodo && <div className="func-meta">⚙️ {func.metodo}</div>}
                    {func.modelo && <div className="func-meta">💾 {func.modelo}</div>}
                    {func.lib && <div className="func-meta">📚 {func.lib}</div>}
                    {func.endpoint && <div className="func-meta">🌐 {func.endpoint}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ABA: DADOS ATUAIS */}
          {abaAtiva === 'dados' && (
            <div className="aba-dados">
              <h3>📦 Dados Atuais do Formulário POP</h3>
              <div className="dados-json">
                <pre>{JSON.stringify(dadosPOP, null, 2)}</pre>
              </div>
            </div>
          )}

          {/* ABA: LOGS */}
          {abaAtiva === 'logs' && (
            <div className="aba-logs">
              <h3>📋 Histórico de Mensagens ({messages.length})</h3>
              <div className="lista-logs">
                {messages.slice().reverse().map((msg, idx) => (
                  <div key={idx} className={`log-item log-${msg.tipo}`}>
                    <div className="log-header">
                      <span className="log-tipo">{msg.tipo}</span>
                      <span className="log-index">#{messages.length - idx}</span>
                    </div>
                    <div className="log-mensagem">{msg.mensagem}</div>
                    {msg.interface && (
                      <div className="log-interface">
                        Interface: <code>{msg.interface.tipo}</code>
                      </div>
                    )}
                    {msg.metadados && (
                      <div className="log-metadados">
                        <details>
                          <summary>Metadados</summary>
                          <pre>{JSON.stringify(msg.metadados, null, 2)}</pre>
                        </details>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="painel-footer">
          <div className="footer-stats">
            <span>Estados: {TODOS_ESTADOS.length}</span>
            <span>Interfaces: {TODAS_INTERFACES.length}</span>
            <span>Handlers: {TODOS_HANDLERS.length}</span>
            <span>Funcionalidades: {FUNCIONALIDADES_ESPECIAIS.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PainelDesenvolvedor;
