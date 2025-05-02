#!/usr/bin/env python3

import os
import sys
import gradio as gr

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversation_agent import process_user_input, initialize_state
from symptoms.symptom_state import SymptomState


def format_symptom_summary(symptom_state):
    """Format the symptom state into a markdown summary."""
    if not symptom_state or not symptom_state.primary_symptoms:
        return "No symptoms recorded yet"

    summary = "## Live Symptoms Tracking\n\n"

    for symptom in symptom_state.primary_symptoms:
        summary += f"- **{symptom}**\n"
        if symptom in symptom_state.symptom_details:
            details = symptom_state.symptom_details[symptom]
            if details.severity:
                summary += f"  - Severity: Level {details.severity.level if details.severity.level is not None else 'Not specified'}\n"
                if details.severity.description:
                    summary += f"    - Description: {details.severity.description}\n"
            if details.duration:
                if details.duration.start_date:
                    summary += f"  - Started: {details.duration.start_date}\n"
                if details.duration.is_ongoing:
                    summary += f"  - Status: Ongoing\n"
                elif details.duration.end_date:
                    summary += f"  - Ended: {details.duration.end_date}\n"
            if details.characteristics:
                summary += (
                    f"  - Characteristics: {', '.join(details.characteristics)}\n"
                )
            if details.location:
                summary += f"  - Location: {details.location}\n"
            if details.quality:
                summary += f"  - Quality: {details.quality}\n"
            if details.frequency:
                if details.frequency.times:
                    summary += f"  - Frequency: {details.frequency.times} times"
                    if details.frequency.period:
                        summary += f" per {details.frequency.period}\n"
                    else:
                        summary += "\n"
                elif details.frequency.description:
                    summary += f"  - Frequency: {details.frequency.description}\n"
            if details.aggravating_factors:
                summary += f"  - Aggravating factors: {', '.join(details.aggravating_factors)}\n"
            if details.relieving_factors:
                summary += (
                    f"  - Relieving factors: {', '.join(details.relieving_factors)}\n"
                )

            if details.triggers:
                summary += f"  - Triggers: {', '.join(details.triggers)}\n"
        summary += "\n"

    return summary


# Create Gradio interface
with gr.Blocks(title="Healthcare Conversation Assistant") as demo:
    # Add state for conversation
    state = gr.State(None)

    with gr.Row():
        with gr.Column(scale=2):
            # Use tuple format for chatbot which is the default
            chatbot = gr.Chatbot(
                label="Conversation",
                height=400,
                show_copy_button=True,
                elem_classes=["gr-box"],
            )
            with gr.Row():
                msg = gr.Textbox(
                    label="",
                    placeholder="Describe your symptoms or ask a question...",
                    lines=1,
                    scale=5,
                )
                submit_btn = gr.Button("Send 📨", scale=1)
            clear = gr.Button("Clear")

        with gr.Column(scale=1):
            symptoms_display = gr.Markdown(
                label="Current Symptoms",
                value="No symptoms recorded yet",
            )

    def respond(message, history, current_state):
        """Handle chat interactions and update the interface."""
        if not message:
            return "", history, current_state, "No symptoms recorded yet"

        # Process user input through conversation agent
        response, updated_state = process_user_input(message, current_state)

        # Update history and return (using tuple format)
        history.append((message, response))

        # Format symptom summary
        symptom_summary = format_symptom_summary(updated_state["symptom_state"])

        return "", history, updated_state, symptom_summary

    def clear_conversation():
        """Reset the conversation and state."""
        new_state = None  # Will be initialized by process_user_input on first call
        return [], new_state, "No symptoms recorded yet"

    # Wire up the interface
    submit_btn.click(
        respond,
        inputs=[msg, chatbot, state],
        outputs=[msg, chatbot, state, symptoms_display],
    )
    msg.submit(
        respond,
        inputs=[msg, chatbot, state],
        outputs=[msg, chatbot, state, symptoms_display],
    )
    clear.click(clear_conversation, outputs=[chatbot, state, symptoms_display])


def main():
    """Main function to launch the Gradio interface."""
    # Check for OpenAI API key
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable is not set.")
            print("Please set your OpenAI API key as an environment variable.")
            sys.exit(1)

    print("Starting Gradio interface for the Healthcare Conversation Assistant...")
    print("The interface will be available at http://127.0.0.1:7860")
    demo.launch()


if __name__ == "__main__":
    main()
