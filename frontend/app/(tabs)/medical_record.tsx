import React, { useState } from 'react'
import { ScrollView, Switch, Text, View } from 'react-native'
import PatientList from '@/components/PatientList'
// import MedicationManager from '@/components/MedicationManager'
// import SymptomManager from '@/components/SymptomManager'
import { Patient } from '@/types/patient'
import SymptomModalManager from '@/components/SyptomModalManager'
import MedicationModalManager from '@/components/MedicationModalManager'

// mock data
// const mockPatients: Patient[] = [
//   {
//     id: 'p1',
//     name: 'John Smith',
//     age: 72,
//     avatar: '',
//     healthData: {
//       medications: [
//         { id: 'm1', drugName: 'Lisinopril', dosage: '10mg' },
//         { id: 'm2', drugName: 'Aspirin', dosage: '81mg' }
//       ],
//       symptoms: [
//         { id: 's1', description: 'Mild headache' },
//         { id: 's2', description: 'Slight dizziness when standing' }
//       ]
//     }
//   },
// ]

const medical_record = () => {
  // const [patients, setPatients] = useState<Patient[]>(mockPatients)
  // const [selectedPatientId, setSelectedPatientId] = useState(patients[0].id)
  const [isEditing, setIsEditing] = useState(false)

  // const selectedPatient = patients.find(p => p.id === selectedPatientId)!

  return (
    <ScrollView className="flex-1 bg-gray-100">
      <View className="p-4">
        <Text className="text-3xl font-bold text-center text-gray-800 mb-8">medical record</Text>
        
        {/* patient list */}
        {/* <PatientList
          patients={patients}
          selectedPatientId={selectedPatientId}
          onSelectPatient={setSelectedPatientId}
        /> */}

        {/* editting switch */}
        <View className="flex-row justify-center items-center my-4">
          <Text className="text-lg mr-2">Edit Mode</Text>
          <Switch value={isEditing} onValueChange={setIsEditing} />
        </View>

        {/* medication section
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
        /> */}

        {/* symptom section
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
          
        /> */}
        
        <View style={{}} >
          <Text className="text-xl font-bold mb-4">Medications</Text>
            <MedicationModalManager/>
        </View>

        <View style={{}} >
          <Text className="text-xl font-bold mb-4">symptoms</Text>
            <SymptomModalManager/>
        </View>



      </View>
    </ScrollView>
  )
}

export default medical_record
