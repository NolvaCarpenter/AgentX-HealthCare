
export type Medication = {
    pharmacy_name: string
    pharmacy_address: string
    pharmacy_phone: string
    drug_name: string
    drug_strength: string
    drug_instructions: string
    pill_markings: string
    manufacturer: string
    ndc_upc: string
    rx_written_date: string
    discard_after: string
    federal_caution: string
    rx_number: string
    refill_count: string
    prescriber_name: string
    reorder_after: string
    qty_filled: string
    location_code: string
    filled_date: string
    pharmacist: string
    barcode: string
  }

  export const medicationField: { label: string; key: keyof Medication }[] = [
  { label: "Pharmacy Name", key: "pharmacy_name" },
  { label: "Pharmacy Address", key: "pharmacy_address" },
  { label: "Pharmacy Phone", key: "pharmacy_phone" },
  { label: "Drug Name", key: "drug_name" },
  { label: "Drug Strength", key: "drug_strength" },
  { label: "Drug Instructions", key: "drug_instructions" },
  { label: "Pill Markings", key: "pill_markings" },
  { label: "Manufacturer", key: "manufacturer" },
  { label: "NDC/UPC", key: "ndc_upc" },
  { label: "RX Written Date", key: "rx_written_date" },
  { label: "Discard After", key: "discard_after" },
  { label: "Federal Caution", key: "federal_caution" },
  { label: "RX Number", key: "rx_number" },
  { label: "Refill Count", key: "refill_count" },
  { label: "Prescriber Name", key: "prescriber_name" },
  { label: "Reorder After", key: "reorder_after" },
  { label: "Qty Filled", key: "qty_filled" },
  { label: "Location Code", key: "location_code" },
  { label: "Filled Date", key: "filled_date" },
  { label: "Pharmacist", key: "pharmacist" },
  { label: "Barcode", key: "barcode" }
];


export type symptom_details = {
    name: string;
    onset_description: string;
    onset_pattern: string;
    characteristics: string[];
    location: string;
    quality: string;
    timing: string;
    context: string;
    frequency: string;
    severity: number;
    triggers: string[];
    aggravating_factors: string[];
    relieving_factors: string[];
    associated_symptoms: string[];
  };
  export const symptomDetailFields: { label: string; key: keyof symptom_details }[] = [
    { label: "Symptom Name", key: "name" },
    { label: "Onset Description", key: "onset_description" },
    { label: "Onset Pattern", key: "onset_pattern" },
    { label: "Characteristics", key: "characteristics" },
    { label: "Location", key: "location" },
    { label: "Quality", key: "quality" },
    { label: "Timing", key: "timing" },
    { label: "Context", key: "context" },
    { label: "Frequency", key: "frequency" },
    { label: "Severity (1-10)", key: "severity" },
    { label: "Triggers", key: "triggers" },
    { label: "Aggravating Factors", key: "aggravating_factors" },
    { label: "Relieving Factors", key: "relieving_factors" },
    { label: "Associated Symptoms", key: "associated_symptoms" }
  ];

  // 전체 환자의 symptom data를 구성하는 상위 구조
  export type Symptom = {
    primary_symptoms: string[]; // 주증상 이름들
    secondary_symptoms: string[]; // 부증상 이름들
    symptom_details: {
      [symptomName: string]: symptom_details; // 예: symptom_details["headache"]
    };
  };

  export const SymptomFields : { label: string; key: keyof Symptom}[]=[
    { label: "Primary Symptoms", key: "primary_symptoms" },
    { label: "Secondary Symptoms", key: "secondary_symptoms" }
  ]



export type Patient = {
    id: string
    name: string
    age: number
    adress : string
    healthData: {
        medications: Medication[]
        symptoms: Symptom[]
    }
}