import React, { useEffect } from 'react';
import { View, Text, FlatList } from 'react-native';
import { usePatientStore } from '@/store/usePatientStore';
import { useFetchData } from '@/hooks/useFetchData';

const DataScreen = () => {
  const { medications } = usePatientStore();
  const { fetchMedications } = useFetchData();

  useEffect(() => {
    // Medications 데이터만 가져오도록 수정
    fetchMedications();
  }, []);

  return (
    <View style={{ padding: 16 }}>
      <Text style={{ fontSize: 20, fontWeight: 'bold', marginBottom: 10 }}>Medications:</Text>
      {medications.length > 0 ? (
        <FlatList
          data={medications}
          keyExtractor={(item) => item.user_id}
          renderItem={({ item }) => (
            <View style={{ marginBottom: 8, padding: 10, backgroundColor: '#f0f0f0', borderRadius: 5 }}>
              <Text style={{ fontSize: 16 }}>Drug Name: {item.drug_name}</Text>
              <Text>Strength: {item.drug_strength}</Text>
              <Text>Instructions: {item.drug_instructions}</Text>
              <Text>Pharmacy: {item.pharmacy_name}</Text>
              <Text>Prescriber: {item.prescriber_name}</Text>
              <Text>Refill Count: {item.refill_count}</Text>
              <Text>Filled Date: {item.filled_date}</Text>
            </View>
          )}
        />
      ) : (
        <Text style={{ marginTop: 20, fontSize: 16 }}>No Medications Available</Text>
      )}
    </View>
  );
};

export default DataScreen;
