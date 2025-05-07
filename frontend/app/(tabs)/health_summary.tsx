// app/health_summary.tsx
import React from 'react';
import { View, ScrollView } from 'react-native';
import HighlightOverviewCard from '@/components/HighlightOverviewCard';
import SymptomHistoryCard from '@/components/SymptomHistoryCard';
import MedicationHistoryCard from '@/components/MedicationHistoryCard';
import CurrentSymptomsCard from '@/components/CurrentSymptomsCard';
import CurrentMedicationsCard from '@/components/CurrentMedicationsCard';

export default function HealthSummaryTab() {
  return (
    <ScrollView className="flex-1 bg-gray-50 px-4 pt-4">
      <View className="flex-1 bg-gray-50 border-b border-gray-300 shadow-sm p-4">
        <HighlightOverviewCard />
      </View>

      <View className="flex-row flex-wrap justify-between mt-4">
        <View className="w-[48%] mb-4">
          <CurrentMedicationsCard />
        </View>
        <View className="w-[48%] mb-4">
          <CurrentSymptomsCard />
        </View>
        <View className="w-[48%] mb-4">
          <MedicationHistoryCard />
        </View>
        <View className="w-[48%] mb-4">
          <SymptomHistoryCard />
        </View>
      </View>
    </ScrollView>
  );
}