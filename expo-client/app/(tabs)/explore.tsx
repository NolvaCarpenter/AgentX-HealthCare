import React, { useEffect } from 'react';
import { View, Text, Button, ActivityIndicator } from 'react-native';
import { useApi } from '@/hooks/useAPI';

export default function TabTwoScreen() {
  const { data, loading, error, fetchData } = useApi('ping');

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 20 }}>Ping Test</Text>
      {loading && <ActivityIndicator size="large" />}
      {error && <Text style={{ color: 'red' }}>Error: {error}</Text>}
      {data && <Text>Response: {data.message}</Text>}
      <Button title="Retry" onPress={fetchData} />
    </View>
  );
}