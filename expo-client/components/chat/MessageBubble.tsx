import React from 'react';
import { StyleSheet, Image, View } from 'react-native';
import { ThemedText } from '../ThemedText';
import { ThemedView } from '../ThemedView';
import { Message } from '../../types/chat';
import { ToolCallBubble } from './ToolCallBubble';
import { ToolOutputBubble } from './ToolOutputBubble';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  if (message.type === 'tool_call') {
    return <ToolCallBubble message={message} />;
  }
  
  if (message.type === 'tool_output') {
    return <ToolOutputBubble message={message} />;
  }
  
  return (
    <ThemedView 
      key={message.id} 
      style={[
        styles.messageBubble, 
        message.type === 'user' ? styles.userBubble : styles.assistantBubble
      ]}>
      <ThemedText selectable>{message.content}</ThemedText>
      
      {message.imageUri && (
        <View style={styles.imageContainer}>
          <Image 
            source={{ uri: message.imageUri }} 
            style={styles.image} 
            resizeMode="cover"
          />
        </View>
      )}
    </ThemedView>
  );
};

const styles = StyleSheet.create({
  messageBubble: {
    padding: 12,
    borderRadius: 18,
    marginVertical: 5,
    maxWidth: '80%',
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#DCF8C6',
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#E5E5EA',
  },
  imageContainer: {
    marginTop: 8,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 8,
  },
}); 