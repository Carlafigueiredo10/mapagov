/**
 * HelenaPublicDrawer - Drawer demonstrativo da Helena na landing
 *
 * 100% client-side, sem API, sem persistência.
 * Mostra interações pré-roteirizadas sobre o portfólio de produtos.
 */
import { useState, useRef, useEffect } from 'react';

interface Props {
  open: boolean;
  onClose: () => void;
}

interface Msg {
  de: 'helena' | 'usuario';
  texto: string;
}

const SCRIPT: { pergunta: string; resposta: string }[] = [
  {
    pergunta: 'O que é o MapaGov?',
    resposta:
      'O MapaGov é uma plataforma de governança, riscos e conformidade para o setor público. ' +
      'Reúne ferramentas para mapeamento de processos, análise de riscos, planejamento estratégico ' +
      'e consolidação de evidências, seguindo os padrões da Administração Pública Federal.',
  },
  {
    pergunta: 'Quais produtos estão disponíveis?',
    resposta:
      'Hoje estão disponíveis quatro produtos:\n\n' +
      '• Gerador de POP — mapeia o processo e gera o Procedimento Operacional Padrão estruturado.\n' +
      '• Gerador de Fluxograma — gera fluxograma com base no POP ou a partir de conversa estruturada.\n' +
      '• Análise de Riscos — identifica, avalia e propõe tratamento de riscos com base nas diretrizes do MGI.\n' +
      '• Planejamento Estratégico — estrutura objetivos, diretrizes e ferramentas conforme o Guia Prático do MGI.',
  },
  {
    pergunta: 'Quais produtos estão previstos?',
    resposta:
      'Seis produtos estão planejados para as próximas fases:\n\n' +
      '• Plano de Ação e Acompanhamento — organiza ações, responsáveis e prazos para execução e monitoramento.\n' +
      '• Painel Executivo — apresenta indicadores e visão consolidada dos produtos gerados.\n' +
      '• Dossiê Consolidado de Governança — reúne em documento único tudo o que foi produzido sobre o objeto.\n' +
      '• Relatório de Conformidade — avalia se o processo seguiu o POP, etapas e prazos definidos.\n' +
      '• Relatório Técnico Consolidado — consolida o histórico completo em formato técnico para formalização.\n' +
      '• Revisão e Adequação de Documentos — revisa documentos para adequação às diretrizes federais.',
  },
  {
    pergunta: 'Como funciona o mapeamento?',
    resposta:
      'O mapeamento é construído progressivamente através de uma conversa guiada. ' +
      'Eu conduzo perguntas sobre o processo — atividade, operadores, sistemas, etapas — ' +
      'e organizo as informações no formato POP (Procedimento Operacional Padrão). ' +
      'O resultado pode ser usado como insumo para o fluxograma, a análise de riscos e os demais produtos.',
  },
];

const GREETING: Msg = {
  de: 'helena',
  texto:
    'Olá! Sou a Helena, assistente da plataforma MapaGov. ' +
    'Posso explicar como funciona a plataforma e o portfólio de produtos. Escolha uma pergunta:',
};

