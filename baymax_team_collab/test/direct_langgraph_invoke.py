#!/usr/bin/env python3
# filepath: d:\VSCodeProjects\baymax_team_collab\direct_langgraph_invoke.py

"""
Direct LangGraph invoke example with thread_id configuration.
This demonstrates how to use thread_id from LangGraph configuration
as mentioned in the user prompt with:
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

# Load environment variables
load_dotenv()


def main():
    """Direct LangGraph invoke example with thread_id"""
    print("Direct LangGraph Thread ID Example")
    print("=================================\n")

    # Step 1: Create a simple input message
    input_message = "I have a headache and fever since yesterday"
    print(f"User input: {input_message}")

    # Step 2: Create a basic state
    state = initialize_state()
    state["user_input"] = (
        input_message  # Step 3: Create configuration with thread_id exactly as described in the prompt
    )
    # This is exactly the pattern requested: config = {"configurable": {"thread_id": "1"}}
    # Create a constant thread ID that's easily recognizable
    thread_id = "CUSTOM-THREAD-1234"
    print(f"Setting thread_id to: {thread_id}")

    # Update all possible places where thread_id might be read from
    config = {"configurable": {"thread_id": thread_id}}

    # Also update the module's config directly
    from conversation_agent import config as agent_config

    agent_config["configurable"]["thread_id"] = thread_id

    # Also set it in the state object directly
    state["thread_id"] = thread_id

    # Step 4: Invoke the graph with the state and config
    print("\nInvoking LangGraph with thread_id configuration...")
    output = conversation_graph.invoke(state, config)

    # Step 5: Display results
    print("\nResults:")
    print(f"Thread ID used: {output['thread_id']}")
    print(f"Assistant response: {output['ai_response']}")

    # Step 6: Continue the conversation with the same thread_id
    print("\nContinuing conversation with same thread_id...")

    # Update state with new input
    follow_up = "The pain is concentrated on my forehead"
    output["user_input"] = follow_up

    # Invoke again with the same configuration
    output = conversation_graph.invoke(output, config)

    print(f"User: {follow_up}")
    print(f"Assistant: {output['ai_response']}")


if __name__ == "__main__":
    main()
