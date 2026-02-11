import { useState } from 'react';
import './StepEditModal.css';

interface FlowStep {
  id: number;
  label: string;
  texto: string;
}

interface StepEditModalProps {
  step: FlowStep | null;
  mode: 'edit' | 'insert';
  insertAfterLabel?: string;
  onSave: (stepId: number | null, texto: string) => void;
  onRemove: (stepId: number) => void;
  onClose: () => void;
}

export default function StepEditModal({
  step,
  mode,
  insertAfterLabel,
  onSave,
  onRemove,
  onClose,
}: StepEditModalProps) {
  const [texto, setTexto] = useState(mode === 'edit' && step ? step.texto : '');
  const [confirmRemove, setConfirmRemove] = useState(false);

  const title =
    mode === 'insert'
      ? `Nova etapa${insertAfterLabel ? ` (após ${insertAfterLabel})` : ''}`
      : `Editar ${step?.label || 'etapa'}`;

  const handleSave = () => {
    if (!texto.trim()) return;
    onSave(mode === 'edit' && step ? step.id : null, texto.trim());
  };

  return (
    <div className="step-modal-overlay" onClick={onClose}>
      <div className="step-modal" onClick={(e) => e.stopPropagation()}>
        <h3 className="step-modal__title">{title}</h3>

        <textarea
          className="step-modal__textarea"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Descreva a etapa..."
          rows={3}
          autoFocus
        />

        <div className="step-modal__actions">
          <button className="step-modal__btn step-modal__btn--primary" onClick={handleSave} disabled={!texto.trim()}>
            Salvar
          </button>
          <button className="step-modal__btn step-modal__btn--cancel" onClick={onClose}>
            Cancelar
          </button>

          {mode === 'edit' && step && (
            <>
              {!confirmRemove ? (
                <button
                  className="step-modal__btn step-modal__btn--danger"
                  onClick={() => setConfirmRemove(true)}
                >
                  Remover etapa
                </button>
              ) : (
                <button
                  className="step-modal__btn step-modal__btn--danger-confirm"
                  onClick={() => onRemove(step.id)}
                >
                  Confirmar remoção
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
