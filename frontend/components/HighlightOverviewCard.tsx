// components/HighlightOverviewCard.tsx
import { View, Text } from 'react-native';
import { usePatientStore } from '@/stores/usePatientStore';

export default function HighlightOverviewCard() {
  const { patient } = usePatientStore();

  const symptomCount = patient?.symptoms?.length ?? 0;
  const medicationCount = patient?.medications?.length ?? 0;
  const severeSymptoms = patient?.symptoms?.filter(sym => {
    const primary = sym.primary_symptoms?.[0];
    return sym.symptom_details?.[primary]?.severity >= 7;
  }).length ?? 0;

  return (
    <View className="bg-white rounded-2xl shadow p-6 mb-6">
      {/* Patient Info */}
      <Text className="text-xl font-bold text-blue-800 mb-3">Patient Summary</Text>

      <View className="flex-row flex-wrap justify-between mb-4">
        <Text className="w-1/2 mb-1">👤 Name: {patient?.name}</Text>
        <Text className="w-1/2 mb-1">🎂 Age: {patient?.age}</Text>
        <Text className="w-1/2 mb-1">⚥ Gender: {patient?.gender}</Text>
        <Text className="w-1/2 mb-1">📏 Height: {patient?.height} cm</Text>
        <Text className="w-1/2 mb-1">⚖️ Weight: {patient?.weight} kg</Text>
      </View>

      {/* Tracking Overview */}
      <View className="border-t border-gray-200 pt-4 mt-2">
        <Text className="text-lg font-semibold text-gray-800 mb-2">📊 Tracking Overview</Text>
        <Text className="mb-1">🩺 Current Symptoms: {symptomCount}</Text>
        <Text className="mb-1">💊 Medications: {medicationCount}</Text>
        <Text className={`mb-1 ${severeSymptoms > 0 ? 'text-red-600 font-bold' : ''}`}>
          🚨 Severe Symptoms (7+): {severeSymptoms}
        </Text>
      </View>

      {/* Clinical Flags */}
      <View className="border-t border-gray-200 pt-4 mt-4">
        <Text className="text-lg font-semibold text-gray-800 mb-2">⚠️ Clinical Flags</Text>
        <Text className="mb-1">- Known Allergies: None reported</Text>
        <Text className="mb-1">- Key Conditions: Hypertension</Text>
        <Text>- Recent Hospitalization: 3 months ago</Text>
      </View>
    </View>
  );
}
