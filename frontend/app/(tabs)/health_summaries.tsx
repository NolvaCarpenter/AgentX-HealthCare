import { useState } from "react";
import { View, Text, ScrollView, Button, Modal, TextInput, TouchableOpacity } from "react-native";
import uuid from 'react-native-uuid'; 


export default function HealthSummaryScreen() {
  const [activeTab, setActiveTab] = useState<"medications" | "symptoms">("medications");
  const [medications, setMedications] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const openEditModal = (med: any) => {
    setFormData(med);  // 선택한 Medication 데이터를 formData에 그대로 넣는다
    setShowModal(true); // 모달을 연다
  };

  const [formData, setFormData] = useState({
    user_id: "",
    recorded_datetime: "",
    pharmacy_name: "",
    pharmacy_address: "",
    pharmacy_phone: "",
    patient_name: "",
    patient_address: "",
    drug_name: "",
    drug_strength: "",
    drug_instructions: "",
    pill_markings: "",
    manufacturer: "",
    ndc_upc: "",
    rx_written_date: "",
    discard_after: "",
    federal_caution: "",
    rx_number: "",
    refill_count: "",
    prescriber_name: "",
    reorder_after: "",
    qty_filled: "",
    location_code: "",
    filled_date: "",
    pharmacist: "",
    barcode: ""
  });

  

  const openModal = () => {
    setFormData({
      user_id: uuid.v4() as string,
      recorded_datetime: new Date().toISOString(),
      pharmacy_name: "",
      pharmacy_address: "",
      pharmacy_phone: "",
      patient_name: "",
      patient_address: "",
      drug_name: "",
      drug_strength: "",
      drug_instructions: "",
      pill_markings: "",
      manufacturer: "",
      ndc_upc: "",
      rx_written_date: "",
      discard_after: "",
      federal_caution: "",
      rx_number: "",
      refill_count: "",
      prescriber_name: "",
      reorder_after: "",
      qty_filled: "",
      location_code: "",
      filled_date: "",
      pharmacist: "",
      barcode: ""
    });
    setShowModal(true);
  };

  const handleSave = () => {
    setMedications([...medications, formData]);
    setShowModal(false);
    setFormData({ // 폼 초기화
      user_id: "",
      recorded_datetime: "",
      pharmacy_name: "",
      pharmacy_address: "",
      pharmacy_phone: "",
      patient_name: "",
      patient_address: "",
      drug_name: "",
      drug_strength: "",
      drug_instructions: "",
      pill_markings: "",
      manufacturer: "",
      ndc_upc: "",
      rx_written_date: "",
      discard_after: "",
      federal_caution: "",
      rx_number: "",
      refill_count: "",
      prescriber_name: "",
      reorder_after: "",
      qty_filled: "",
      location_code: "",
      filled_date: "",
      pharmacist: "",
      barcode: ""
    });
  };

  return (
    <View className="flex-1 bg-gray-100">
      {/* 탭 버튼 */}
      <View className="flex-row justify-center mt-4 space-x-4">
        <Button title="Medications" onPress={() => setActiveTab("medications")} />
        <Button title="Symptoms" onPress={() => setActiveTab("symptoms")} />
      </View>

      {/* 메인 내용 */}
      <ScrollView className="p-4">
        {activeTab === "medications" ? (
          <View>
            {medications.map((med, index) => (
              <TouchableOpacity onPress={() => openEditModal(med)}>
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
        ) : (
          <View>
            <Text className="text-center text-gray-500">Symptoms 관리 화면 (아직 구현 안 됨)</Text>
          </View>
        )}
      </ScrollView>

      {/* 모달 폼 */}
      <Modal visible={showModal} transparent={true} animationType="fade">
        <View className="flex-1 bg-black bg-opacity-50 justify-center items-center">
          <ScrollView className="w-11/12 bg-white p-6 rounded-2xl max-h-[80%]" contentContainerStyle={{ paddingBottom: 30 }}>
            <Text className="text-2xl font-bold mb-4 text-center">Add New Medication</Text>

            {/* 폼 항목들 */}
            {[
              { label: "Pharmacy Name", key: "pharmacy_name" },
              { label: "Pharmacy Address", key: "pharmacy_address" },
              { label: "Pharmacy Phone", key: "pharmacy_phone" },
              { label: "Patient Name", key: "patient_name" },
              { label: "Patient Address", key: "patient_address" },
              { label: "Drug Name", key: "drug_name" },
              { label: "Drug Strength", key: "drug_strength" },
              { label: "Drug Instructions", key: "drug_instructions" },
              { label: "Pill Markings", key: "pill_markings" },
              { label: "Manufacturer", key: "manufacturer" },
              { label: "NDC/UPC", key: "ndc_upc" },
              { label: "RX Written Date", key: "rx_written_date" },
              { label: "Discard After", key: "discard_after" },
              { label: "Federal Caution", key: "federal_caution" },
              { label: "RX Number", key: "rx_number" },
              { label: "Refill Count", key: "refill_count" },
              { label: "Prescriber Name", key: "prescriber_name" },
              { label: "Reorder After", key: "reorder_after" },
              { label: "Qty Filled", key: "qty_filled" },
              { label: "Location Code", key: "location_code" },
              { label: "Filled Date", key: "filled_date" },
              { label: "Pharmacist", key: "pharmacist" },
              { label: "Barcode", key: "barcode" }
            ].map(({ label, key }) => (
              <View key={key} className="mb-3">
                <Text className="mb-1">{label}</Text>
                <TextInput
                  className="border rounded-lg p-2"
                  placeholder={`Enter ${label}`}
                  value={formData[key as keyof typeof formData]}
                  onChangeText={(text) => setFormData({ ...formData, [key]: text })}
                />a
              </View>
            ))}

            

          </ScrollView>

          {/* 저장 버튼 */}
          <View className="flex-row justify-between mt-6">
              <Button title="Cancel" color="red" onPress={() => setShowModal(false)} />
              <Button title="Save" onPress={handleSave} />
            </View>
        </View>
      </Modal>
    </View>
  );
}
