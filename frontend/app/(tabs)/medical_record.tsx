import React, { useState } from 'react'
import { ScrollView, Switch, Text, View } from 'react-native'
import { Patient } from '@/types/patient'
import SymptomModalManager from '@/components/SymptomModalManager'
import MedicationModalManager from '@/components/MedicationModalManager'

const medical_record = () => {
  // const [patients, setPatients] = useState<Patient[]>(mockPatients)
  // const [selectedPatientId, setSelectedPatientId] = useState(patients[0].id)
  const [isEditing, setIsEditing] = useState(false)

  // const selectedPatient = patients.find(p => p.id === selectedPatientId)!

  return (
    <ScrollView className="flex-1 bg-gray-100">
      <View className="p-4">
        <Text className="text-3xl font-bold text-center text-gray-800 mb-8">medical record</Text>

        {/* editting switch */}
        {/* <View className="flex-row justify-center items-center my-4">
          <Text className="text-lg mr-2">Edit Mode</Text>
          <Switch value={isEditing} onValueChange={setIsEditing} />
        </View> */}
        
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
