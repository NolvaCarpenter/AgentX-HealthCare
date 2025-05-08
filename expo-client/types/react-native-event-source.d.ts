declare module 'react-native-event-source' {
  interface EventSourceInit {
    headers?: Record<string, string>;
    method?: string;
    body?: string;
  }

  interface EventSourceEvent {
    data: string;
    type: string;
    lastEventId: string;
    origin: string;
  }

  type EventSourceListener = (event: EventSourceEvent) => void;

  export class EventSourcePolyfill {
    constructor(url: string, init?: EventSourceInit);
    
    close(): void;
    
    addEventListener(type: string, listener: EventSourceListener): void;
    removeEventListener(type: string, listener: EventSourceListener): void;
    
    onerror: (error: any) => void;
    onmessage: EventSourceListener;
  }
} 