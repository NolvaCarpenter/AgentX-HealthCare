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

    summary = "## Symptoms Tracking\n\n"

    if (
        not symptom_state
        or not hasattr(symptom_state, "primary_symptoms")
        or not symptom_state.primary_symptoms
    ):
        return summary + "No symptoms recorded yet"

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
                summary += f"  - Frequency: {details.frequency}\n"
            if details.aggravating_factors:
                summary += f"  - Aggravating factors: {', '.join(details.aggravating_factors)}\n"
            if details.relieving_factors:
                summary += (
                    f"  - Relieving factors: {', '.join(details.relieving_factors)}\n"
                )
            if details.associated_symptoms:
                summary += f"  - Associated symptoms: {', '.join(details.associated_symptoms)}\n"
            if details.context:
                summary += f"  - Context: {details.context}\n"
            summary += "\n"

    return summary


def start_conversation(name):
    """Start a new conversation with the user."""
    if not name.strip():
        return gr.update(visible=True), gr.update(visible=False), ""

    # Set username to use for the whole session
    username = name.strip().replace(" ", "_").lower()
    print(f"Starting conversation for user: {username}")

    # Hide login screen and show chat interface
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        username,
    )


def switch_thread(selected_thread_id, current_username):
    """Switch to a different conversation thread."""
    thread_messages = get_thread_history(selected_thread_id)
    thread_summary = get_thread_summary(selected_thread_id)

    # Convert history to chatbot messages format and initialize state
    chatbot_history = []
    for message in thread_messages:
        role = message["role"]
        content = message["content"]
        if role == "user":
            chatbot_history.append({"role": "user", "content": content})
        elif role == "assistant":
            chatbot_history.append({"role": "assistant", "content": content})

    # Initialize state from thread history with the proper username
    new_state = initialize_state(username=current_username)
    if thread_messages:
        for message in thread_messages:
            if "symptom_state" in message:
                new_state = message["symptom_state"]

    symptom_summary = format_symptom_summary(new_state)

    thread_display = f"## Active Thread\n\n{thread_summary}"

    # Return all the updates
    return (
        chatbot_history,
        new_state,
        symptom_summary,
        selected_thread_id,
        thread_display,
        current_username,
    )


def respond(message, chat_history, state, thread_id, username):
    """Process user message and update the interface."""
    if not message:
        return message, chat_history, state, "", thread_id, "", username

    # Create thread if not exists
    if not thread_id:
        thread_id = create_new_thread(username)

    chat_history.append({"role": "user", "content": message})

    # This ensures the partial appearance
    yield message, chat_history, state, "", thread_id, "", username

    # Process the message
    print(f"Processing message: {message}")
    print(f"Current state: {state}")
    print(f"Using username: {username}")
    response, updated_state = process_user_input(message, state, thread_id, username)
    state = updated_state

    chat_history.append({"role": "assistant", "content": response})
    symptom_summary = format_symptom_summary(state["symptom_state"])

    # Update thread summary
    thread_summary = get_thread_summary(thread_id)
    thread_display = f"## Active Thread\n\n{thread_summary}"

    yield "", chat_history, state, symptom_summary, thread_id, thread_display, username


def refresh_thread_list(username="default_user"):
    """Refresh the list of conversation threads."""
    print(f"Refreshing threads for user: {username}")
    active_threads = get_active_threads(user_id=username)
    thread_choices = [
        (thread["thread_id"], f"Thread from {thread['last_updated']}")
        for thread in active_threads
    ]
    return gr.update(choices=thread_choices)


def create_new_conversation(username):
    """Create a new conversation for the current user."""
    print(f"Creating new conversation for user: {username}")
    new_thread_id = create_new_thread(username)
    return [], None, new_thread_id, "No symptoms recorded yet", ""


