#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
from conversation_agent import process_user_input
from conversation_thread import create_new_thread
from symptoms.voice_symptom_pipeline import (
    process_voice_input,
)

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main function to run the conversational AI agent."""
    print("Initializing symptom documentation agent...")

    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    state = None
    thread_id = None

    print("\n" + "=" * 50)
    print("Symptom Documentation Assistant")
    print("Type 'exit', 'quit', or 'bye' to end the conversation")
    print("Type 'summary' to get a summary of documented symptoms")
    print("Type 'voice' to transcribe and extract symptoms from an audio file")
    print("=" * 50 + "\n")

    # Create a new thread for this conversation
    thread_id = create_new_thread()
    print(f"Started new conversation thread: {thread_id}\n")

    # Initialize the conversation with the new thread
    response, state = process_user_input("", state, thread_id)
    print(f"\nAssistant: {response}\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using the AI Medical Assistant. Goodbye!")
            break

        if user_input.lower() == "voice":
            process_voice_input()
            continue

        response, state = process_user_input(user_input, state, thread_id)
        print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    main()
