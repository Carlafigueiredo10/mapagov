import StepCard from './StepCard';

interface FlowStep {
  id: number;
  label: string;
  texto: string;
}

interface StepListProps {
  steps: FlowStep[];
  activeStepId: number | null;
  onEdit: (stepId: number) => void;
  onInsertAfter: (stepId: number) => void;
}

export default function StepList({ steps, activeStepId, onEdit, onInsertAfter }: StepListProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {steps.map((step) => (
        <StepCard
          key={step.id}
          step={step}
          isActive={step.id === activeStepId}
          onEdit={onEdit}
          onInsertAfter={onInsertAfter}
        />
      ))}
    </div>
  );
}
