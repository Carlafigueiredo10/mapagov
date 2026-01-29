// ChatRiscos.tsx - Chat conversacional para perguntas de análise de riscos
import { useEffect, useRef, useState } from 'react';
import { useRiscosStore } from '../../store/riscosStore';
import { QUESTIONS_RISCOS, detectSystemsFromPOPText } from '../../data/questionsRiscos';
import { analisarRiscos } from '../../services/riscosApi';
import QuestionHandler from './QuestionHandler';
import styles from './ChatRiscos.module.css';

export default function ChatRiscos() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [currentAnswer, setCurrentAnswer] = useState<string | Record<string, string>>('');

  const {
    messages,
    currentQuestionIndex,
    answers,
    popText,
    popInfo,
    isAnswering,
    addMessage,
    saveAnswer,
    setCurrentQuestion,
    setIsAnswering,
    startAnalysis,
    setRelatorio,
    finishAnalysis,
    setError,
  } = useRiscosStore();

  // Auto-scroll ao adicionar mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Inicia primeira pergunta
  useEffect(() => {
    if (messages.length === 1 && currentQuestionIndex === 0) {
      setTimeout(() => askNextQuestion(), 1000);
    }
  }, [messages]);

  // Detectar sistemas do POP para pergunta 8
  useEffect(() => {
    if (popText && popInfo) {
      const detectedSystems = detectSystemsFromPOPText(popText, popInfo);
      const q8 = QUESTIONS_RISCOS.find((q) => q.id === 8);
      if (q8) {
        q8.systems = detectedSystems;
      }
    }
  }, [popText, popInfo]);

  const askNextQuestion = () => {
    if (currentQuestionIndex >= QUESTIONS_RISCOS.length) {
      // Todas perguntas respondidas - iniciar análise
      handleFinishQuestions();
      return;
    }

    const question = QUESTIONS_RISCOS[currentQuestionIndex];

    addMessage({
      role: 'helena',
      content: `**${question.category}** (${currentQuestionIndex + 1}/20)\n\n${question.question}`,
      questionId: question.id,
      isQuestion: true,
    });
  };

  const handleAnswer = (value: string | Record<string, string>) => {
    const question = QUESTIONS_RISCOS[currentQuestionIndex];

    // Salvar resposta
    saveAnswer(question.id, value);

    // Adicionar resposta do usuário ao chat
    const displayValue = typeof value === 'string'
      ? value
      : JSON.stringify(value, null, 2);

    addMessage({
      role: 'user',
      content: displayValue,
    });

    // Feedback da Helena
    addMessage({
      role: 'helena',
      content: `✓ Resposta registrada! ${currentQuestionIndex + 1}/20 perguntas respondidas.`,
    });

    // Próxima pergunta
    setCurrentQuestion(currentQuestionIndex + 1);
    setCurrentAnswer('');

    setTimeout(() => {
      askNextQuestion();
    }, 800);
  };

  const handleFinishQuestions = async () => {
    addMessage({
      role: 'helena',
      content: `🎉 Excelente! Recebi todas as 20 respostas.\n\nAgora vou analisar os riscos do POP "${popInfo?.titulo}" usando IA avançada com os referenciais:\n\n• COSO ERM (2017)\n• ISO 31000 (2018)\n• Modelo das Três Linhas (IIA)\n• Referencial Básico de Governança TCU\n\n⏳ Aguarde enquanto processo...`,
    });

    setIsAnswering(true);
    startAnalysis();

    try {
      const result = await analisarRiscos({
        pop_text: popText,
        pop_info: popInfo!,
        answers,
      });

      if (result.success && result.data) {
        setRelatorio(result.data);
        finishAnalysis();

        addMessage({
          role: 'helena',
          content: `✅ **Análise concluída!**\n\n🔍 Identifiquei **${result.data.riscos.length} riscos** no processo, sendo:\n• 🔴 ${result.data.matriz_riscos.criticos} críticos\n• 🟠 ${result.data.matriz_riscos.altos} altos\n• 🟡 ${result.data.matriz_riscos.moderados} moderados\n• 🟢 ${result.data.matriz_riscos.baixos} baixos\n\nVeja o relatório completo abaixo! 👇`,
        });
      } else {
        throw new Error(result.error || 'Erro na análise');
      }
    } catch (error) {
      console.error('Erro ao analisar riscos:', error);
      setError('Erro ao analisar riscos. Tente novamente.');

      addMessage({
        role: 'helena',
        content: `❌ Desculpe, houve um erro na análise. Por favor, tente novamente ou entre em contato com o suporte.`,
      });
    } finally {
      setIsAnswering(false);
    }
  };

  const currentQuestion = QUESTIONS_RISCOS[currentQuestionIndex];
  const shouldShowInput = currentQuestionIndex < QUESTIONS_RISCOS.length && !isAnswering;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <img src="/helena_riscos.png" alt="Helena" className={styles.helenaAvatar} />
          <div>
            <h2>Helena - Análise de Riscos</h2>
            <p className={styles.status}>
              {isAnswering ? 'Analisando...' : `Pergunta ${currentQuestionIndex + 1}/${QUESTIONS_RISCOS.length}`}
            </p>
          </div>
        </div>
        {popInfo && (
          <div className={styles.popInfo}>
            <small>POP: {popInfo.titulo}</small>
          </div>
        )}
      </div>

      <div className={styles.messagesContainer}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.message} ${
              msg.role === 'helena' ? styles.helena : styles.user
            }`}
          >
            {msg.role === 'helena' && (
              <img src="/helena_riscos.png" alt="Helena" className={styles.avatar} />
            )}
            <div className={styles.messageContent}>
              <div className={styles.messageText}>
                {msg.content.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
              <span className={styles.timestamp}>
                {msg.timestamp.toLocaleTimeString('pt-BR', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
            {msg.role === 'user' && (
              <span className={styles.avatar}>👤</span>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {isAnswering && (
          <div className={`${styles.message} ${styles.helena}`}>
            <img src="/helena_riscos.png" alt="Helena" className={styles.avatar} />
            <div className={styles.messageContent}>
              <div className={styles.typing}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input de resposta - sempre visível durante as perguntas */}
      {shouldShowInput && currentQuestion && (
        <div className={styles.inputArea}>
          <QuestionHandler
            question={currentQuestion}
            value={currentAnswer}
            onChange={setCurrentAnswer}
            onSubmit={handleAnswer}
          />
        </div>
      )}
    </div>
  );
}