# Create Gradio interface
with gr.Blocks(
    title="Healthcare Conversation Assistant",
    css="""
        /* Main styling for the entire interface */
        .gradio-container {
            background-color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
        
        /* Login container styling */
        #login-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 20px;
            max-width: 800px;
            margin: 50px auto;
        }
        
        /* Card styling for components */
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            padding: 15px;
            margin-bottom: 15px;
        }
        
        /* Header styling */
        h1, h2, h3 {
            font-weight: 600;
            color: #333;
        }
        
        /* Button styling */
        button.primary {
            background-color: #0078d4 !important;
            border: none;
            color: white;
        }
        
        /* Secondary buttons */
        .secondary-button {
            border: 1px solid #0078d4 !important;
            color: #0078d4 !important;
            background-color: white !important;
        }
        
        /* Chat interface styling */
        #chat-interface {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 20px;
        }
        
        /* Message container */
        .message {
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        /* User message */
        .user-message {
            background-color: #e6f2ff;
            color: #333;
            margin-left: 20%;
        }
        
        /* Bot message */
        .bot-message {
            background-color: #f5f5f7;
            color: #333;
            margin-right: 20%;
        }
        
        /* Sidebar with symptoms */
        .sidebar {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
        }
        
        /* Improve textbox appearance */
        .gr-box {
            border-radius: 8px !important;
            border: 1px solid #ddd !important;
        }
        
        /* Conversation container */
        .gr-chatbox {
            border: 1px solid #eee;
            border-radius: 10px;
            overflow: hidden;
        }
    """,
) as demo:
    # Add states for conversation
    state = gr.State(None)
    thread_id = gr.State(None)
    username = gr.State("")  # Add a state to store the username

    # Login screen
    with gr.Group(visible=True, elem_id="login-container") as login_screen:
        with gr.Column(scale=1, min_width=500, elem_classes=["card"]):
            gr.Markdown("# Welcome to Healthcare Conversation Assistant")
            gr.Markdown("\nPlease enter your name to get started.")
            name_input = gr.Textbox(
                label="Your Name",
                placeholder="Enter your name",
                lines=1,
                elem_classes=["gr-box"],
                container=False,
            )
            start_btn = gr.Button("Start Conversation", variant="primary")

    # Main chat interface (hidden initially)
    with gr.Group(visible=False, elem_id="chat-interface") as chat_interface:
        with gr.Row():
            # Use messages format for chatbot (recommended)
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    show_copy_button=True,
                    elem_classes=["gr-box", "gr-chatbox"],
                    type="messages",
                )
                with gr.Row():
                    msg = gr.Textbox(
                        label="",
                        placeholder="Describe your symptoms or ask a question...",
                        lines=1,
                        scale=5,
                        elem_classes=["gr-box"],
                        container=False,
                    )
                    submit_btn = gr.Button("Send 📨", scale=1, variant="primary")

                with gr.Row():
                    clear = gr.Button(
                        "New Conversation", elem_classes=["secondary-button"]
                    )

            # Sidebar for symptoms and thread information
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                symptoms_display = gr.Markdown(
                    label="Current Symptoms",
                    value="No symptoms recorded yet",
                    elem_classes=["card"],
                )

                thread_info = gr.Markdown(
                    label="Thread Information",
                    value="No active thread",
                    elem_classes=["card"],
                )

                with gr.Accordion(
                    "Conversation Threads", open=False, elem_classes=["card"]
                ):
                    thread_dropdown = gr.Dropdown(
                        label="Select a conversation thread",
                        choices=[],
                        interactive=True,
                        container=False,
                    )
                    refresh_threads = gr.Button(
                        "Refresh Threads", elem_classes=["secondary-button"]
                    )

    # Wire up the interface
    submit_btn.click(
        respond,
        inputs=[msg, chatbot, state, thread_id, username],
        outputs=[
            msg,
            chatbot,
            state,
            symptoms_display,
            thread_id,
            thread_info,
            username,
        ],
    )
    msg.submit(
        respond,
        inputs=[msg, chatbot, state, thread_id, username],
        outputs=[
            msg,
            chatbot,
            state,
            symptoms_display,
            thread_id,
            thread_info,
            username,
        ],
    )

    # Set up thread management
    start_btn.click(
        start_conversation,
        inputs=[name_input],
        outputs=[login_screen, chat_interface, username],
    )

    # New conversation button creates a fresh thread with the current username
    clear.click(
        create_new_conversation,
        inputs=[username],
        outputs=[chatbot, state, thread_id, symptoms_display, thread_info],
        queue=False,
    )

    thread_dropdown.change(
        switch_thread,
        inputs=[thread_dropdown, username],
        outputs=[chatbot, state, symptoms_display, thread_id, thread_info, username],
    )

    refresh_threads.click(
        refresh_thread_list, inputs=[username], outputs=[thread_dropdown]
    )

    # Initialize thread list with default user (will be updated when user logs in)
    # demo.load(lambda: refresh_thread_list("default_user"), outputs=[thread_dropdown])


if __name__ == "__main__":
    # Launch the demo
    print("Starting Gradio interface for the Healthcare Conversation Assistant...")
    demo.queue().launch()
