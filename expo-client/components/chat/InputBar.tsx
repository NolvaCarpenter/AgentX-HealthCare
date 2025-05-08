import React from 'react';
import { StyleSheet, TextInput, View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { ThemedView } from '../ThemedView';
import { useChatStore } from '../../store/chatStore';
import { Ionicons } from '@expo/vector-icons';

interface InputBarProps {
  input: string;
  setInput: (input: string) => void;
  handleSend?: () => void;  // Made optional to allow direct store usage
  handleCancel?: () => void; // Made optional to allow direct store usage
  isLoading?: boolean; // Made optional since we can get from store
  onImageSelect?: () => void; // New prop for image selection
  hasAttachment?: boolean; // New prop to indicate if there's an attachment
}

export function InputBar({ 
  input, 
  setInput, 
  handleSend: propHandleSend, 
  handleCancel: propHandleCancel,
  isLoading: propIsLoading,
  onImageSelect,
  hasAttachment
}: InputBarProps) {
  // Get loading state and actions from store
  const { isLoading: storeIsLoading } = useChatStore();
  
  // Use provided props or fallback to store values
  const isLoading = propIsLoading !== undefined ? propIsLoading : storeIsLoading;
  
  return (
    <ThemedView style={styles.container}>
      <View style={styles.inputContainer}>
        <TouchableOpacity 
          style={styles.attachButton} 
          onPress={onImageSelect}
          disabled={isLoading}
        >
          <Ionicons 
            name={hasAttachment ? "image" : "image-outline"} 
            size={24} 
            color={hasAttachment ? "#4CD964" : "#007AFF"} 
          />
        </TouchableOpacity>

        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Type a message..."
          placeholderTextColor="#888"
          multiline
          returnKeyType="send"
          onSubmitEditing={propHandleSend}
          editable={!isLoading}
        />
        
        {isLoading ? (
          <TouchableOpacity style={styles.button} onPress={propHandleCancel}>
            <Ionicons name="stop-circle" size={24} color="#FF3B30" />
          </TouchableOpacity>
        ) : (
          <TouchableOpacity 
            style={styles.button} 
            onPress={propHandleSend}
            disabled={!input.trim() && !hasAttachment}
          >
            <Ionicons 
              name="send" 
              size={24} 
              color={(input.trim() || hasAttachment) ? "#007AFF" : "#C7C7CC"} 
            />
          </TouchableOpacity>
        )}
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 10,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#C7C7CC',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#C7C7CC',
    borderRadius: 18,
    padding: 10,
    paddingHorizontal: 15,
    maxHeight: 100,
    color: 'white',
  },
  button: {
    marginLeft: 10,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  attachButton: {
    marginRight: 10,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
}); 