import React from 'react';
import { StyleSheet, View } from 'react-native';
import { ThemedText } from '../ThemedText';
import { ThemedView } from '../ThemedView';
import { Message } from '../../types/chat';

interface ToolCallBubbleProps {
  message: Message;
}

export const ToolCallBubble = ({ message }: ToolCallBubbleProps) => {
  return (
    <ThemedView style={styles.container}>
      <View style={styles.header}>
        <ThemedText style={styles.toolName}>🔧 Tool: {message.toolData?.name || 'Unknown'}</ThemedText>
      </View>
      <View style={styles.content}>
        <ThemedText style={styles.argsLabel}>Arguments:</ThemedText>
        <ThemedView style={styles.argsContainer}>
          <ThemedText style={styles.args}>
            {message.toolData?.args ? JSON.stringify(message.toolData.args, null, 2) : 'None'}
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
    backgroundColor: '#EBF6FF',
    borderWidth: 1,
    borderColor: '#B8E2FF',
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
    borderBottomColor: '#D0E8FF',
    paddingBottom: 8,
  },
  toolName: {
    fontWeight: 'bold',
    color: '#0070E0',
  },
  content: {
    marginTop: 4,
  },
  argsLabel: {
    fontWeight: 'bold',
    marginBottom: 4,
    fontSize: 12,
  },
  argsContainer: {
    backgroundColor: '#F8FBFF',
    padding: 8,
    borderRadius: 6,
  },
  args: {
    fontFamily: 'monospace',
    fontSize: 12,
  }
}); 