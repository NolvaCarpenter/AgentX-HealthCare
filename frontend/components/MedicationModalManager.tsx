import { useState } from "react";
import { View, Text, ScrollView, Button, Modal, TextInput, TouchableOpacity } from "react-native";
import { v4 as uuidv4 } from 'uuid';
import { Medication, medicationField } from "@/types/patient"; // 경로는 프로젝트 구조에 맞게 조정

type FullMedication = Medication & {
  user_id: string;
  recorded_datetime: string;
};

// 초기값 생성 함수
const createEmptyForm = (): FullMedication => {
  const base = {} as Medication;
  for (const { key } of medicationField) base[key] = "";
  return {
    ...base,
    user_id: uuidv4() as string,
    recorded_datetime: new Date().toISOString(),
  };
};

export default function MedicationModalManager() {
  const [medications, setMedications] = useState<FullMedication[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<FullMedication>(createEmptyForm());

  const openModal = () => {
    setFormData(createEmptyForm());
    setShowModal(true);
  };

  const openEditModal = (med: FullMedication) => {
    setFormData(med);
    setShowModal(true);
  };


  const handleSave = () => {
    setMedications(prev => [...prev, formData]);
    setShowModal(false);
    setFormData(createEmptyForm());
  };

  return (
    <View className="flex-1 bg-gray-100">
      <ScrollView className="p-4">
       <View>
       {medications.map((med, index) => (
          <TouchableOpacity key={med.user_id} onPress={() => openEditModal(med)}>
            className="bg-blue-500 p-4 rounded-xl mt-6"
            
          
            <Text className="text-center text-white font-bold">Add Medication</Text>
          </TouchableOpacity>
          ))}

          {medications.map((med, index) => (
            <TouchableOpacity key={med.user_id} onPress={() => openEditModal(med)}>
              <View className="p-4 mb-2 bg-white rounded-xl shadow">
                <Text className="font-bold">{med.drug_name || "Unnamed Medication"}</Text>
                <Text className="text-gray-600">{med.pharmacy_name}</Text>
              </View>
            </TouchableOpacity>
          ))}

          <TouchableOpacity
            className="bg-blue-500 p-4 rounded-xl mt-6"
            onPress={openModal}
          >
            <Text className="text-center text-white font-bold">Add Medication</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      <Modal visible={showModal} transparent animationType="fade">
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView className="w-11/12 bg-white p-6 rounded-2xl max-h-[80%]" contentContainerStyle={{ paddingBottom: 30 }}>
            <Text className="text-2xl font-bold mb-4 text-center">Add New Medication</Text>

            {medicationField.map(({ label, key }) => (
              <View key={key} className="mb-3">
                <Text className="mb-1">{label}</Text>
                <TextInput
                  className="border rounded-lg p-2"
                  placeholder={`Enter ${label}`}
                  value={formData[key]}
                  onChangeText={(text) => setFormData({ ...formData, [key]: text })}
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
