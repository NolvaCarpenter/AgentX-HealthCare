import React, { useState } from 'react'
import { View, Text, TouchableOpacity, TextInput } from 'react-native'
import { Medication } from '@/types/patient'
import AccordionItem from './AccordionItem'

// Props type definition
interface MedicationManagerProps {
  medications: Medication[]
  isEditing: boolean
  onChangeMedications: (newMedications: Medication[]) => void
}

export default function MedicationManager({ medications, isEditing, onChangeMedications }: MedicationManagerProps) {
  //Function to update medication information
  const handleUpdateMedication = (id: string, field: keyof Medication, value: string) => {
    const updated = medications.map(med =>
      med.id === id ? { ...med, [field]: value } : med
    )
    onChangeMedications(updated)
  }

  return (
    <View className="p-4">
      <Text className="text-xl font-bold mb-4">Medications</Text>
      {medications.map((med) => (
        <AccordionItem
          key={med.id}
          title={`${med.drugName} (${med.dosage})`}
        >

          {/*Delete Item */}
          {isEditing && (
            <TouchableOpacity
              className="self-end mb-2 bg-red-500 px-3 py-1 rounded"
              onPress={() => {
                const updated = medications.filter((m) => m.id !== med.id)
                onChangeMedications(updated)
              }}
            >
              <Text className="text-white">Delete</Text>
            </TouchableOpacity>
          )}

          {isEditing ? (
            <>
              <Text className="text-base">Drug Name:</Text>
              <TextInput
                value={med.drugName}
                onChangeText={(text) => handleUpdateMedication(med.id, 'drugName', text)}
                className="border rounded px-3 py-2"
              />
              <Text className="text-base">Dosage:</Text>
              <TextInput
                value={med.dosage}
                onChangeText={(text) => handleUpdateMedication(med.id, 'dosage', text)}
                className="border rounded px-3 py-2"
              />
            </>
          ) : (
            <>
              <Text className="text-base">Drug Name: {med.drugName}</Text>
              <Text className="text-base">Dosage: {med.dosage}</Text>
            </>
          )}
        </AccordionItem>
      ))}

      {/* add medication button */}
      {isEditing && (
        <TouchableOpacity
          className="mt-4 p-4 bg-blue-500 rounded-lg items-center"
          onPress={() => {
            const newMed = { id: Date.now().toString(), drugName: 'New Drug', dosage: '0mg' }
            onChangeMedications([...medications, newMed])
          }}
        >
          <Text className="text-white font-medium">+ Add Medication</Text>
        </TouchableOpacity>
      )}
    </View>
  )
}
