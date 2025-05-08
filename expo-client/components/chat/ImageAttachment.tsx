import React from 'react';
import { View, Image, TouchableOpacity, StyleSheet, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface ImageAttachmentProps {
  uri: string;
  onRemove: () => void;
}

export const ImageAttachment: React.FC<ImageAttachmentProps> = ({ uri, onRemove }) => {
  return (
    <View style={styles.container}>
      <Image source={{ uri }} style={styles.image} />
      <TouchableOpacity style={styles.removeButton} onPress={onRemove}>
        <Ionicons name="close-circle" size={24} color="#fff" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 8,
    position: 'relative',
    alignSelf: 'center',
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 8,
  },
  removeButton: {
    position: 'absolute',
    top: -10,
    right: -10,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: 12,
  },
}); 