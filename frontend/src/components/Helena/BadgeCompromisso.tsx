import { useState, useEffect } from "react";
import styles from "./BadgeTrofeu.module.css";

interface BadgeCompromissoProps {
  nomeCompromisso?: string;
  emoji?: string;
  descricao?: string;
  onContinuar: () => void;
}

export default function BadgeCompromisso({
  nomeCompromisso = "Compromisso de Cartógrafo(a)",
  emoji = "🤝",
  descricao = "Você se comprometeu a registrar seu processo com cuidado e dedicação!",
  onContinuar
}: BadgeCompromissoProps) {
  const [showConfetti, setShowConfetti] = useState(false);
  const [compromissoFirmado, setCompromissoFirmado] = useState(false);

  useEffect(() => {
    if (showConfetti) {
      const timer = setTimeout(() => setShowConfetti(false), 2500);
      return () => clearTimeout(timer);
    }
  }, [showConfetti]);

  const handleContinuar = () => {
    // Não remove o componente, apenas chama o callback
    onContinuar();
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {!compromissoFirmado ? (
          <div
            className={styles.trofeuWrapper}
            onClick={() => {
              setShowConfetti(true);
              setCompromissoFirmado(true);
            }}
            role="button"
            aria-label="Clique para firmar seu compromisso"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                setShowConfetti(true);
                setCompromissoFirmado(true);
              }
            }}
          >
            <span className={styles.trofeu}>{emoji}</span>
            <span className={styles.btnTexto}>Clique aqui pra fechar nosso acordo</span>
          </div>
        ) : (
          <>
            <div className={styles.trofeuExibido}>
              <span className={styles.trofeu}>{emoji}</span>
            </div>
            <h3 className={styles.titulo}>Compromisso firmado!</h3>

            <div className={styles.botoes}>
              <button
                className={styles.btnPrimario}
                onClick={handleContinuar}
                aria-label="Continuar para próxima etapa"
              >
                Vamos lá!
              </button>
            </div>
          </>
        )}
      </div>

      {showConfetti && (
        <div className={styles.confettiContainer}>
          {[...Array(40)].map((_, i) => (
            <div
              key={i}
              className={styles.confetti}
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 0.5}s`,
                backgroundColor: ["#FFD700", "#1351B4", "#50C878", "#FF69B4"][
                  Math.floor(Math.random() * 4)
                ],
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
