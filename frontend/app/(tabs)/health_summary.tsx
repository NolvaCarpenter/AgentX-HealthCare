// app/health_summary.tsx
import React from 'react';
import { View, Text } from 'react-native';
import PastHistorySummary from '@/components/PastHistorySummary';
import CurrentStatusSummary from '@/components/CurrentStatusSummary';

export default function HealthSummaryTab() {
  return (
    <View className="flex-1 bg-white">
      <PastHistorySummary />
      <CurrentStatusSummary />
    </View>
  );
}