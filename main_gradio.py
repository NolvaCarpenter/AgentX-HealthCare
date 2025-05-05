#!/usr/bin/env python3

import os
import sys
import gradio as gr
from datetime import datetime

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversation_agent import process_user_input, initialize_state
from symptoms.symptom_state import SymptomState
from conversation_thread import (
    get_active_threads,
    create_new_thread,
    get_thread_history,
    get_thread_summary,
)


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
    # Add states for conversation
    state = gr.State(None)
    thread_id = gr.State(None)

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

            with gr.Row():
                clear = gr.Button("New Conversation")

        with gr.Column(scale=1):
            symptoms_display = gr.Markdown(
                label="Current Symptoms",
                value="No symptoms recorded yet",
            )

            thread_info = gr.Markdown(
                label="Thread Information", value="No active thread"
            )

            with gr.Accordion("Conversation Threads", open=False):
                thread_dropdown = gr.Dropdown(
                    label="Select a conversation thread", choices=[], interactive=True
                )
                refresh_threads = gr.Button("Refresh Threads")

    def get_thread_display(thread_id_value):
        """Get thread information display"""
        if not thread_id_value:
            return "No active thread"

        thread_info = get_thread_summary(thread_id_value)
        return f"""
### Active Thread
**ID**: {thread_id_value}  
**Created**: {thread_info['created_at']}  
**Messages**: {thread_info['message_count']}  
**Last Updated**: {thread_info['last_updated']}
"""

    def update_thread_dropdown():
        """Update the thread dropdown with active threads"""
        threads = get_active_threads()
        choices = []

        for t in threads:
            created_date = datetime.fromisoformat(t["created_at"]).strftime(
                "%m/%d/%Y %H:%M"
            )
            display = f"{created_date} - {t['thread_id'][:10]}..."
            choices.append((display, t["thread_id"]))

        return gr.Dropdown(choices=choices)

    def respond(message, history, current_state, current_thread_id):
        """Handle chat interactions and update the interface."""
        if not message:
            return (
                "",
                history,
                current_state,
                "No symptoms recorded yet",
                current_thread_id,
                "No active thread",
            )

        # Create a new thread if none exists
        if not current_thread_id:
            current_thread_id = create_new_thread()

        # Import and update the LangGraph config with current thread_id
        from conversation_agent import config

        config["configurable"]["thread_id"] = current_thread_id

        # Process user input through conversation agent
        response, updated_state = process_user_input(
            message, current_state, current_thread_id
        )

        # Update history and return (using tuple format)
        history.append((message, response))

        # Format symptom summary
        symptom_summary = format_symptom_summary(updated_state["symptom_state"])

        # Get thread display
        thread_display = get_thread_display(current_thread_id)

        return (
            "",
            history,
            updated_state,
            symptom_summary,
            current_thread_id,
            thread_display,
        )

    def new_conversation():
        """Start a new conversation thread."""
        new_thread_id = create_new_thread()
        new_state = None  # Will be initialized by process_user_input on first call

        # Update the LangGraph config with the new thread_id
        from conversation_agent import config

        config["configurable"]["thread_id"] = new_thread_id

        thread_display = get_thread_display(new_thread_id)

        # Update the thread dropdown
        updated_dropdown = update_thread_dropdown()

        return (
            [],
            new_state,
            "No symptoms recorded yet",
            new_thread_id,
            thread_display,
            updated_dropdown,
        )

    def switch_thread(selected_thread_id):
        """Switch to the selected conversation thread."""
        if not selected_thread_id:
            return [], None, "No symptoms recorded yet", None, "No active thread"

        # Get the thread history
        thread_messages = get_thread_history(selected_thread_id)

        # Convert thread history to chatbot format
        history = [
            (msg["content"], thread_messages[i + 1]["content"])
            for i, msg in enumerate(thread_messages)
            if msg["role"] == "user" and i + 1 < len(thread_messages)
        ]

        # Initialize a new state with this thread
        new_state = None  # Will be reinitialized with the thread context

        # Update the LangGraph config with the selected thread_id
        from conversation_agent import config

        config["configurable"]["thread_id"] = selected_thread_id

        # Format thread display
        thread_display = get_thread_display(selected_thread_id)

        # We'll need to run at least one process_user_input to get the state with symptom info
        if history:
            # Use the last user message to restore state
            _, new_state = process_user_input(history[-1][0], None, selected_thread_id)
            symptom_summary = format_symptom_summary(new_state["symptom_state"])
        else:
            # Empty thread, initialize with empty message
            _, new_state = process_user_input("", None, selected_thread_id)
            symptom_summary = "No symptoms recorded yet"

        return history, new_state, symptom_summary, selected_thread_id, thread_display

    # Wire up the interface
    submit_btn.click(
        respond,
        inputs=[msg, chatbot, state, thread_id],
        outputs=[msg, chatbot, state, symptoms_display, thread_id, thread_info],
    )
    msg.submit(
        respond,
        inputs=[msg, chatbot, state, thread_id],
        outputs=[msg, chatbot, state, symptoms_display, thread_id, thread_info],
    )
    clear.click(
        new_conversation,
        outputs=[
            chatbot,
            state,
            symptoms_display,
            thread_id,
            thread_info,
            thread_dropdown,
        ],
    )

    thread_dropdown.change(
        switch_thread,
        inputs=[thread_dropdown],
        outputs=[chatbot, state, symptoms_display, thread_id, thread_info],
    )

    refresh_threads.click(update_thread_dropdown, outputs=[thread_dropdown])


def main():
    """Main function to launch the Gradio interface."""
    # Check for OpenAI API key
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable is not set.")
            print("Please set your OpenAI API key as an environment variable.")
            sys.exit(1)

    # Create thread tables if they don't exist
    from conversation_thread import create_conversation_tables

    create_conversation_tables()

    print("Starting Gradio interface for the Healthcare Conversation Assistant...")
    print("The interface will be available at http://127.0.0.1:7860")
    demo.launch()


if __name__ == "__main__":
    main()
