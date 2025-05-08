import React from 'react';
import { StyleSheet, View } from 'react-native';
import { ThemedText } from '../ThemedText';
import { ThemedView } from '../ThemedView';
import { Message } from '../../types/chat';

interface ToolOutputBubbleProps {
  message: Message;
}

export const ToolOutputBubble = ({ message }: ToolOutputBubbleProps) => {
  return (
    <ThemedView style={styles.container}>
      <View style={styles.header}>
        <ThemedText style={styles.toolName}>📊 Tool Result</ThemedText>
      </View>
      <View style={styles.content}>
        <ThemedView style={styles.resultContainer}>
          <ThemedText selectable style={styles.result}>
            {message.toolData?.result || message.content || 'No result data'}
          </ThemedText>
        </ThemedView>
      </View>
    </ThemedView>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 12,
    borderRadius: 12,
    marginVertical: 5,
    maxWidth: '90%',
    alignSelf: 'flex-start',
    backgroundColor: '#F0F9ED',
    borderWidth: 1,
    borderColor: '#C8E6C9',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    marginBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#D5E8D6',
    paddingBottom: 8,
  },
  toolName: {
    fontWeight: 'bold',
    color: '#43A047',
  },
  content: {
    marginTop: 4,
  },
  resultContainer: {
    backgroundColor: '#F8FFF5',
    padding: 8,
    borderRadius: 6,
  },
  result: {
    fontSize: 13,
  }
}); 