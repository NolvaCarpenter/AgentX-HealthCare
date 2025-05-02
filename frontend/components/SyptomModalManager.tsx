import { useState } from "react";
import { View, Text, ScrollView, Button, Modal, TextInput, TouchableOpacity } from "react-native";
import { v4 as uuidv4 } from 'uuid';
import { symptomDetailFields, type symptom_details } from "@/types/patient"; 
import { SymptomFields, type Symptom } from "@/types/patient";


type FullSymptom = symptom_details & Symptom & {
  user_id: string;
  recorded_datetime: string;
};

// 초기값 생성 함수
export const createEmptyForm = (): FullSymptom => {
  const base = {} as Partial<symptom_details>;

  for (const { key } of symptomDetailFields) {
    const defaultValue =
      key === "severity" ? 0 :
      ["characteristics", "triggers", "aggravating_factors", "relieving_factors", "associated_symptoms"].includes(key)
        ? []
        : "";

    (base[key] as any) = defaultValue;
  }

  return {
    ...(base as symptom_details),
    primary_symptoms: [],
    secondary_symptoms: [],
    symptom_details: {},
    user_id: uuidv4() as string,
    recorded_datetime: new Date().toISOString()
  };
};



export default function SymptomModalManager() {
  const [symptomMap, setSymptomMap] = useState<Record<string, FullSymptom>>({});
  const [formData, setFormData] = useState<FullSymptom>(createEmptyForm());
  const [showModal, setShowModal] = useState(false);

  const openModal = () => {
    setFormData(createEmptyForm());
    setShowModal(true);
  };

  const openEditModal = (symptom: FullSymptom) => {
    setFormData(symptom);
    setShowModal(true);
  };

  const handleSave = () => {
    if (!formData.name.trim()) return;
  
    const { name, user_id, recorded_datetime, primary_symptoms, secondary_symptoms, symptom_details: _, ...details } = formData;
  
    const symptomToSave: Symptom = {
      primary_symptoms,
      secondary_symptoms,
      symptom_details: {
        [name]: {
          ...(details as symptom_details) // symptom_details만 따로 추출
        }
      }
    };
  
    setSymptomMap(prev => ({
      ...prev,
      [name]: {
        ...symptomToSave.symptom_details[name],
        user_id,
        recorded_datetime,
        ...symptomToSave // 추가 메타정보
      }
    }));
  
    setShowModal(false);
  };

  // 간단히 comma-separated 필드 처리
  const handleTextInputChange = (key: keyof FullSymptom, text: string) => {
    const value = Array.isArray(formData[key])
      ? text.split(",").map(s => s.trim()) // 배열 처리
      : key === "severity"
        ? Number(text)
        : text;

    setFormData(prev => ({ ...prev, [key]: value as any }));
  };

  return (
    <View className="flex-1 bg-gray-100">
      <ScrollView className="p-4">
        {Object.values(symptomMap).map((symptom) => (
          <TouchableOpacity key={symptom.name} onPress={() => openEditModal(symptom)}>
            <View className="p-4 mb-2 bg-white rounded-xl shadow">
              <Text className="font-bold">{symptom.name}</Text>
              <Text className="text-gray-600">{symptom.onset_description}</Text>
            </View>
          </TouchableOpacity>
        ))}

        <TouchableOpacity
          className="bg-green-500 p-4 rounded-xl mt-6"
          onPress={openModal}
        >
          <Text className="text-center text-white font-bold">Add Symptom</Text>
        </TouchableOpacity>
      </ScrollView>

      <Modal visible={showModal} transparent animationType="fade">
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView className="w-11/12 bg-white p-6 rounded-2xl max-h-[80%]" contentContainerStyle={{ paddingBottom: 30 }}>
            <Text className="text-2xl font-bold mb-4 text-center">Add Symptom</Text>

            {SymptomFields.map(({ label, key }) => {
                const typedKey = key as keyof FullSymptom;
                const value = formData[typedKey];

                return (
                  <View key={String(key)} className="mb-3">
                    <Text className="mb-1">{label}</Text>
                    <TextInput
                      className="border rounded-lg p-2"
                      placeholder={`Enter ${label}`}
                      value={
                        Array.isArray(value)
                          ? (value as string[]).join(", ")
                          : String(value)
                      }
                      onChangeText={(text) => handleTextInputChange(typedKey, text)}
                      keyboardType={typedKey === "severity" ? "numeric" : "default"}
                    />
                  </View>
                );
              })}

              <Text className="text-xl font-bold mb-2 mt-4">Symptom Detail</Text>
            {symptomDetailFields.map(({ label, key }) => {
                const typedKey = key as keyof FullSymptom;
                const value = formData[typedKey];

                return (
                  <View key={String(key)} className="mb-3">
                    <Text className="mb-1">{label}</Text>
                    <TextInput
                      className="border rounded-lg p-2"
                      placeholder={`Enter ${label}`}
                      value={
                        Array.isArray(value)
                          ? (value as string[]).join(", ")
                          : String(value)
                      }
                      onChangeText={(text) => handleTextInputChange(typedKey, text)}
                      keyboardType={typedKey === "severity" ? "numeric" : "default"}
                    />
                  </View>
                              );
              })}


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
