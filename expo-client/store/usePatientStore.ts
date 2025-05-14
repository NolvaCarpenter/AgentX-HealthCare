// import { create } from 'zustand';
// import { Patient, Medication, Symptom } from '@/types/patient';

// // Zustand 전역 상태: 환자 정보 및 수정 함수 포함
// type PatientState = {
//   patient: Patient | null;
//   setPatient: (p: Patient) => void;
//   updateMedications: (meds: Medication[]) => void;
//   updateSymptoms: (syms: Symptom[]) => void;
// };

// // 상태 생성
// export const usePatientStore = create<PatientState>((set) => ({
//   patient: {
//     id: 'demo-p1',
//     name: 'hong',
//     age: 75,
//     gender: 'M',
//     height: 180,
//     weight: 70,
//     conditions: ['Hypertension', 'Diabetes'],
//     allergies: ['Penicillin'],
//     hospitalizations: ['2023-09-15: Knee surgery'],
//     medications: [
//       {
//         user_id: 'demo-p1',
//         label_uploaded_datetime: '2024-04-01T10:00:00',
//         pharmacy_name: 'RX OUTREACH',
//         pharmacy_address: '3171 Riverport Tech Center Dr, Maryland Heights',
//         pharmacy_phone: '1-800-769-3880',
//         patient_name: 'hong',
//         patient_address: '1234 City Street, Seoul',
//         drug_name: 'METFORMIN HCL TAB 1000MG',
//         drug_strength: '1000MG',
//         drug_instructions: 'TAKE 1 TABLET BY MOUTH DAILY',
//         pill_markings: '2 71 OVAL WHITE TABLET',
//         manufacturer: 'ZYGENERICS',
//         ndc_upc: '68382003010',
//         rx_written_date: '2024-04-01',
//         discard_after: '2025-04-01',
//         federal_caution: 'FEDERAL LAW PROHIBITS TRANSFER...',
//         rx_number: '1099747',
//         refill_count: 3,
//         prescriber_name: 'Dr. A. Physician',
//         reorder_after: '2024-05-20',
//         qty_filled: 90,
//         location_code: '555-020201',
//         filled_date: '2024-04-03',
//         pharmacist: 'S. Barranco',
//         barcode: '234582134291'
//       }
//     ],
//     symptoms: [
//       {
//         user_id: 'demo-p1',
//         recorded_datetime: '2024-04-05T09:00:00',
//         primary_symptoms: ['headache'],
//         secondary_symptoms: ['nausea'],
//         symptom_details: {
//           headache: {
//             name: 'headache',
//             onset_description: 'Started last night, becoming sharper',
//             onset_pattern: 'sudden',
//             characteristics: ['throbbing', 'constant'],
//             location: 'head',
//             quality: 'throbbing',
//             timing: 'constant',
//             context: 'during physical activity',
//             frequency: 'daily',
//             severity: 8,
//             triggers: ['stress', 'lack of sleep'],
//             aggravating_factors: ['bright light', 'noise'],
//             relieving_factors: ['rest', 'darkness'],
//             associated_symptoms: ['nausea', 'sensitivity to light']
//           },
//           nausea: {
//             name: 'nausea',
//             onset_description: 'After headache onset',
//             onset_pattern: 'gradual',
//             characteristics: ['queasy'],
//             location: 'stomach',
//             quality: 'nauseating',
//             timing: 'intermittent',
//             context: 'especially after meals',
//             frequency: 'frequent',
//             severity: 6,
//             triggers: ['smell of food'],
//             aggravating_factors: ['movement'],
//             relieving_factors: ['rest'],
//             associated_symptoms: ['loss of appetite']
//           }
//         }
//       }
//     ],
//     past_medications: [{
//       user_id: 'demo-p1',
//       label_uploaded_datetime: '2024-04-01T10:00:00',
//       pharmacy_name: 'RX OUTREACH',
//       pharmacy_address: '3171 Riverport Tech Center Dr, Maryland Heights',
//       pharmacy_phone: '1-800-769-3880',
//       patient_name: 'hong',
//       patient_address: '1234 City Street, Seoul',
//       drug_name: 'METFORMIN HCL TAB 1000MG',
//       drug_strength: '1000MG',
//       drug_instructions: 'TAKE 1 TABLET BY MOUTH DAILY',
//       pill_markings: '2 71 OVAL WHITE TABLET',
//       manufacturer: 'ZYGENERICS',
//       ndc_upc: '68382003010',
//       rx_written_date: '2024-04-01',
//       discard_after: '2025-04-01',
//       federal_caution: 'FEDERAL LAW PROHIBITS TRANSFER...',
//       rx_number: '1099747',
//       refill_count: 3,
//       prescriber_name: 'Dr. A. Physician',
//       reorder_after: '2024-05-20',
//       qty_filled: 90,
//       location_code: '555-020201',
//       filled_date: '2024-04-03',
//       pharmacist: 'S. Barranco',
//       barcode: '234582134291'
//     }],
//     past_symptoms: [{
//       name: 'nausea',
//       onset_description: 'After headache onset',
//       onset_pattern: 'gradual',
//       characteristics: ['queasy'],
//       location: 'stomach',
//       quality: 'nauseating',
//       timing: 'intermittent',
//       context: 'especially after meals',
//       frequency: 'frequent',
//       severity: 6,
//       triggers: ['smell of food'],
//       aggravating_factors: ['movement'],
//       relieving_factors: ['rest'],
//       associated_symptoms: ['loss of appetite']
//     }]
//   },

  
//   setPatient: (p) => set({ patient: p }),

//   updateMedications: (meds) =>
//     set((state) =>
//       state.patient ? { patient: { ...state.patient, medications: meds } } : state
//     ),

//   updateSymptoms: (syms) =>
//     set((state) =>
//       state.patient ? { patient: { ...state.patient, symptoms: syms } } : state
//     ),
// }));
import { create } from 'zustand';
import { Patient, Medication, Symptom } from '@/types/patient';

type PatientState = {
  medications: Medication[];
  symptoms: Symptom[];
  setMedications: (meds: Medication[]) => void;
  setSymptoms: (syms: Symptom[]) => void;
};

export const usePatientStore = create<PatientState>((set) => ({
  medications: [],
  symptoms: [],
  setMedications: (meds) => set({ medications: meds }),
  setSymptoms: (syms) => set({ symptoms: syms }),
}));
