#!/usr/bin/env python3
# filepath: d:\VSCodeProjects\baymax_team_collab\langgraph_thread_direct.py

"""
A direct, simplified example of using thread_id with LangGraph configuration.

This demonstrates the pattern:
config = {"configurable": {"thread_id": "1"}}
output = graph.invoke({"messages": [input_message]}, config)
"""

import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from conversation_agent import conversation_graph, initialize_state, ConversationState
from symptoms.symptom_state import SymptomState
from medications.medication_state import MedicationProcessState

# Load environment variables
load_dotenv()


def main():
    """Example of direct thread_id usage with LangGraph"""
    print("LangGraph Thread ID Direct Example")
    print("================================\n")

    # Create a custom thread ID
    thread_id = "direct-example-thread-1"
    print(f"Using thread ID: {thread_id}")

    # Create the initial state using our helper function
    # This ensures all required objects are properly initialized
    state = initialize_state(configurable={"thread_id": thread_id})

    # Update with our specific values
    state.update(
        {
            "thread_id": thread_id,  # Directly set in the state
            "user_input": "I have a headache",
            "ai_response": "",
            "user_id": "default_user",
            "current_action": "chat",
            "chat_history": [],
            "extracted_symptoms": {},
            "extracted_medications": {},
            "missing_fields": [],
            "filename": "",
        }
    )

    # Create configuration exactly as mentioned in the prompt
    config = {"configurable": {"thread_id": thread_id}}
    print(f"Config: {config}")

    # Invoke the graph with the state and config
    print("\nInvoking graph with thread_id configuration...")
    output = conversation_graph.invoke(state, config)

    # Print results
    print(f"\nThread ID in result: {output['thread_id']}")
    print(f"AI response: {output['ai_response']}")

    # Continue with a follow-up question using the same thread_id
    print("\nContinuing conversation with same thread_id...")

    # Create the second input
    state2 = {**output, "user_input": "It's a throbbing pain behind my eyes"}

    # Use the same config with thread_id
    output2 = conversation_graph.invoke(state2, config)

    # Print results
    print(f"Thread ID in result: {output2['thread_id']}")
    print(f"User: It's a throbbing pain behind my eyes")
    print(f"AI response: {output2['ai_response']}")


if __name__ == "__main__":
    main()
