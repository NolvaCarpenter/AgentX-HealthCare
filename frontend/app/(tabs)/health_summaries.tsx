import React, { useState } from 'react'
import { ScrollView, Switch, Text, View } from 'react-native'
import PatientList from '@/components/PatientList'
import MedicationManager from '@/components/MedicationManager'
import SymptomManager from '@/components/SymptomManager'
import { Patient } from '@/types/patient'

// 임시 환자 데이터 (약물 포함)
const mockPatients: Patient[] = [
  {
    id: 'p1',
    name: 'John Smith',
    age: 72,
    avatar: '',
    healthData: {
      medications: [
        { id: 'm1', drugName: 'Lisinopril', dosage: '10mg' },
        { id: 'm2', drugName: 'Aspirin', dosage: '81mg' }
      ],
      symptoms: [
        { id: 's1', description: 'Mild headache' },
        { id: 's2', description: 'Slight dizziness when standing' }
      ]
    }
  },
  {
    id: 'p2',
    name: 'Mary Johnson',
    age: 68,
    avatar: '',
    healthData: {
      medications: [
        { id: 'm3', drugName: 'Metformin', dosage: '500mg' }
      ],
      symptoms: [
        { id: 's3', description: 'Fatigue in the afternoons' }
      ]
    }
  },
  {
    id: 'p3',
    name: 'Robert Davis',
    age: 75,
    avatar: '',
    healthData: {
      medications: [
        { id: 'm4', drugName: 'Atorvastatin', dosage: '20mg' },
        { id: 'm5', drugName: 'Losartan', dosage: '50mg' }
      ],
      symptoms: [
        { id: 's4', description: 'Occasional muscle soreness' },
        { id: 's5', description: 'Mild joint pain' }
      ]
    }
  },
  {
    id: 'p4',
    name: 'Emily Wilson',
    age: 70,
    avatar: '',
    healthData: {
      medications: [
        { id: 'm6', drugName: 'Simvastatin', dosage: '40mg' }
      ],
      symptoms: [
        { id: 's6', description: 'Frequent thirst' },
        { id: 's7', description: 'Numbness in feet' }
      ]
    }
  }
]

const health_summaries = () => {
  const [patients, setPatients] = useState<Patient[]>(mockPatients)
  const [selectedPatientId, setSelectedPatientId] = useState(patients[0].id)
  const [isEditing, setIsEditing] = useState(false)

  const selectedPatient = patients.find(p => p.id === selectedPatientId)!

  return (
    <ScrollView className="flex-1 bg-gray-100">
      <View className="p-4">
        <Text className="text-3xl font-bold text-center text-gray-800 mb-8">Health Summaries</Text>
        {/* 환자 리스트 */}
        <PatientList
          patients={patients}
          selectedPatientId={selectedPatientId}
          onSelectPatient={setSelectedPatientId}
        />

        {/* 편집 모드 스위치 */}
        <View className="flex-row justify-center items-center my-4">
          <Text className="text-lg mr-2">Edit Mode</Text>
          <Switch value={isEditing} onValueChange={setIsEditing} />
        </View>

        {/* 약물 관리 */}
        <MedicationManager
          medications={selectedPatient.healthData.medications}
          isEditing={isEditing}
          onChangeMedications={(newMedications) => {
            setPatients(prev =>
              prev.map(p =>
                p.id === selectedPatientId
                  ? { ...p, healthData: { ...p.healthData, medications: newMedications } }
                  : p
              )
            )
          }}
        />
        <SymptomManager
          symptoms={selectedPatient.healthData.symptoms}
          isEditing={isEditing}
          onChangeSymptoms={(newSymptoms) => {
            setPatients(prev =>
              prev.map(p =>
                p.id === selectedPatientId
                  ? { ...p, healthData: { ...p.healthData, symptoms: newSymptoms } }
                  : p
              )
            )
          }}
        />
      </View>
    </ScrollView>
  )
}

export default health_summaries
