// types/form/symptomField.ts

export const symptomField = [
  {
    key: 'name',
    label: 'Symptom Name',
    placeholder: 'Enter symptom name',
  },
  {
    key: 'onset_description',
    label: 'Onset Description',
    placeholder: 'Describe when and how the symptom began',
  },
  {
    key: 'onset_pattern',
    label: 'Onset Pattern',
    placeholder: 'e.g., sudden, gradual',
  },
  {
    key: 'location',
    label: 'Location',
    placeholder: 'Where is the symptom located?',
  },
  {
    key: 'quality',
    label: 'Quality',
    placeholder: 'Describe the quality (e.g., sharp, dull)',
  },
  {
    key: 'timing',
    label: 'Timing',
    placeholder: 'e.g., constant, intermittent',
  },
  {
    key: 'frequency',
    label: 'Frequency',
    placeholder: 'e.g., daily, weekly',
  },
  {
    key: 'severity',
    label: 'Severity (1-10)',
    placeholder: 'Enter severity level',
  },
  {
    key: 'context',
    label: 'Context',
    placeholder: 'Context of symptom appearance',
  },
  {
    key: 'characteristics',
    label: 'Characteristics',
    placeholder: 'Comma-separated list (e.g., throbbing, sharp)',
  },
  {
    key: 'triggers',
    label: 'Triggers',
    placeholder: 'Comma-separated list (e.g., stress, cold)',
  },
  {
    key: 'aggravating_factors',
    label: 'Aggravating Factors',
    placeholder: 'Comma-separated list (e.g., noise, light)',
  },
  {
    key: 'relieving_factors',
    label: 'Relieving Factors',
    placeholder: 'Comma-separated list (e.g., rest, darkness)',
  },
  {
    key: 'associated_symptoms',
    label: 'Associated Symptoms',
    placeholder: 'Comma-separated list (e.g., nausea, dizziness)',
  },
] as const;
// export const symptomField = [
//     {
//       key: 'name',
//       label: 'Symptom Name',
//       placeholder: 'Enter symptom name',
//     },
//     {
//       key: 'severity',
//       label: 'Severity (1-5)',
//       placeholder: 'Enter severity level',
//     },
//     {
//       key: 'onset_description',
//       label: 'Description',
//       placeholder: 'Describe the symptom',
//     },
//   ] as const;
  