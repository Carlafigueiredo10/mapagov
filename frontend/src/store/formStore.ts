import { create } from 'zustand';
import type { POPData } from '../types/pop.types';

interface FormState {
  popData: POPData;
  isReviewMode: boolean;
  
  updateField: (field: keyof POPData, value: any) => void;
  updateMultipleFields: (data: Partial<POPData>) => void;
  clearForm: () => void;
  setReviewMode: (status: boolean) => void;
  getFilledFieldsCount: () => number;
}

export const useFormStore = create<FormState>((set, get) => ({
  popData: {},
  isReviewMode: false,

  updateField: (field, value) =>
    set((state) => ({
      popData: { ...state.popData, [field]: value },
    })),

  updateMultipleFields: (data) =>
    set((state) => ({
      popData: { ...state.popData, ...data },
    })),

  clearForm: () =>
    set({
      popData: {},
      isReviewMode: false,
    }),

  setReviewMode: (status) => set({ isReviewMode: status }),

  getFilledFieldsCount: () => {
    const { popData } = get();
    return Object.values(popData).filter(
      (v) => v && (typeof v === 'string' ? v.length > 5 : true)
    ).length;
  },
}));