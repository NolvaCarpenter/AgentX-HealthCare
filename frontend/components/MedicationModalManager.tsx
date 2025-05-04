// components/MedicationModalManager.tsx
import { useState } from 'react';
import { View, Text, ScrollView, Button, Modal, TextInput, TouchableOpacity, Alert } from 'react-native';
import { usePatientStore } from '@/stores/usePatientStore';
import { medicationField } from '@/types/form/medicationField';

// 초기값 생성 함수
const createEmptyForm = (): any => {
  const base: any = {};
  for (const { key } of medicationField) base[key] = '';
  return base;
};

export default function MedicationModalManager() {
  const { patient, updateMedications } = usePatientStore();
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<any>(createEmptyForm());
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const medications = patient?.medications ?? [];

  const openEditModal = (index: number) => {
    setFormData(medications[index]);
    setEditingIndex(index);
    setShowModal(true);
  };

  const addNewMedication = () => {
    setFormData(createEmptyForm());
    setEditingIndex(null);
    setShowModal(true);
  };

  const handleSave = () => {
    const newMed = {
      ...formData,
      user_id: patient?.id ?? 'temp-user',
      recorded_datetime: new Date().toISOString(),
    };

    const updated = [...medications];
    if (editingIndex !== null) {
      updated[editingIndex] = newMed;
    } else {
      updated.push(newMed);
    }
    updateMedications(updated);
    setShowModal(false);
    setFormData(createEmptyForm());
    setEditingIndex(null);
  };

  const handleDelete = () => {
    if (editingIndex !== null) {
      Alert.alert('Delete Medication', 'Are you sure you want to delete this medication?', [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete', style: 'destructive', onPress: () => {
            const updated = medications.filter((_, idx) => idx !== editingIndex);
            updateMedications(updated);
            setShowModal(false);
            setFormData(createEmptyForm());
            setEditingIndex(null);
          }
        }
      ]);
    }
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

          <TouchableOpacity className="bg-blue-500 p-4 rounded-xl mt-6" onPress={addNewMedication}>
            <Text className="text-center text-white font-bold">Add Medication</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      <Modal visible={showModal} transparent animationType="fade">
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView className="w-11/12 bg-white p-6 rounded-2xl max-h-[80%]" contentContainerStyle={{ paddingBottom: 30 }}>
            <Text className="text-2xl font-bold mb-4 text-center">
              {editingIndex !== null ? 'Edit Medication' : 'Add New Medication'}
            </Text>

            {medicationField.map(({ label, key }) => (
              <View key={key} className="mb-3">
                <Text className="mb-1">{label}</Text>
                <TextInput
                  className="border rounded-lg p-2"
                  placeholder={`Enter ${label}`}
                  value={formData[key]?.toString() || ''}
                  onChangeText={(text) => setFormData((prev: any) => ({ ...prev, [key]: text }))}
                />
              </View>
            ))}
          </ScrollView>

          <View className="flex-row justify-between mt-6 gap-2">
            <Button title="Cancel" color="gray" onPress={() => setShowModal(false)} />
            {editingIndex !== null && <Button title="Delete" color="red" onPress={handleDelete} />}
            <Button title="Save" onPress={handleSave} />
          </View>
        </View>
      </Modal>
    </View>
  );
}

// import { useState } from 'react';
// import { View, Text, ScrollView, Button, Modal, TextInput, TouchableOpacity } from 'react-native';
// import { Medication } from '@/types/patient';
// import { medicationField } from '@/types/form/medicationField';
// import { usePatientStore } from '@/stores/usePatientStore';

// // 초기값 생성 함수
// const createEmptyForm = (): Medication => {
//   const base = {} as Medication;
//   for (const { key } of medicationField) base[key] = '';
//   return base;
// };

// export default function MedicationModalManager() {
//   const { patient, updateMedications } = usePatientStore();
//   const [showModal, setShowModal] = useState(false);
//   const [formData, setFormData] = useState<Medication>(createEmptyForm());
//   const [editingIndex, setEditingIndex] = useState<number | null>(null);

//   const medications = patient?.medications ?? [];

//   const openEditModal = (index: number) => {
//     setFormData(medications[index]);
//     setEditingIndex(index);
//     setShowModal(true);
//   };

//   const addNewMedication = () => {
//     const newMed = createEmptyForm();
//     setFormData(newMed);
//     setEditingIndex(null);
//     setShowModal(true);
//   };

//   const handleSave = () => {
//     const newMed: Medication = {
//       ...formData,
//       id: formData.id ?? `temp-${Date.now()}` // 서버에서 user_id를 부여할 예정이므로 임시 ID
//     };

//     const updated = [...medications];
//     if (editingIndex !== null) {
//       updated[editingIndex] = newMed;
//     } else {
//       updated.push(newMed);
//     }
//     updateMedications(updated);
//     setShowModal(false);
//     setFormData(createEmptyForm());
//     setEditingIndex(null);
//   };

//   return (
//     <View className="flex-1 bg-gray-100">
//       <ScrollView className="p-4">
//         <View>
//           {medications.map((med, index) => (
//             <TouchableOpacity key={med.id ?? index} onPress={() => openEditModal(index)}>
//               <View className="p-4 mb-2 bg-white rounded-xl shadow">
//                 <Text className="font-bold">{med.drug_name}</Text>
//                 <Text className="text-gray-600">{med.pharmacy_name}</Text>
//               </View>
//             </TouchableOpacity>
//           ))}

//           <TouchableOpacity className="bg-blue-500 p-4 rounded-xl mt-6" onPress={addNewMedication}>
//             <Text className="text-center text-white font-bold">Add Medication</Text>
//           </TouchableOpacity>
//         </View>
//       </ScrollView>

//       <Modal visible={showModal} transparent animationType="fade">
//         <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
//           <ScrollView className="w-11/12 bg-white p-6 rounded-2xl max-h-[80%]" contentContainerStyle={{ paddingBottom: 30 }}>
//             <Text className="text-2xl font-bold mb-4 text-center">
//               {editingIndex !== null ? 'Edit Medication' : 'Add New Medication'}
//             </Text>

//             {medicationField.map(({ label, key }) => (
//               <View key={key} className="mb-3">
//                 <Text className="mb-1">{label}</Text>
//                 <TextInput
//                   className="border rounded-lg p-2"
//                   placeholder={`Enter ${label}`}
//                   value={formData[key]}
//                   onChangeText={(text) => setFormData((prev) => ({ ...prev, [key]: text }))}
//                 />
//               </View>
//             ))}
//           </ScrollView>

//           <View className="flex-row justify-between mt-6">
//             <Button title="Cancel" color="red" onPress={() => setShowModal(false)} />
//             <Button title="Save" onPress={handleSave} />
//           </View>
//         </View>
//       </Modal>
//     </View>
//   );
// }