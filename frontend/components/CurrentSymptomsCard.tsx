// components/CurrentSymptomsCard.tsx
import { useState } from 'react';
import { View, Text, TouchableOpacity, Modal, ScrollView, Button } from 'react-native';
import { usePatientStore } from '@/stores/usePatientStore';

export default function CurrentSymptomsCard() {
  const { patient } = usePatientStore();
  const [modalVisible, setModalVisible] = useState(false);

  const symptoms = patient?.symptoms ?? [];

  return (
    <View className="bg-white rounded-xl shadow p-4 border border-gray-200">
      {/* 카드 제목 클릭 시 모달 열기 */}
      <TouchableOpacity onPress={() => setModalVisible(true)} className="flex-row items-center justify-between">
        <Text className="text-lg font-bold">🩺 Current Symptoms</Text>
        <Text className="text-blue-500 text-sm">View All</Text>
      </TouchableOpacity>

      {/* 요약 미리보기 */}
      {symptoms.length > 0 && (
        <Text className="mt-2 text-sm text-gray-600 truncate">
          {symptoms.map(sym => sym.primary_symptoms?.[0]).filter(Boolean).join(', ')}
        </Text>
      )}

      {/* 모달 팝업 */}
      <Modal visible={modalVisible} animationType="slide" transparent>
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView className="bg-white w-11/12 p-4 rounded-xl max-h-[80%]">
            <Text className="text-xl font-bold mb-4 text-center">🩺 Current Symptoms</Text>

            {symptoms.length > 0 ? (
              symptoms.map((sym, index) => {
                const primary = sym.primary_symptoms?.[0];
                const detail = sym.symptom_details?.[primary];
                return (
                  <View key={index} className="border border-gray-200 rounded-lg p-3 mb-3">
                    <Text className="font-semibold text-base">{primary}</Text>
                    {detail?.severity !== undefined && (
                      <Text className="text-sm text-gray-700">Severity: {detail.severity}</Text>
                    )}
                    {detail?.onset_description && (
                      <Text className="text-sm text-gray-600 mt-1">{detail.onset_description}</Text>
                    )}
                  </View>
                );
              })
            ) : (
              <Text className="text-gray-500">No current symptoms recorded.</Text>
            )}

            <View className="mt-4">
              <Button title="Close" onPress={() => setModalVisible(false)} />
            </View>
          </ScrollView>
        </View>
      </Modal>
    </View>
  );
}
