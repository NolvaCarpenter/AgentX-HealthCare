# Conversational AI Agent for Symptom Documentation 

This project implements a conversational AI agent that conducts interactive symptom documentation using structured memory. The agent collects and iteratively updates symptom details based on a predefined schema, guiding the user through a dynamic dialogue to fill in missing information.

## Project Structure

This project is organized into two main components:

- **baymax_team_collab/**: Backend Python application with the conversational AI agent
- **expo-client/**: Expo frontend application 

## Participation in AgentX Challenge and Berkeley MOOC

This project is part of our submission to the [AgentX Challenge](https://rdi.berkeley.edu/agentx/), hosted by the [Berkeley Advanced Agentic AI MOOC](https://llmagents-learning.org/sp25). 

## Architecture

The system is built using Python with LangChain and LangGraph frameworks, and consists of the following components:

### Core Components

1. **SymptomState** (`baymax_team_collab/symptom_state.py`): 
   - Manages the state of the conversation including primary symptoms, symptom details, and follow-up questions
   - Provides methods for adding symptoms, updating details, and identifying missing fields
   - Handles multi-symptom management and session summaries

2. **Conversation Agent** (`baymax_team_collab/conversation_agent.py`):
   - Implements the main conversation flow as a LangGraph
   - Handles user input processing and agent response generation
   - Orchestrates the extraction and documentation of symptom details

3. **Thread Management System** (`baymax_team_collab/conversation_thread.py`):
   - Tracks conversation threads with unique thread IDs
   - Maintains persistent conversation history in SQLite database
   - Allows users to switch between multiple conversation sessions
   - Supports retrieving past conversations and continuing them seamlessly

4. **Extraction System**:
   - `baymax_team_collab/symptom_extraction.py`: Extracts primary symptoms and details from user messages
   - `baymax_team_collab/medication_extraction.py`: Processes medication information from uploaded images

5. **User Interfaces**:
   - Command-line interface (`baymax_team_collab/main.py`)
   - Web interface using Gradio (`baymax_team_collab/main_gradio.py`)
   - Expo mobile application (`expo-client/`)
   - Both backend interfaces support thread management for persistent conversations

## Features

- **Structured Symptom Documentation**: Collects symptom details including severity, duration, location, and more
- **Multi-symptom Management**: Tracks multiple symptoms in a single session
- **Thread ID Tracking**: Maintains persistent conversation threads across sessions
- **Medication Label Processing**: Extracts medication information from uploaded images  
- **Voice Conversation Processing**: Extracts symptoms from transcribed patient-doctor conversations
- **Interactive Web Interface**: User-friendly Gradio interface with symptom tracking display
- **Thread Management**: Switch between different conversation threads or start new ones

## How to Use

### Command Line Interface

1. Run `make run` to start the command-line interface
2. Interact with the agent by describing your symptoms
3. Use special commands:
   - Type `exit`, `quit`, or `bye` to end the conversation
   - Type `threads` to list active conversation threads
   - Type `thread <thread_id>` to switch to a specific thread
   - Type `summary` to get a summary of documented symptoms
   - Type `voice` to process a voice conversation file

### Gradio Web Interface

1. Run `make gradio` to start the web interface
2. Access the interface at http://127.0.0.1:7860
3. Use the conversation panel to interact with the agent
4. Features:
   - View current symptoms in the right panel
   - Start a new conversation with the "New Conversation" button
   - Select previous threads from the dropdown menu
   - View thread information including creation time and message count

### Expo Frontend

1. Run `make expo` to start the Expo development server
2. Use the Expo Go app on your mobile device to connect to the development server
3. Alternatively, use an emulator to test the application

## Requirements

- Python 3.10+ (for backend)
- Poetry for dependency management (backend)
- Node.js and npm (for frontend)
- OpenAI API key (set as an environment variable `OPENAI_API_KEY`)

## Setup

1. Clone this repository
2. For the backend:
   - Navigate to the `baymax_team_collab` directory
   - Install dependencies using Poetry: `cd baymax_team_collab && poetry install`
   - Set up your OpenAI API key as an environment variable
3. For the frontend:
   - Navigate to the `expo-client` directory
   - Install dependencies: `cd expo-client && npm install`
4. Run the applications using the Makefile commands

## Makefile Commands

- `make run` - Run the CLI application
- `make gradio` - Run the Gradio web interface
- `make expo` - Run the Expo frontend



## Documents

The following documents provide detailed information about the project's architecture, data schema, and use cases:

1. [Data Schema](https://docs.google.com/document/d/1sBzSR1jdjC9XWkTIZaqrUFHMIwtgNfVxq3LY2ljImIs/edit?tab=t.0) - Defines the structured data format for symptom documentation

2. [AgentX-Health Kick-Off Meeting](https://docs.google.com/document/d/1eDQMryUz0kMzt4K9KkPQC3Ob2OLHeLvfEyREmZyHK1I/edit?tab=t.0) - Overview of the project's initial planning and goals

3. [Functionality of Components and Use Case Mapping](https://docs.google.com/document/d/1iXce2qyz664qGSdg08gIdYjVfgOmVt2yFk3YHXHGAIs/edit?tab=t.0) - Detailed breakdown of component functionality and use case implementation