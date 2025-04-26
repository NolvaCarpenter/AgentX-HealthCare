import { Tabs } from 'expo-router'
import { Bot, ClipboardList } from 'lucide-react-native'

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerShown: false }}>
      <Tabs.Screen
        name="chatbot"
        options={{
          title: 'Chatbot',
          tabBarIcon: ({ color, size }) => <Bot size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="health_summaries"
        options={{
          title: 'Summaries',
          tabBarIcon: ({ color, size }) => <ClipboardList size={size} color={color} />,
        }}
      />
    </Tabs>
  )
}