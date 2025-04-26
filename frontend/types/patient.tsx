export type Medication = {
    id: string
    drugName: string
    dosage: string
}

export type Symptom = {
    id: string
    description: string
}

export type Patient = {
    id: string
    name: string
    age: number
    avatar: string
    healthData: {
        medications: Medication[]
        symptoms: Symptom[]
    }
}