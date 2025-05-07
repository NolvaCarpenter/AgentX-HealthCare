// components/CurrentMedicationsCard.tsx
import { useState } from 'react';
import { View, Text, TouchableOpacity, Modal, ScrollView, Button } from 'react-native';
import { usePatientStore } from '@/stores/usePatientStore';

export default function CurrentMedicationsCard() {
  const { patient } = usePatientStore();
  const [modalVisible, setModalVisible] = useState(false);

  const medications = patient?.medications ?? [];

  return (
    <View className="bg-white rounded-xl shadow p-4 border border-gray-200">
      {/* 카드 제목 클릭 시 모달 열기 */}
      <TouchableOpacity onPress={() => setModalVisible(true)} className="flex-row items-center justify-between">
        <Text className="text-lg font-bold">💊 Current Medications</Text>
        <Text className="text-blue-500 text-sm">View All</Text>
      </TouchableOpacity>

      {/* 요약 미리보기 */}
      {medications.length > 0 && (
        <Text className="mt-2 text-sm text-gray-600 truncate">
          {medications.map(med => med.drug_name).join(', ')}
        </Text>
      )}

      {/* 모달 팝업 */}
      <Modal visible={modalVisible} animationType="slide" transparent>
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView className="bg-white w-11/12 p-4 rounded-xl max-h-[80%]">
            <Text className="text-xl font-bold mb-4 text-center">💊 Current Medications</Text>

            {medications.length > 0 ? (
              medications.map((med, index) => (
                <View key={index} className="border border-gray-200 rounded-lg p-3 mb-3">
                  <Text className="font-semibold text-base">{med.drug_name}</Text>
                  {med.drug_strength && (
                    <Text className="text-sm text-gray-700">Dosage: {med.drug_strength}</Text>
                  )}
                  {med.pharmacy_name && (
                    <Text className="text-sm text-gray-600 mt-1">Pharmacy: {med.pharmacy_name}</Text>
                  )}
                </View>
              ))
            ) : (
              <Text className="text-gray-500">No current medications recorded.</Text>
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
