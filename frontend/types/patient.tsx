// types/patient.ts

// 약물 타입 정의
export interface Medication {
  id: string;
  drug_name: string;
  dosage: string;
  pharmacy_name?: string;
}

// 증상 타입 정의
export interface Symptom {
  id: string;
  name: string;
  severity?: number;
  onset_description?: string;
}

// 환자 전체 정보 타입 정의
export interface Patient {
  id: string;
  name: string;
  age: number;
  avatar?: string;
  medications: Medication[];         // 현재 복용 중인 약물
  symptoms: Symptom[];               // 현재 증상
  past_medications?: Medication[];   // 과거 복용했던 약물
  past_symptoms?: Symptom[];         // 과거 겪었던 증상/질병
}
