import { useRef, useEffect } from 'react';
import EventSource from 'react-native-sse';
import { API_BASE_URL } from '../types/chat';
import { useChatStore } from '../store/chatStore';
import 'react-native-get-random-values'; // Required for UUID to work in React Native
import { v4 as uuidv4 } from 'uuid';

export const useSSEConnection = () => {
  // Get state and actions from store
  const { 
    currentResponse,
    threadId: storeThreadId,
    appendToken,
    addCompleteMessage,
    addToolCallMessage,
    addToolOutputMessage,
    setIsLoading,
    setIsConnecting,
    setThreadId,
    setError
  } = useChatStore();
  
  // References
  const eventSourceRef = useRef<EventSource | null>(null);
  
  // Connection management
  const closeConnection = () => {
    if (!eventSourceRef.current) return;
    
    eventSourceRef.current.removeAllEventListeners();
    eventSourceRef.current.close();
    eventSourceRef.current = null;
  };
  
  const cancelConnection = () => {
    closeConnection();
    setIsLoading(false);
    setIsConnecting(false);
    
    if (currentResponse) {
      addCompleteMessage(currentResponse + ' [Cancelled]', 'assistant');
    }
  };

  
  const handleErrorEvent = (event: any) => {
    console.log('SSE error event received:', event);
    
    const errorMessage = 'error' in event && event.error ? String(event.error) :
                       'message' in event && event.message ? String(event.message) : 
                       'Connection error';
    
    handleError(errorMessage);
    closeConnection();
  };
  
  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setIsLoading(false);
    setIsConnecting(false);
  };



// Event handlers
  const handleOpenEvent = () => {
    console.log('SSE connection opened');
    setIsConnecting(false);
  };
  







  // workhorse
  const handleMessageEvent = (event: any) => {
    console.log('Raw SSE event received:', event);
    console.log('Raw SSE data:', event.data);
    if (!event.data) return;
    
    if (event.data === '[DONE]') {
      console.log('SSE stream completed with [DONE] signal');
      
      // Get the current value from the store directly
      const latestState = useChatStore.getState();
      if (latestState.currentResponse) {
        console.log('Adding complete message:', latestState.currentResponse);
        addCompleteMessage(latestState.currentResponse, 'assistant');
      }
      
      setIsLoading(false);
      setIsConnecting(false);
      closeConnection();
      return;
    }
    
    try {
      const data = JSON.parse(event.data);
      console.log('SSE parsed data:', data);
      setIsConnecting(false);
      
      type MessageType = 'token' | 'error' | 'message';
      
      const handlers: Record<MessageType, () => void> = {
        token: () => {
          console.log('SSE token received:', data.content);
          appendToken(data.content);
        },
        error: () => {
          console.log('SSE error message:', data.content);
          handleError(typeof data.content === 'string' ? data.content : 'An error occurred');
        },
        message: () => {
          const { content } = data;
          
          if (content.type === 'ai') {
            
            if (content.tool_calls?.length > 0) {
              console.log('SSE tool calls received:', content.tool_calls);
              
              // Process each tool call individually
              content.tool_calls.forEach((toolCall: any) => {
                console.log('Processing individual tool call:', toolCall);
                addToolCallMessage({
                  ...content,
                  tool_calls: [toolCall] // Pass single tool call in the expected format
                });
              });
            }
          } else if (content.type === 'tool') {
            console.log('SSE tool output received:', content);
            addToolOutputMessage(content);
          }
        }
      };
      
      const messageType = data.type as MessageType;
      const handler = handlers[messageType];
      if (handler) handler();
      
    } catch (error) {
      console.error('Error parsing message:', error);
      handleError('Error parsing server response');
    }
  };











  // Main function to start SSE connection
  const setupSSEConnection = (userContent: string) => {
    
    // Setup
    addCompleteMessage(userContent, 'user');
    setError(null);
    setIsLoading(true);
    setIsConnecting(true);
    closeConnection();
    
    try {
      // Create connection
      const url = new URL(`${API_BASE_URL}/stream`);
      
      // Get or generate thread_id
      let currentThreadId = useChatStore.getState().threadId;
      
      // Generate a new thread_id if none exists
      if (!currentThreadId) {
        currentThreadId = uuidv4();
        console.log('Generated new thread ID:', currentThreadId);
        setThreadId(currentThreadId);
      } else {
        console.log('Using existing thread ID:', currentThreadId);
      }
      
      const payload = {
        message: userContent,
        thread_id: currentThreadId,
        stream_tokens: true
      };
      
      const es = new EventSource(url.toString(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        pollingInterval: 0,
        debug: true,
      });
      
      eventSourceRef.current = es;
      
      // Attach event listeners
      es.addEventListener('open', handleOpenEvent);
      es.addEventListener('message', handleMessageEvent);
      es.addEventListener('error', handleErrorEvent);
      es.addEventListener('close', () => {});
      
    } catch (error) {
      console.error('Error setting up EventSource:', error);
      handleError('Failed to connect to the server');
    }
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return closeConnection;
  }, []);
  
  return {
    setupSSEConnection,
    cancelConnection
  };
}; 