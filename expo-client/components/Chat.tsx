import React, { useRef, useEffect, useState } from 'react';
import { StyleSheet, KeyboardAvoidingView, ScrollView, Platform, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import 'react-native-url-polyfill/auto';

// Custom hooks
import { useSSEConnection } from '../hooks/useSSEConnection';
import { useChatStore } from '../store/chatStore';

// UI Components
import { MessageList } from './chat/MessageList';
import { InputBar } from './chat/InputBar';
import { ImageAttachment } from './chat/ImageAttachment';

export function Chat() {
  const [input, setInput] = React.useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  
  // Get state from store
  const { 
    messages, 
    currentResponse, 
    isConnecting,
    isLoading,
    error,
    setCurrentResponse,
    addCompleteMessage 
  } = useChatStore();
  
  // Get SSE connection methods
  const { setupSSEConnection, cancelConnection } = useSSEConnection();
  
  // Handle picking an image
  const handleImagePick = async () => {
    // Request permission if needed
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (status !== 'granted') {
      alert('Sorry, we need camera roll permissions to make this work!');
      return;
    }
    
    // Launch image picker
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });
    
    if (!result.canceled && result.assets && result.assets.length > 0) {
      setSelectedImage(result.assets[0].uri);
      // Scroll to bottom after image is selected
      setTimeout(() => scrollToBottom(), 100);
    }
  };
  
  // Remove selected image
  const removeSelectedImage = () => {
    setSelectedImage(null);
  };
  
  // Handle sending a message
  const handleSend = () => {
    if ((!input.trim() && !selectedImage) || isLoading) return;
    
    const userContent = input.trim();
    setInput('');
    
    // If there's an image, add it to the message
    if (selectedImage) {
      // Add user message with image
      const messageText = userContent ? userContent : '[Image attached]';
      
      // Add a custom message with image to the chat
      addCompleteMessage(messageText, 'user', selectedImage);
      
      // For AI response, we'll just tell it an image was attached
      const messageWithImageDescription = userContent 
        ? `${userContent} [Image attached]` 
        : '[Image attached]';
      
      setCurrentResponse('');
      setupSSEConnection(messageWithImageDescription);
      setSelectedImage(null);
    } else {
      // Regular text message
      setCurrentResponse('');
      setupSSEConnection(userContent);
    }
  };
  
  // Scroll to bottom helper function
  const scrollToBottom = () => {
    if (scrollViewRef.current) {
      scrollViewRef.current.scrollToEnd({ animated: true });
    }
  };
  
  // Scroll to bottom when messages change
  useEffect(() => {
    setTimeout(() => scrollToBottom(), 100);
  }, [messages, currentResponse, selectedImage]);
  
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={100}>
      
      {/* Messages area */}
      <MessageList 
        ref={scrollViewRef}
        messages={messages}
        currentResponse={currentResponse}
        isConnecting={isConnecting}
        error={error}
      />

      {/* Selected image preview */}
      {selectedImage && (
        <View style={styles.imagePreviewContainer}>
          <ImageAttachment 
            uri={selectedImage} 
            onRemove={removeSelectedImage} 
          />
        </View>
      )}

      {/* Input area */}
      <InputBar
        input={input}
        setInput={setInput}
        handleSend={handleSend}
        handleCancel={cancelConnection}
        isLoading={isLoading}
        onImageSelect={handleImagePick}
        hasAttachment={!!selectedImage}
      />
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  imagePreviewContainer: {
    padding: 10,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#C7C7CC',
  },
}); 