export default function HelenaPublicDrawer({ open, onClose }: Props) {
  const [msgs, setMsgs] = useState<Msg[]>([GREETING]);
  const [usedIndexes, setUsedIndexes] = useState<Set<number>>(new Set());
  const [typing, setTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Reset ao fechar
  useEffect(() => {
    if (!open) {
      setMsgs([GREETING]);
      setUsedIndexes(new Set());
      setTyping(false);
    }
  }, [open]);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [msgs, typing]);

  const handleChoice = (idx: number) => {
    if (typing || usedIndexes.has(idx)) return;

    const item = SCRIPT[idx];
    setMsgs((prev) => [...prev, { de: 'usuario', texto: item.pergunta }]);
    setUsedIndexes((prev) => new Set(prev).add(idx));
    setTyping(true);

    setTimeout(() => {
      const nextUsed = new Set(usedIndexes).add(idx);
      const allUsed = nextUsed.size >= SCRIPT.length;

      setMsgs((prev) => [
        ...prev,
        { de: 'helena', texto: item.resposta },
        ...(allUsed
          ? [
              {
                de: 'helena' as const,
                texto:
                  'Essas são as informações gerais do portfólio. ' +
                  'Para utilizar os produtos disponíveis, acesse a plataforma pelo portal.',
              },
            ]
          : []),
      ]);
      setTyping(false);
    }, 1200);
  };

  if (!open) return null;

  const available = SCRIPT.map((_, i) => i).filter((i) => !usedIndexes.has(i));
  const allDone = usedIndexes.size >= SCRIPT.length;

  return (
    <div style={overlay} onClick={onClose}>
      <div style={drawer} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={header}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <img
              src="/helena_em_pe.png"
              alt="Helena"
              style={{ width: 36, height: 36, borderRadius: '50%', objectFit: 'cover' }}
            />
            <div>
              <div style={{ fontWeight: 600, color: '#1B4F72', fontSize: '0.95rem' }}>Helena</div>
              <div style={{ fontSize: '0.75rem', color: '#7F8C8D' }}>Assistente da Plataforma MapaGov</div>
            </div>
          </div>
          <button onClick={onClose} style={closeBtn} aria-label="Fechar">
            ✕
          </button>
        </div>

        {/* Messages */}
        <div style={messagesArea}>
          {msgs.map((m, i) => (
            <div key={i} style={m.de === 'helena' ? bubbleHelena : bubbleUser}>
              {m.texto.split('\n').map((line, j) => (
                <span key={j}>
                  {line}
                  {j < m.texto.split('\n').length - 1 && <br />}
                </span>
              ))}
            </div>
          ))}

          {typing && (
            <div style={bubbleHelena}>
              <span style={typingDots}>●●●</span>
            </div>
          )}

          {/* Quick-reply buttons */}
          {!typing && !allDone && available.length > 0 && (
            <div style={choicesContainer}>
              {available.map((idx) => (
                <button key={idx} onClick={() => handleChoice(idx)} style={choiceBtn}>
                  {SCRIPT[idx].pergunta}
                </button>
              ))}
            </div>
          )}

          {!typing && allDone && (
            <div style={{ textAlign: 'center', padding: '1rem 0' }}>
              <a href="/portal" style={ctaLink}>
                Acessar o Portal
              </a>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  );
}

/* ---- Inline styles ---- */

const overlay: React.CSSProperties = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0,0,0,0.4)',
  zIndex: 1000,
  display: 'flex',
  justifyContent: 'flex-end',
};

const drawer: React.CSSProperties = {
  width: '100%',
  maxWidth: 420,
  height: '100%',
  background: '#f8fbff',
  display: 'flex',
  flexDirection: 'column',
  boxShadow: '-4px 0 20px rgba(0,0,0,0.15)',
};

const header: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '1rem 1.25rem',
  background: '#fff',
  borderBottom: '1px solid #e8f4fd',
};

const closeBtn: React.CSSProperties = {
  background: 'none',
  border: 'none',
  fontSize: '1.2rem',
  cursor: 'pointer',
  color: '#7F8C8D',
  padding: '0.25rem 0.5rem',
};

const messagesArea: React.CSSProperties = {
  flex: 1,
  overflowY: 'auto',
  padding: '1.25rem',
  display: 'flex',
  flexDirection: 'column',
  gap: '0.75rem',
};

const bubbleBase: React.CSSProperties = {
  maxWidth: '85%',
  padding: '0.75rem 1rem',
  borderRadius: '12px',
  fontSize: '0.9rem',
  lineHeight: 1.6,
};

const bubbleHelena: React.CSSProperties = {
  ...bubbleBase,
  background: '#fff',
  color: '#2C3E50',
  alignSelf: 'flex-start',
  border: '1px solid #e8f4fd',
};

const bubbleUser: React.CSSProperties = {
  ...bubbleBase,
  background: '#1351B4',
  color: '#fff',
  alignSelf: 'flex-end',
};

const typingDots: React.CSSProperties = {
  letterSpacing: 3,
  color: '#7F8C8D',
  animation: 'pulse 1.2s infinite',
};

const choicesContainer: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.5rem',
  padding: '0.5rem 0',
};

const choiceBtn: React.CSSProperties = {
  background: '#fff',
  border: '1px solid #1351B4',
  color: '#1351B4',
  padding: '0.6rem 1rem',
  borderRadius: '20px',
  cursor: 'pointer',
  fontSize: '0.85rem',
  textAlign: 'left',
  transition: 'all 0.2s ease',
};

const ctaLink: React.CSSProperties = {
  display: 'inline-block',
  background: '#1351B4',
  color: '#fff',
  padding: '0.6rem 1.5rem',
  borderRadius: '6px',
  textDecoration: 'none',
  fontWeight: 600,
  fontSize: '0.9rem',
};
