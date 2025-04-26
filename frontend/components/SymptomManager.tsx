import React, { useState } from 'react'
import { View, Text, TouchableOpacity, TextInput } from 'react-native'
import { Symptom } from '@/types/patient'
import AccordionItem from './AccordionItem'
// Props 타입 정의
interface SymptomManagerProps {
    symptoms: Symptom[]
    isEditing: boolean
    onChangeSymptoms: (newSymptoms: Symptom[]) => void
}

export default function SymptomManager({ symptoms, isEditing, onChangeSymptoms }: SymptomManagerProps) {
    // 증상 정보를 수정할 수 있도록 업데이트하는 함수입니다.
    const handleUpdateSymptom = (id: string, value: string) => {
        const updated = symptoms.map(sym =>
          sym.id === id ? { ...sym, description: value } : sym
        )
        onChangeSymptoms(updated)
      }
    
      return (
        <View className="p-4">
          <Text className="text-xl font-bold mb-4">Symptoms</Text>
          {symptoms.map((sym) => (
            <AccordionItem
              key={sym.id}
              title={sym.description}
            >
              {isEditing ? (
                <>
                  <Text className="text-base">Description:</Text>
                  <TextInput
                    value={sym.description}
                    onChangeText={(text) => handleUpdateSymptom(sym.id, text)}
                    className="border rounded px-3 py-2"
                  />
                </>
              ) : (
                <Text className="text-base">Description: {sym.description}</Text>
              )}
            </AccordionItem>
          ))}
    
          {/* 편집 모드에서 증상 추가 버튼 */}
          {isEditing && (
            <TouchableOpacity
              className="mt-4 p-4 bg-green-500 rounded-lg items-center"
              onPress={() => {
                const newSym = { id: Date.now().toString(), description: 'New Symptom' }
                onChangeSymptoms([...symptoms, newSym])
              }}
            >
              <Text className="text-white font-medium">+ Add Symptom</Text>
            </TouchableOpacity>
          )}
        </View>
      )
}
