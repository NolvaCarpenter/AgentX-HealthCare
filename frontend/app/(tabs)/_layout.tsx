import { Tabs } from 'expo-router'
import { Bot, ClipboardList, Activity, Stethoscope } from 'lucide-react-native'

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
        name="medical_record"
        options={{
          title: 'record',
          tabBarIcon: ({ color, size }) => <Stethoscope size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="health_summary"
        options={{
          title: 'summary',
          tabBarIcon: ({ color, size }) => <ClipboardList size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="index"
        options={{
          href: null
        }}
      />

    </Tabs>
  )
}