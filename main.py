#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversation_agent import process_user_input

# ✅ Import voice feature (modular)
from symptoms.voice_symptom_pipeline import (
    process_audio_to_symptoms_and_summary,
    store_results_in_sqlite,
    list_audio_files_for_patient,
)


def main():
    """Main function to run the conversational AI agent."""
    print("Initializing symptom documentation agent...")

    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    state = None

    print("\n" + "=" * 50)
    print("Symptom Documentation Assistant")
    print("Type 'exit', 'quit', or 'bye' to end the conversation")
    print("Type 'summary' to get a summary of documented symptoms")
    print("Type 'voice' to transcribe and extract symptoms from an audio file")
    print("=" * 50 + "\n")

    response, state = process_user_input("", state)
    print(f"Assistant: {response}\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using the AI Medical Assistant. Goodbye!")
            break

        if user_input.lower() == "voice":
            patient_id = input("Enter Patient ID (e.g., default: CAR0001): ").strip()
            patient_id = "CAR0001" if not patient_id else patient_id
            files = list_audio_files_for_patient(patient_id)

            if not files:
                print(f"❌ No audio files found for patient ID {patient_id}.")
                continue

            print("\n🎧 Available Audio Files:")
            for i, f in enumerate(files, 1):
                print(f"{i}. {f}")
            try:
                choice = int(input("Select file number to process: ").strip())
                selected_file = files[choice - 1]
            except (ValueError, IndexError):
                print("❌ Invalid selection.")
                continue

            print(f"🔊 Processing {selected_file}...")
            audio_path = os.path.join("data", "patient_conversations", selected_file)
            results = process_audio_to_symptoms_and_summary(audio_path, patient_id)

            store_results_in_sqlite(results)

            print("\n📄 Summary:\n", results["physician_summary"])
            print("\n🩺 Structured Symptoms:\n", results["symptoms_json"])
            continue

        # Continue normal chat agent processing
        response, state = process_user_input(user_input, state)
        print(f"Assistant: {response}\n")


if __name__ == "__main__":
    main()
