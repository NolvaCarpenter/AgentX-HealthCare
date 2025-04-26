import React from 'react'
import { FlatList, View, Text, TouchableOpacity, Image } from 'react-native'
import {Patient, Medication, Symptom} from '@/types/patient'


type PatientListProps = {
    patients: Patient[]
    selectedPatientId: string
    onSelectPatient: (id: string) => void
}

export default function PatientList({ patients, selectedPatientId, onSelectPatient }: PatientListProps) {
    return (
        <FlatList
            horizontal
            data={patients}
            keyExtractor={(item) => item.id}
            //showsHorizontalScrollIndicator={false}
            renderItem={({ item }) => {
                const isSelected = item.id === selectedPatientId
                return (
                    <TouchableOpacity
                        onPress={() => onSelectPatient(item.id)}
                        className={`items-center mr-4 p-2 rounded-lg ${isSelected ? 'opacity-100' : 'opacity-60'}`}
                    >
                        <Image
                            // source={item.avatar ? { uri: item.avatar } : require('../assets/images/react-logo.png')}
                            source={require('../assets/images/react-logo.png')}
                            className={`w-20 h-20 rounded-full bg-gray-200 ${isSelected ? 'border-2 border-blue-500' : ''}`}
                            resizeMode="cover"
                        />
                        <Text className="text-sm font-medium mt-2 text-gray-500 ">{item.name}</Text>
                        <Text className="text-xs text-gray-500">{item.age} yrs</Text>
                    </TouchableOpacity>
                )
            }}
        />
    )
}
