import { create } from 'zustand';
import { nanoid } from 'nanoid/non-secure';
import { Message } from '../types/chat';

interface ChatState {
  // State
  messages: Message[];
  currentResponse: string;
  isLoading: boolean;
  isConnecting: boolean;
  threadId: string | undefined;
  error: string | null;
  
  // Message handling actions
  setCurrentResponse: (response: string) => void;
  appendToken: (token: string) => void;
  addCompleteMessage: (content: string, type: 'user' | 'assistant', imageUri?: string) => void;
  addToolCallMessage: (toolCall: any) => void;
  addToolOutputMessage: (toolOutput: any) => void;
  
  // Connection actions
  setIsLoading: (isLoading: boolean) => void;
  setIsConnecting: (isConnecting: boolean) => void;
  setThreadId: (threadId: string | undefined) => void;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  // Initial state
  messages: [],
  currentResponse: '',
  isLoading: false,
  isConnecting: false,
  threadId: undefined,
  error: null,
  
  // Message handling actions
  setCurrentResponse: (response: string) => set({ currentResponse: response }),
  
  appendToken: (token: string) => 
    set((state) => ({ currentResponse: state.currentResponse + token })),
  
  addCompleteMessage: (content: string, type: 'user' | 'assistant', imageUri?: string) => {
    if (!content.trim() && !imageUri) return;
    
    set((state) => ({
      messages: [
        ...state.messages, 
        {
          id: nanoid(),
          content: content.trim(),
          type,
          imageUri
        }
      ],
      currentResponse: '',
    }));
  },
  
  addToolCallMessage: (toolCall: any) => {
    if (!toolCall || !toolCall.tool_calls || toolCall.tool_calls.length === 0) return;
    
    const toolCallData = toolCall.tool_calls[0];
    
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: nanoid(),
          content: `Tool call: ${toolCallData.name}`,
          type: 'tool_call',
          toolData: {
            name: toolCallData.name,
            args: toolCallData.args
          }
        }
      ]
    }));
  },
  
  addToolOutputMessage: (toolOutput: any) => {
    if (!toolOutput) return;
    
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: nanoid(),
          content: toolOutput.content || '',
          type: 'tool_output',
          toolData: {
            result: toolOutput.content
          }
        }
      ]
    }));
  },
  
  // Connection actions
  setIsLoading: (isLoading: boolean) => set({ isLoading }),
  setIsConnecting: (isConnecting: boolean) => set({ isConnecting }),
  setThreadId: (threadId: string | undefined) => set({ threadId }),
  setError: (error: string | null) => set({ error }),
})); 