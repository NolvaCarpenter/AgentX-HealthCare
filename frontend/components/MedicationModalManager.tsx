import { useState } from "react";
import { View, Text, ScrollView, Button, Modal, TextInput, TouchableOpacity } from "react-native";
import { Medication} from "@/types/patient";
import { medicationField } from "@/types/form/medicationField";

// 초기값 생성 함수
const createEmptyForm = (): Medication => {
  const base = {} as Medication;
  for (const { key } of medicationField) base[key] = "";
  return base;
};


export default function MedicationModalManager() {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<Medication>(createEmptyForm());
  const [editingIndex, setEditingIndex] = useState<number | null>(null); // 현재 편집 중인 인덱스


  // 기존 항목 편집 모달 열기
  const openEditModal = (index: number) => {
    setFormData(medications[index]);
    setEditingIndex(index);
    setShowModal(true);
  };


  // 새로운 항목 추가 + 편집 모달 열기
  const addNewMedication = () => {
    const newMed = createEmptyForm();
    setFormData(newMed);
    setEditingIndex(null); // 새 항목이므로 index 없음
    setShowModal(true);
  };


  // 저장 버튼
  const handleSave = () => {
    if (editingIndex !== null) {
      // 기존 항목 수정
      setMedications(prev => prev.map((med, idx) => idx === editingIndex ? formData : med));
    } else {
      // 새 항목 추가
      setMedications(prev => [...prev, formData]);
    }
    setShowModal(false);
    setFormData(createEmptyForm());
    setEditingIndex(null);
  };


  return (
    <View className="flex-1 bg-gray-100">
      <ScrollView className="p-4">
        <View>
          {medications.map((med, index) => (
            <TouchableOpacity key={index} onPress={() => openEditModal(index)}>
              <View className="p-4 mb-2 bg-white rounded-xl shadow">
                <Text className="font-bold">{med.drug_name}</Text>
                <Text className="text-gray-600">{med.pharmacy_name}</Text>
              </View>
            </TouchableOpacity>
          ))}


          <TouchableOpacity
            className="bg-blue-500 p-4 rounded-xl mt-6"
            onPress={addNewMedication}
          >
            <Text className="text-center text-white font-bold">Add Medication</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>


      <Modal visible={showModal} transparent animationType="fade">
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView className="w-11/12 bg-white p-6 rounded-2xl max-h-[80%]" contentContainerStyle={{ paddingBottom: 30 }}>
            <Text className="text-2xl font-bold mb-4 text-center">
              {editingIndex !== null ? "Edit Medication" : "Add New Medication"}
            </Text>


            {medicationField.map(({ label, key }) => (
              <View key={key} className="mb-3">
                <Text className="mb-1">{label}</Text>
                <TextInput
                  className="border rounded-lg p-2"
                  placeholder={`Enter ${label}`}
                  value={formData[key]}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, [key]: text }))}
                />
              </View>
            ))}
          </ScrollView>


          <View className="flex-row justify-between mt-6">
            <Button title="Cancel" color="red" onPress={() => setShowModal(false)} />
            <Button title="Save" onPress={handleSave} />
          </View>
        </View>
      </Modal>
    </View>
  );
}
