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

2. **Symptom Extraction** (`symptom_extraction.py`):
   - Contains `SymptomExtractor` for identifying symptoms in user input
   - Contains `SymptomDetailExtractor` for extracting specific details about symptoms

3. **Conversation Agent** (`conversation_agent.py`):
   - Implements the conversation flow using LangGraph
   - Manages the state transitions between different actions (greeting, extracting symptoms, asking questions, etc.)
   - Processes user input and generates appropriate responses

4. **Symptom Reference** (`symptom_reference.py`):
   - Integrates with Mayo Clinic symptom reference data
   - Provides additional information about symptoms for enhanced responses

5. **Main Application** (`main.py`):
   - Provides a command-line interface for interacting with the agent
   - Handles the conversation loop and user input/output


