import { useState, useEffect } from "react";
import styles from "./BadgeTrofeu.module.css";

interface BadgeTrofeuProps {
  nomeBadge?: string;
  emoji?: string;
  descricao?: string;
  onContinuar: () => void;
}

export default function BadgeTrofeu({
  nomeBadge = "Cartógrafo(a) de Processos – Nível 1",
  emoji = "✔",
  descricao = "Primeiro trecho do percurso concluído. Seguimos para o próximo.",
  onContinuar
}: BadgeTrofeuProps) {
  const [showConfetti, setShowConfetti] = useState(false);
  const [badgeClicada, setBadgeClicada] = useState(false);

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
        {!badgeClicada ? (
          <div
            className={styles.trofeuWrapper}
            onClick={() => {
              setShowConfetti(true);
              setBadgeClicada(true);
            }}
            role="button"
            aria-label="Clique para visualizar marco de percurso"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                setShowConfetti(true);
                setBadgeClicada(true);
              }
            }}
          >
            <span className={styles.trofeu}>{emoji}</span>
            <span className={styles.btnTexto}>Ver marco do percurso</span>
          </div>
        ) : (
          <>
            <div className={styles.trofeuExibido}>
              <span className={styles.trofeu}>{emoji}</span>
            </div>
            <h3 className={styles.titulo}>Marco alcançado!</h3>
            <p className={styles.texto}>
              <strong>{nomeBadge}</strong> <br />
              {descricao}
            </p>

            <div className={styles.botoes}>
              <button
                className={styles.btnPrimario}
                onClick={handleContinuar}
                aria-label="Continuar para próxima etapa"
              >
                Continuar
              </button>
            </div>
          </>
        )}
      </div>

      {showConfetti && (
        <div className={styles.confettiContainer}>
          {[...Array(15)].map((_, i) => (
            <div
              key={i}
              className={styles.confetti}
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 0.5}s`,
                backgroundColor: ["#1351B4", "#50C878", "#4ecdc4"][
                  Math.floor(Math.random() * 3)
                ],
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
