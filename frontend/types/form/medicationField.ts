// types/form/medicationField.ts

export const medicationField = [
  {
    key: 'drug_name',
    label: 'Drug Name',
    placeholder: 'Enter drug name',
  },
  {
    key: 'drug_strength',
    label: 'Drug Strength',
    placeholder: 'Enter drug strength (e.g. 1000MG)',
  },
  {
    key: 'drug_instructions',
    label: 'Instructions',
    placeholder: 'Enter usage instructions',
  },
  {
    key: 'pharmacy_name',
    label: 'Pharmacy Name',
    placeholder: 'Enter pharmacy name',
  },
  {
    key: 'prescriber_name',
    label: 'Prescriber Name',
    placeholder: 'Enter prescriber name',
  },
  {
    key: 'refill_count',
    label: 'Refill Count',
    placeholder: 'Enter number of refills',
  },
  {
    key: 'recorded_datetime',
    label: 'Recorded Date',
    placeholder: 'Enter recorded date (YYYY-MM-DDTHH:mm:ss)',
  },
] as const;
// export const medicationField = [
//     {
//       key: 'drug_name',
//       label: 'Drug Name',
//       placeholder: 'Enter drug name',
//     },
//     {
//       key: 'dosage',
//       label: 'Dosage',
//       placeholder: 'Enter dosage',
//     },
//     {
//       key: 'pharmacy_name',
//       label: 'Pharmacy Name',
//       placeholder: 'Enter pharmacy name',
//     },
//   ] as const;