#!/usr/bin/env python3

import os
import sys
import json
from typing import Dict, Any, Optional

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from symptom_state import SymptomState
from symptom_extraction import SymptomExtractor, SymptomDetailExtractor
from conversation_agent import process_user_input, initialize_state, display_workflow
from symptom_reference import SymptomReferenceData

def main():
    """Main function to run the conversational AI agent."""
    print("Initializing symptom documentation agent...")
    
    # Check for OpenAI API key
    if "OPENAI_API_KEY" not in os.environ:        
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    # Initialize symptom reference data
    print("Loading symptom reference data...")
    symptom_reference = SymptomReferenceData()
    
    # Initialize conversation state
    state = None
    
    print("\n" + "="*50)
    print("Symptom Documentation Assistant")
    print("Type 'exit', 'quit', or 'bye' to end the conversation")
    print("Type 'summary' to get a summary of documented symptoms")
    print("="*50 + "\n")
    
    # Get initial greeting
    response, state = process_user_input("", None)
    print(f"Assistant: {response}\n")
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using the AI Medical Assistant. Goodbye!")
            break
        
        # Process user input
        response, state = process_user_input(user_input, state)
        
        # Print response
        print(f"\nAssistant: {response}\n")
        
        # If new symptoms were added, try to fetch reference information
        if state and hasattr(state, "symptom_state"):
            symptom_state = state["symptom_state"]
            for symptom in symptom_state.primary_symptoms:
                # Check if we already have reference data for this symptom
                if not hasattr(symptom_state, "reference_data"):
                    symptom_state.reference_data = {}
                
                if symptom not in symptom_state.reference_data:
                    try:
                        # Get reference data in the background
                        symptom_info = symptom_reference.get_symptom_info(symptom)
                        symptom_state.reference_data[symptom] = symptom_info
                    except Exception as e:
                        print(f"Error fetching reference data for {symptom}: {e}")

if __name__ == "__main__":
    main()
