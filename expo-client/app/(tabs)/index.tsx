import { Image } from 'expo-image';
import { Platform, StyleSheet } from 'react-native';

import { Chat } from '@/components/Chat';
import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

export default function HomeScreen() {
  return (
    <ThemedView style={styles.container}>
      <ThemedView style={styles.header}>
        <ThemedText type="title">LangGraph Chat</ThemedText>
        <HelloWave />
      </ThemedView>
      
      <ThemedView style={styles.chatContainer}>
        <Chat />
      </ThemedView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  chatContainer: {
    flex: 1,
  },
});
