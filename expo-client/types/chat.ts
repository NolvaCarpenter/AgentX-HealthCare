// Chat message interface
export interface Message {
  id: string;
  content: string;
  type: 'user' | 'assistant' | 'tool_call' | 'tool_output';
  toolData?: {
    name?: string;
    args?: any;
    result?: string;
  };
  imageUri?: string; // Add support for image attachments
}

// Server API configuration
export const API_BASE_URL = 'http://127.0.0.1:1500'; 