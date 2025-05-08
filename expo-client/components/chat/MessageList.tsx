import React, { forwardRef } from 'react';
import { StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { ThemedText } from '../ThemedText';
import { ThemedView } from '../ThemedView';
import { useChatStore } from '../../store/chatStore';
import { MessageBubble } from './MessageBubble';

// We still accept props for ScrollView ref forwarding
interface MessageListProps {
  messages?: any[]; // Made optional since we get from store
  currentResponse?: string; // Made optional since we get from store
  isConnecting?: boolean; // Made optional since we get from store
  error?: string | null; // Made optional since we get from store
}

export const MessageList = forwardRef<ScrollView, MessageListProps>(
  (props, ref) => {
    // Get state from store
    const { 
      messages: storeMessages, 
      currentResponse: storeCurrentResponse,
      isConnecting: storeIsConnecting,
      error: storeError 
    } = useChatStore();
    
    // Use props if provided, otherwise use store values
    // This allows for flexibility and backwards compatibility
    const messages = props.messages || storeMessages;
    const currentResponse = props.currentResponse || storeCurrentResponse;
    const isConnecting = props.isConnecting || storeIsConnecting;
    const error = props.error || storeError;
    
    return (
      <ScrollView
        ref={ref}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}>
        {/* Empty state */}
        {messages.length === 0 && !currentResponse && !isConnecting && !error && (
          <ThemedView style={styles.emptyState}>
            <ThemedText style={styles.emptyStateText}>
              Start a conversation with the AI assistant...
            </ThemedText>
          </ThemedView>
        )}
        
        {/* Message bubbles */}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {/* Connecting indicator */}
        {isConnecting && (
          <ThemedView style={[styles.messageBubble, styles.assistantBubble]}>
            <ActivityIndicator size="small" color="#007AFF" />
            <ThemedText style={{marginTop: 4}}>Connecting...</ThemedText>
          </ThemedView>
        )}
        
        {/* Current response being streamed */}
        {currentResponse && (
          <ThemedView style={[styles.messageBubble, styles.assistantBubble, styles.streamingBubble]}>
            <ThemedText selectable>{currentResponse}</ThemedText>
          </ThemedView>
        )}
        
        {/* Error message */}
        {error && (
          <ThemedView style={[styles.messageBubble, styles.errorBubble]}>
            <ThemedText style={styles.errorText}>{error}</ThemedText>
          </ThemedView>
        )}
      </ScrollView>
    );
  }
);

MessageList.displayName = 'MessageList';

const styles = StyleSheet.create({
  messagesContainer: {
    flex: 1,
    padding: 10,
  },
  messagesContent: {
    paddingBottom: 10,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    opacity: 0.5,
  },
  emptyStateText: {
    textAlign: 'center',
  },
  messageBubble: {
    padding: 12,
    borderRadius: 18,
    marginVertical: 5,
    maxWidth: '80%',
  },
  streamingBubble: {
    borderWidth: 1,
    borderColor: '#4F8EF7',
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#E5E5EA',
  },
  errorBubble: {
    alignSelf: 'center',
    backgroundColor: '#FFE5E5',
    marginVertical: 10,
  },
  errorText: {
    color: '#FF6B6B',
  },
}); 