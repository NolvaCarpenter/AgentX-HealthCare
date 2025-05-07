// components/SymptomHistoryCard.tsx
import { useState } from 'react';
import { View, Text, TouchableOpacity, Modal, ScrollView, Button } from 'react-native';
import { usePatientStore } from '@/stores/usePatientStore';

export default function SymptomHistoryCard() {
  const { patient } = usePatientStore();
  const [modalVisible, setModalVisible] = useState(false);

  const pastSymptoms = patient?.past_symptoms ?? [];

  return (
    <View className="bg-white rounded-xl shadow p-4">
      {/* 카드 제목 클릭 시 모달 열기 */}
      <TouchableOpacity onPress={() => setModalVisible(true)}>
        <Text className="text-lg font-bold">🩺 Symptom History</Text>
      </TouchableOpacity>

      {/* 모달 팝업 */}
      <Modal visible={modalVisible} animationType="slide" transparent>
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView className="bg-white w-11/12 p-4 rounded-xl max-h-[80%]">
            <Text className="text-xl font-bold mb-4 text-center">🩺 Past Symptoms</Text>

            {pastSymptoms.length > 0 ? (
              pastSymptoms.map((sym, index) => (
                <View key={index} className="border border-gray-200 rounded-lg p-3 mb-3">
                  <Text className="font-semibold text-base">{sym.name}</Text>
                  {sym.severity !== undefined && (
                    <Text className="text-sm text-gray-700">Severity: {sym.severity}</Text>
                  )}
                  {sym.onset_description && (
                    <Text className="text-sm text-gray-600 mt-1">{sym.onset_description}</Text>
                  )}
                </View>
              ))
            ) : (
              <Text className="text-gray-500">No past symptoms recorded.</Text>
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
