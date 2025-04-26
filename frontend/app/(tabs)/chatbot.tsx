import React from 'react'
import { ScrollView, Text } from 'react-native'

const chatbot = () => {
  return (
    <ScrollView className="flex-1 p-4">
      <Text>MedicationChatbot</Text>
      {/* <MedicationChatbot
        healthData={healthData}
        updateHealthData={updateHealthData}
      /> */}
    </ScrollView>
  )
}

export default chatbot