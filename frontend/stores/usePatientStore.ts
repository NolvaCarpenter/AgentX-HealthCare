// stores/usePatientStore.ts
import { create } from 'zustand';
import { Patient, Medication, Symptom } from '@/types/patient';

// Zustand 전역 상태: 환자 정보 및 수정 함수 포함
type PatientState = {
  patient: Patient | null;
  setPatient: (p: Patient) => void;
  updateMedications: (meds: Medication[]) => void;
  updateSymptoms: (syms: Symptom[]) => void;
};

// 상태 생성
export const usePatientStore = create<PatientState>((set) => ({
  // patient: null,
  patient: {
    id: 'demo-p1',
    name: '홍길동',
    age: 75,
    medications: [
      { id: 'm1', drug_name: 'Lisinopril', dosage: '10mg' },
      { id: 'm2', drug_name: 'Aspirin', dosage: '81mg' }
    ],
    symptoms: [
      { id: 's1', name: '두통', severity: 2 },
      { id: 's2', name: '기립 시 어지러움', severity: 1 }
    ],
    past_medications: [
      { id: 'pm1', drug_name: 'Metformin', dosage: '500mg', pharmacy_name: '건강약국' },
      { id: 'pm2', drug_name: 'Atorvastatin', dosage: '20mg' }
    ],
    past_symptoms: [
      { id: 'ps1', name: '요통', severity: 3, onset_description: '작년 겨울에 한 달간 지속됨' },
      { id: 'ps2', name: '기침', onset_description: '감기 증상과 함께 발생' }
    ]
  },

  // 전체 환자 정보 설정
  setPatient: (p) => set({ patient: p }),

  // 약물 정보만 업데이트
  updateMedications: (meds) =>
    set((state) =>
      state.patient
        ? { patient: { ...state.patient, medications: meds } }
        : state
    ),

  // 증상 정보만 업데이트
  updateSymptoms: (syms) =>
    set((state) =>
      state.patient
        ? { patient: { ...state.patient, symptoms: syms } }
        : state
    ),
}));
