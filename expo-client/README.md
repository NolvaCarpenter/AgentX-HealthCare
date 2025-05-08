# LangGraph Expo Client

A React Native Expo client that consumes the LangGraph FastAPI streaming service.

## Setup

1. Install dependencies:

```bash
npm install
```

2. Start the Expo development server:

```bash
npm start
```

3. Configure the API URL:

Before running the app, make sure to update the API URL in `services/api.ts` to point to your LangGraph server:

```typescript
// For Android emulator (default)
const API_BASE_URL = 'http://10.0.2.2:1500'; 

// For iOS simulator
// const API_BASE_URL = 'http://localhost:1500'; 

// For physical devices
// const API_BASE_URL = 'http://YOUR_COMPUTER_IP:1500';
```

## Running the app

1. Make sure the LangGraph server is running:

```bash
cd /path/to/minimal-langgraph-fastapi-streaming
# Start your server according to its documentation
```

2. Press:
   - `a` to open in an Android emulator
   - `i` to open in an iOS simulator
   - Or scan the QR code with the Expo Go app on your physical device

## Features

- Real-time streaming chat interface
- Token by token streaming responses
- Maintains a conversation thread
- Cancel ongoing requests
- Error handling with visual feedback
- Loading indicators

## Implementation Details

This client uses:

- `react-native-sse` for Server-Sent Events (SSE) communication
- `react-native-url-polyfill` for URL support 
- Expo & React Native for the UI
- TypeScript for type safety

### How it works

The application connects to the `/stream` endpoint of the LangGraph service using Server-Sent Events (SSE) with POST requests to receive real-time streaming responses from the AI.

The `react-native-sse` library allows sending POST requests with a JSON body to the streaming endpoint, which is not supported by the standard EventSource API.

# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## Get started

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the app

   ```bash
   npx expo start
   ```

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.
