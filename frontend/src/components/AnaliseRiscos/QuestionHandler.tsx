// QuestionHandler.tsx - Handler para diferentes tipos de perguntas
import { useState } from 'react';
import type { Question } from './types';
import styles from './QuestionHandler.module.css';

interface QuestionHandlerProps {
  question: Question;
  value: string | Record<string, string>;
  onChange: (value: string | Record<string, string>) => void;
  onSubmit: (value: string | Record<string, string>) => void;
}

export default function QuestionHandler({
  question,
  value,
  onChange,
  onSubmit,
}: QuestionHandlerProps) {
  const [systemsRisks, setSystemsRisks] = useState<Record<string, string>>({});
  const [othersText, setOthersText] = useState('');

  const handleSubmit = () => {
    if (!value || (typeof value === 'string' && value.trim() === '')) {
      if (question.required) {
        alert('Esta pergunta é obrigatória!');
        return;
      }
    }

    if (question.type === 'systems_checklist') {
      onSubmit({
        systems: systemsRisks,
        others: othersText,
      });
    } else {
      onSubmit(value);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && question.type === 'text') {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Renderização baseada no tipo
  if (question.type === 'text') {
    return (
      <div className={styles.container}>
        <textarea
          className={styles.textarea}
          value={value as string}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Digite sua resposta..."
          rows={3}
          autoFocus
        />
        <button
          className={styles.btnSubmit}
          onClick={handleSubmit}
          disabled={question.required && !(value as string).trim()}
        >
          Enviar →
        </button>
      </div>
    );
  }

  if (question.type === 'select') {
    return (
      <div className={styles.container}>
        <div className={styles.selectOptions}>
          {question.options?.map((opt) => (
            <button
              key={opt.value}
              className={`${styles.optionBtn} ${
                value === opt.value ? styles.selected : ''
              }`}
              onClick={() => {
                onChange(opt.value);
                setTimeout(() => onSubmit(opt.value), 300);
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (question.type === 'systems_checklist') {
    if (!question.systems || question.systems.length === 0) {
      // Se não há sistemas, mostrar campo de texto
      return (
        <div className={styles.container}>
          <p className={styles.noSystemsNote}>
            Nenhum sistema específico foi identificado no POP.
          </p>
          <textarea
            className={styles.textarea}
            value={othersText}
            onChange={(e) => setOthersText(e.target.value)}
            placeholder="Liste os sistemas utilizados..."
            rows={3}
            autoFocus
          />
          <button className={styles.btnSubmit} onClick={handleSubmit}>
            Enviar →
          </button>
        </div>
      );
    }

    return (
      <div className={styles.container}>
        <div className={styles.systemsGrid}>
          {question.systems.map((system) => (
            <div key={system} className={styles.systemCard}>
              <div className={styles.systemName}>{system}</div>
              <div className={styles.riskLevels}>
                {question.risk_levels?.map((level) => (
                  <label key={level} className={styles.radioLabel}>
                    <input
                      type="radio"
                      name={`system_${system}`}
                      value={level}
                      checked={systemsRisks[system] === level}
                      onChange={(e) =>
                        setSystemsRisks({
                          ...systemsRisks,
                          [system]: e.target.value,
                        })
                      }
                    />
                    <span>{level}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className={styles.othersSection}>
          <label className={styles.othersLabel}>
            Outros sistemas não mencionados:
          </label>
          <textarea
            className={styles.textarea}
            value={othersText}
            onChange={(e) => setOthersText(e.target.value)}
            placeholder="Liste outros sistemas..."
            rows={2}
          />
        </div>

        <button className={styles.btnSubmit} onClick={handleSubmit}>
          Enviar →
        </button>
      </div>
    );
  }

  return <div>Tipo de pergunta não suportado</div>;
}
