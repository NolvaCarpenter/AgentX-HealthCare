# Conversational AI Agent for Symptom Documentation 

This project implements a conversational AI agent that conducts interactive symptom documentation using structured memory. The agent collects and iteratively updates symptom details based on a predefined schema, guiding the user through a dynamic dialogue to fill in missing information.

## Participation in AgentX Challenge and Berkeley MOOC

This project is part of our submission to the [AgentX Challenge](https://rdi.berkeley.edu/agentx/), hosted by the [Berkeley Advanced Agentic AI MOOC](https://llmagents-learning.org/sp25). 


## Architecture

The system is built using Python with LangChain and LangGraph frameworks, and consists of the following components:


### Core Components

1. **SymptomState** (`symptom_state.py`): 
   - Manages the state of the conversation including primary symptoms, symptom details, and follow-up questions
   - Provides methods for adding symptoms, updating details, and identifying missing fields
   - Handles multi-symptom management and session summaries

2. **Conversation Agent** (`conversation_agent.py`):
   - Implements the main conversation flow as a LangGraph
   - Handles user input processing and agent response generation
   - Orchestrates the extraction and documentation of symptom details

3. **Thread Management System** (`conversation_thread.py`):
   - Tracks conversation threads with unique thread IDs
   - Maintains persistent conversation history in SQLite database
   - Allows users to switch between multiple conversation sessions
   - Supports retrieving past conversations and continuing them seamlessly

4. **Extraction System**:
   - `symptom_extraction.py`: Extracts primary symptoms and details from user messages
   - `medication_extraction.py`: Processes medication information from uploaded images

5. **User Interfaces**:
   - Command-line interface (`main.py`)
   - Web interface using Gradio (`main_gradio.py`)
   - Both interfaces support thread management for persistent conversations

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

1. Run `python main.py` to start the command-line interface
2. Interact with the agent by describing your symptoms
3. Use special commands:
   - Type `exit`, `quit`, or `bye` to end the conversation
   - Type `threads` to list active conversation threads
   - Type `thread <thread_id>` to switch to a specific thread
   - Type `summary` to get a summary of documented symptoms
   - Type `voice` to process a voice conversation file

### Web Interface

1. Run `python main_gradio.py` to start the web interface
2. Access the interface at http://127.0.0.1:7860
3. Use the conversation panel to interact with the agent
4. Features:
   - View current symptoms in the right panel
   - Start a new conversation with the "New Conversation" button
   - Select previous threads from the dropdown menu
   - View thread information including creation time and message count

## Requirements

- Python 3.8+
- Required packages listed in `requirements.txt`
- OpenAI API key (set as an environment variable `OPENAI_API_KEY`)

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your OpenAI API key as an environment variable
4. Run the application using one of the interfaces described above
