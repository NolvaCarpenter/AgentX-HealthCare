#!/usr/bin/env python3
# filepath: d:\VSCodeProjects\baymax_team_collab\test\langgraph_thread_example.py

"""
Example demonstrating how to use LangGraph thread_id configuration.
This shows a simplified approach to using thread_id directly with LangGraph.
"""

import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from conversation_agent import conversation_graph, initialize_state
from conversation_thread import create_new_thread, get_thread_history, save_message

# Load environment variables
load_dotenv()


def main():
    """Simple example of using LangGraph with thread_id"""
    print("LangGraph Thread ID Example")
    print("==========================\n")

    # Create a new thread in the database
    thread_id = create_new_thread()
    print(f"Created new thread: {thread_id}")

    # Method 1: Using LangGraph configuration directly
    print("\nMethod 1: Using LangGraph configuration")
    print("-------------------------------------")

    # Initialize state
    state = initialize_state()
    state["user_input"] = "I have a headache and sore throat"

    # Set up LangGraph configuration with thread_id
    langgraph_config = {"configurable": {"thread_id": thread_id}}

    # Invoke graph with configuration
    output = conversation_graph.invoke(state, langgraph_config)

    # Save the messages to the thread
    save_message(thread_id, "user", state["user_input"])
    save_message(thread_id, "assistant", output["ai_response"])

    print(f"Thread ID: {output['thread_id']}")
    print(f"Assistant: {output['ai_response']}")

    # Method 2: Pass multiple messages through the same thread
    print("\nMethod 2: Multiple messages with the same thread")
    print("----------------------------------------------")

    # First message
    user_input = "I've had these symptoms for 3 days now"
    state = {**output, "user_input": user_input}

    # Use the same configuration with the thread_id
    output = conversation_graph.invoke(state, langgraph_config)

    # Save the messages
    save_message(thread_id, "user", user_input)
    save_message(thread_id, "assistant", output["ai_response"])

    print(f"User: {user_input}")
    print(f"Assistant: {output['ai_response']}")

    # Second message
    user_input = "My temperature is 101 degrees"
    state = {**output, "user_input": user_input}

    # Same thread_id in configuration
    output = conversation_graph.invoke(state, langgraph_config)

    # Save the messages
    save_message(thread_id, "user", user_input)
    save_message(thread_id, "assistant", output["ai_response"])

    print(f"User: {user_input}")
    print(f"Assistant: {output['ai_response']}")

    # Retrieve thread history
    print("\nThread History:")
    print("--------------")
    history = get_thread_history(thread_id)
    for i, message in enumerate(history):
        role = message["role"].capitalize()
        content = message["content"]
        print(f"{i+1}. {role}: {content}")


if __name__ == "__main__":
    main()
