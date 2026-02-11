import './StepCard.css';

interface FlowStep {
  id: number;
  label: string;
  texto: string;
}

interface StepCardProps {
  step: FlowStep;
  onEdit: (stepId: number) => void;
  onInsertAfter: (stepId: number) => void;
  isActive: boolean;
}

export default function StepCard({ step, onEdit, onInsertAfter, isActive }: StepCardProps) {
  return (
    <div
      className={`step-card${isActive ? ' step-card--active' : ''}`}
      onClick={() => onEdit(step.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onEdit(step.id)}
    >
      <div className="step-card__label">{step.label}</div>
      <div className="step-card__texto">{step.texto}</div>
      <button
        className="step-card__insert-btn"
        onClick={(e) => {
          e.stopPropagation();
          onInsertAfter(step.id);
        }}
        title="Inserir etapa abaixo"
      >
        + Inserir abaixo
      </button>
    </div>
  );
}
