import { useState } from 'react';
import { View, Text, ScrollView, Button, Modal, TextInput, TouchableOpacity } from 'react-native';
import { Symptom } from '@/types/patient';
import { symptomField } from '@/types/form/symptomField';

// 초기값 생성 함수
const createEmptyForm = (): Symptom => {
  const base = {} as Symptom;
  for (const { key } of symptomField) base[key] = "";
  return base;
};

export default function SymptomModalManager() {
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<Symptom>(createEmptyForm());
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const openEditModal = (index: number) => {
    setFormData(symptoms[index]);
    setEditingIndex(index);
    setShowModal(true);
  };

  const addNewSymptom = () => {
    setFormData(createEmptyForm());
    setEditingIndex(null);
    setShowModal(true);
  };

  const handleSave = () => {
    if (editingIndex !== null) {
      setSymptoms((prev) => prev.map((sym, idx) => (idx === editingIndex ? formData : sym)));
    } else {
      setSymptoms((prev) => [...prev, formData]);
    }
    setShowModal(false);
    setFormData(createEmptyForm());
    setEditingIndex(null);
  };

  return (
    <View className="flex-1 bg-gray-100">
      <ScrollView className="p-4">
        <View>
          {symptoms.map((sym, index) => (
            <TouchableOpacity key={index} onPress={() => openEditModal(index)}>
              <View className="p-4 mb-2 bg-white rounded-xl shadow">
                <Text className="font-bold">{sym.name}</Text>
                <Text className="text-gray-600">Severity: {sym.severity}</Text>
              </View>
            </TouchableOpacity>
          ))}

          <TouchableOpacity className="bg-green-500 p-4 rounded-xl mt-6" onPress={addNewSymptom}>
            <Text className="text-center text-white font-bold">Add Symptom</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      <Modal visible={showModal} transparent animationType="fade">
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView
            className="w-11/12 bg-white p-6 rounded-2xl max-h-[80%]"
            contentContainerStyle={{ paddingBottom: 30 }}
          >
            <Text className="text-2xl font-bold mb-4 text-center">
              {editingIndex !== null ? 'Edit Symptom' : 'Add New Symptom'}
            </Text>

            {symptomField.map(({ label, key }) => (
              <View key={key} className="mb-3">
                <Text className="mb-1">{label}</Text>
                <TextInput
                  className="border rounded-lg p-2"
                  placeholder={`Enter ${label}`}
                  value={formData[key]?.toString() || ''}
                  onChangeText={(text) => setFormData((prev) => ({
                    ...prev,
                    [key]: key === 'severity' ? Number(text) : text,
                  }))}
                  keyboardType={key === 'severity' ? 'numeric' : 'default'}
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
