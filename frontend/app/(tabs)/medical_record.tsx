import React, { useState } from 'react'
import { ScrollView, Switch, Text, View } from 'react-native'
import { Patient } from '@/types/patient'
import SymptomModalManager from '@/components/SymptomModalManager'
import MedicationModalManager from '@/components/MedicationModalManager'

const medical_record = () => {

  return (
    <ScrollView className="flex-1 bg-gray-100">
      <View className="p-4">
        <Text className="text-3xl font-bold text-center text-gray-800 mb-8">medical record</Text>

        <View>
          <Text className="text-xl font-bold mb-4">Medications</Text>
          <MedicationModalManager />
        </View>

        <View>
          <Text className="text-xl font-bold mb-4">symptoms</Text>
          <SymptomModalManager />
        </View>

      </View>
    </ScrollView>
  )
}

export default medical_record
