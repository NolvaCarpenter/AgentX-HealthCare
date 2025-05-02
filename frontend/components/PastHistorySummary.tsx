// components/PastHistorySummary.tsx
import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { usePatientStore } from '@/stores/usePatientStore';

export default function PastHistorySummary() {
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
      <Text className="text-2xl font-bold text-center mb-6">📝 Past Medical History</Text>

      <Text className="text-xl font-semibold mt-4 mb-2">💊 Past Medications</Text>
      {patient.past_medications?.map((med) => (
        <View key={med.id} className="mb-2 p-3 border rounded-lg">
          <Text className="font-bold">{med.drug_name}</Text>
          <Text>Dosage: {med.dosage}</Text>
          {med.pharmacy_name && <Text>Pharmacy: {med.pharmacy_name}</Text>}
        </View>
      )) || <Text className="text-gray-500">No past medications recorded.</Text>}

      <Text className="text-xl font-semibold mt-6 mb-2">📋 Past Symptoms</Text>
      {patient.past_symptoms?.map((sym) => (
        <View key={sym.id} className="mb-2 p-3 border rounded-lg">
          <Text className="font-bold">{sym.name}</Text>
          {sym.severity !== undefined && <Text>Severity: {sym.severity}</Text>}
          {sym.onset_description && <Text>Description: {sym.onset_description}</Text>}
        </View>
      )) || <Text className="text-gray-500">No past symptoms recorded.</Text>}
    </ScrollView>
  );
}
