// import React, { useState } from 'react'
// import { View, Text, TouchableOpacity, TextInput } from 'react-native'
// import { Symptom } from '@/types/patient'
// import AccordionItem from './AccordionItem'
// // Props type definition
// interface SymptomManagerProps {
//   symptoms: Symptom[]
//   isEditing: boolean
//   onChangeSymptoms: (newSymptoms: Symptom[]) => void
// }

// export default function SymptomManager({ symptoms, isEditing, onChangeSymptoms }: SymptomManagerProps) {
//   //Function to update symptom information
//   const handleUpdateSymptom = (id: string, value: string) => {
//     const updated = symptoms.map(sym =>
//       sym.id === id ? { ...sym, description: value } : sym
//     )
//     onChangeSymptoms(updated)
//   }

//   return (
//     <View className="p-4">
//       <Text className="text-xl font-bold mb-4">Symptoms</Text>
//       {symptoms.map((sym) => (
//         <AccordionItem
//           key={sym.id}
//           title={sym.description}
//         >
//           {/*Delete Item */}
//           {isEditing && (
//             <TouchableOpacity
//               className="self-end mb-2 bg-red-500 px-3 py-1 rounded"
//               onPress={() => {
//                 const updated = symptoms.filter((s) => s.id !== sym.id)
//                 onChangeSymptoms(updated)
//               }}
//             >
//               <Text className="text-white">Delete</Text>
//             </TouchableOpacity>
//           )}

//           {isEditing ? (
//             <>
//               <Text className="text-base">Description:</Text>
//               <TextInput
//                 value={sym.description}
//                 onChangeText={(text) => handleUpdateSymptom(sym.id, text)}
//                 className="border rounded px-3 py-2"
//               />
//             </>
//           ) : (
//             <Text className="text-base">Description: {sym.description}</Text>
//           )}
//         </AccordionItem>
//       ))}

//       {/* add symptom buttom */}
//       {isEditing && (
//         <TouchableOpacity
//           className="mt-4 p-4 bg-green-500 rounded-lg items-center"
//           onPress={() => {
//             const newSym = { id: Date.now().toString(), description: 'New Symptom' }
//             onChangeSymptoms([...symptoms, newSym])
//           }}
//         >
//           <Text className="text-white font-medium">+ Add Symptom</Text>
//         </TouchableOpacity>
//       )}
//     </View>
//   )
// }
