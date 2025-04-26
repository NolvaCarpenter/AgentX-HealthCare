import React, { useState } from 'react'
import { View, Text, TouchableOpacity } from 'react-native'

interface AccordionItemProps {
  title: string
  children: React.ReactNode
}

export default function AccordionItem({ title, children }: AccordionItemProps) {
  // 아코디언의 펼침 상태를 관리하는 상태입니다. true일 때 내용이 펼쳐집니다.
  const [expanded, setExpanded] = useState(false)

  return (
    <View className="mb-2 border rounded-lg overflow-hidden">
      {/* 아코디언 헤더 부분입니다. 터치 시 펼치기/접기 동작을 토글합니다. */}
      <TouchableOpacity
        className="flex-row justify-between items-center p-4 bg-gray-100"
        onPress={() => setExpanded(!expanded)}
      >
        <Text className="text-lg font-medium">{title}</Text>
        <Text className="text-xl">{expanded ? '▲' : '▼'}</Text>
      </TouchableOpacity>
      {/* 펼쳐진 상태일 때만 세부 내용을 렌더링합니다. 세부 내용은 children으로 외부에서 주입됩니다. */}
      {expanded && (
        <View className="p-4 bg-gray-50">
          {children}
        </View>
      )}
    </View>
  )
}
