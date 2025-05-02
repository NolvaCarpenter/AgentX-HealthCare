// components/CurrentStatusSummary.tsx
import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { usePatientStore } from '@/stores/usePatientStore';

export default function CurrentStatusSummary() {
  const { patient } = usePatientStore();

  if (!patient) {
    return (
      <View className="flex-1 justify-center items-center">
        <Text className="text-gray-500">No patient data available.</Text>
      </View>
    );
  }

  return (
    <ScrollView className="p-4 bg-white">
      <Text className="text-2xl font-bold text-center mb-6">📌 Current Medical Status</Text>

      <Text className="text-xl font-semibold mt-4 mb-2">💊 Current Medications</Text>
      {patient.medications.length > 0 ? (
        patient.medications.map((med) => (
          <View key={med.id} className="mb-2 p-3 border rounded-lg">
            <Text className="font-bold">{med.drug_name}</Text>
            <Text>Dosage: {med.dosage}</Text>
            {med.pharmacy_name && <Text>Pharmacy: {med.pharmacy_name}</Text>}
          </View>
        ))
      ) : (
        <Text className="text-gray-500">No current medications.</Text>
      )}

      <Text className="text-xl font-semibold mt-6 mb-2">🤒 Current Symptoms</Text>
      {patient.symptoms.length > 0 ? (
        patient.symptoms.map((sym) => (
          <View key={sym.id} className="mb-2 p-3 border rounded-lg">
            <Text className="font-bold">{sym.name}</Text>
            {sym.severity !== undefined && <Text>Severity: {sym.severity}</Text>}
            {sym.onset_description && <Text>Description: {sym.onset_description}</Text>}
          </View>
        ))
      ) : (
        <Text className="text-gray-500">No current symptoms.</Text>
      )}
    </ScrollView>
  );
}
