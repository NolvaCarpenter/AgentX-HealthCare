// // types/patient.ts
// types/patient.ts

// 약물 타입 정의 (변경된 구조 반영)
export interface Medication {
  user_id: string;
  recorded_datetime: string;
  pharmacy_name: string;
  pharmacy_address: string;
  pharmacy_phone: string;
  patient_name: string;
  patient_address: string;
  drug_name: string;
  drug_strength: string;
  drug_instructions: string;
  pill_markings: string;
  manufacturer: string;
  ndc_upc: string;
  rx_written_date: string;
  discard_after: string;
  federal_caution: string;
  rx_number: string;
  refill_count: number;
  prescriber_name: string;
  reorder_after: string;
  qty_filled: number;
  location_code: string;
  filled_date: string;
  pharmacist: string;
  barcode: string;
}

// 증상 세부 정보 타입 정의
export interface SymptomDetail {
  name: string;
  onset_description: string;
  onset_pattern: string;
  characteristics: string[];
  location: string;
  quality: string;
  timing: string;
  context: string;
  frequency: string;
  severity: number; // 1 to 10
  triggers: string[];
  aggravating_factors: string[];
  relieving_factors: string[];
  associated_symptoms: string[];
}

// 증상 타입 정의 (변경된 구조 반영)
export interface Symptom {
  user_id: string;
  recorded_datetime: string;
  primary_symptoms: string[];
  secondary_symptoms: string[];
  symptom_details: Record<string, SymptomDetail>;
}

// 환자 전체 정보 타입 정의
export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: string;
  height: number;
  weight: number;
  avatar?: string;
  medications: Medication[];         // 현재 복용 중인 약물
  symptoms: Symptom[];               // 현재 증상
  past_medications?: Medication[];   // 과거 복용했던 약물
  past_symptoms?: SymptomDetail[];         // 과거 겪었던 증상/질병
  conditions?: string[];             // 진단된 질병 목록
  allergies?: string[];              // 알레르기 정보
  hospitalizations?: string[];       // 입원 이력 날짜 또는 설명
}

// // 약물 타입 정의
// export interface Medication {
//   id: string;
//   drug_name: string;
//   dosage: string;
//   pharmacy_name?: string;
// }

// // 증상 타입 정의
// export interface Symptom {
//   id: string;
//   name: string;
//   severity?: number;
//   onset_description?: string;
// }

// // 환자 전체 정보 타입 정의
// export interface Patient {
//   id: string;
//   name: string;
//   age: number;
//   gender : string;
//   height : number;
//   weight : number;
//   avatar?: string;
//   medications: Medication[];         // 현재 복용 중인 약물
//   symptoms: Symptom[];               // 현재 증상
//   past_medications?: Medication[];   // 과거 복용했던 약물
//   past_symptoms?: Symptom[];         // 과거 겪었던 증상/질병
// }

