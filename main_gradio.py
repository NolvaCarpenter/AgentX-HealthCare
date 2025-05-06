#!/usr/bin/env python3

import os, sys, shutil
import gradio as gr

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversation_agent import process_user_input, initialize_state
from symptoms.symptom_state import SymptomState
from conversation_thread import (
    get_active_threads,
    create_new_thread,
    get_thread_summary,
)
from utils.gradio_styles import gradio_css
from medications.handle_upload import validate_medication_image


def format_symptom_summary(state):
    """Format the symptom state into a markdown summary."""
    summary = "## Symptom Tracking\n\n"

    # Get symptom_state from state
    symptom_state = state.get("symptom_state") if state else None

    # Handle symptoms summary
    if (
        not symptom_state
        or not hasattr(symptom_state, "primary_symptoms")
        or not symptom_state.primary_symptoms
    ):
        summary += "No symptoms recorded yet\n\n"
    else:
        for symptom in symptom_state.primary_symptoms:
            summary += f"- **{symptom}**\n"
            if symptom in symptom_state.symptom_details:
                details = symptom_state.symptom_details[symptom]
                if details.severity:
                    summary += f"  - Severity: Level {details.severity.level if details.severity.level is not None else 'Not specified'}\n"
                    if details.severity.description:
                        summary += (
                            f"    - Description: {details.severity.description}\n"
                        )
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
                    summary += f"  - Relieving factors: {', '.join(details.relieving_factors)}\n"
                if details.associated_symptoms:
                    summary += f"  - Associated symptoms: {', '.join(details.associated_symptoms)}\n"
                if details.context:
                    summary += f"  - Context: {details.context}\n"
                summary += "\n"

    # Add medication information if available
    if state and "extracted_medications" in state and state["extracted_medications"]:
        summary += "## Medications\n\n"
        for drug_name, medication in state["extracted_medications"].items():
            summary += f"- **{drug_name}**\n"

            if hasattr(medication, "drug_strength") and medication.drug_strength:
                summary += f"  - Strength: {medication.drug_strength}\n"

            if (
                hasattr(medication, "drug_instructions")
                and medication.drug_instructions
            ):
                summary += f"  - Instructions: {medication.drug_instructions}\n"

            if hasattr(medication, "prescriber_name") and medication.prescriber_name:
                summary += f"  - Prescriber: {medication.prescriber_name}\n"

            if hasattr(medication, "pharmacy_name") and medication.pharmacy_name:
                summary += f"  - Pharmacy: {medication.pharmacy_name}\n"

            if hasattr(medication, "refill_count") and medication.refill_count:
                summary += f"  - Refills: {medication.refill_count}\n"

            if hasattr(medication, "federal_caution") and medication.federal_caution:
                summary += f"  - Warning: {medication.federal_caution}\n"

            summary += "\n"

    return summary


def start_conversation(name):
    """Start a new conversation with the user."""
    if not name.strip():
        return gr.update(visible=True), gr.update(visible=False), ""

    # Set username to use for the whole session
    username = name.strip().replace(" ", "_").lower()
    print(f"Starting conversation for user: {username}")

    refresh_thread_list(username)

    # Hide login screen and show chat interface
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        username,
    )


def switch_thread(selected_thread_id, current_username):
    """Switch to a different conversation thread."""
    from conversation_thread import (
        get_thread_history,
        get_thread_summary,
        get_symptom_data,
        get_medication_data,
    )
    from symptoms.symptom_state import SymptomState
    from medications.medication_state import MedicationLabel

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

    # Initialize state with the proper username
    new_state = initialize_state(username=current_username)

    # Set thread ID in state
    new_state["thread_id"] = selected_thread_id

    # Load symptom data from database
    symptom_data = get_symptom_data(selected_thread_id)
    if symptom_data:
        print(
            f"Loaded symptom data for thread {selected_thread_id}: {symptom_data.get('primary_symptoms', [])}"
        )
        symptom_state = SymptomState.model_validate(symptom_data)
        new_state["symptom_state"] = symptom_state
    else:
        print(f"No symptom data found for thread {selected_thread_id}")

    # Load medication data from database
    medication_data = get_medication_data(selected_thread_id)
    if medication_data:
        print(
            f"Loaded medication data for thread {selected_thread_id}: {list(medication_data.keys())}"
        )

        # Convert medication data back to MedicationLabel objects
        extracted_medications = {}
        for drug_name, med_data in medication_data.items():
            extracted_medications[drug_name] = MedicationLabel.model_validate(med_data)
        new_state["extracted_medications"] = extracted_medications
    else:
        print(f"No medication data found for thread {selected_thread_id}")

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
    symptom_summary = format_symptom_summary(state)

    # Update thread summary
    thread_summary = get_thread_summary(thread_id)
    thread_display = f"## Active Thread\n\n{thread_summary}"

    yield "", chat_history, state, symptom_summary, thread_id, thread_display, username


def refresh_thread_list(username="default_user"):
    """Refresh the list of conversation threads."""
    print(f"Refreshing threads for user: {username}")
    active_threads = get_active_threads(user_id=username)
    thread_choices = [thread["thread_id"] for thread in active_threads]
    return gr.update(choices=thread_choices)


def create_new_conversation(username):
    """Create a new conversation for the current user."""
    print(f"Creating new conversation for user: {username}")
    new_thread_id = create_new_thread(username)

    # Initialize an empty state with the proper username
    state = initialize_state(username=username)
    state["thread_id"] = new_thread_id

    # Clear any previously loaded symptom and medication data
    state["symptom_state"] = SymptomState()
    state["extracted_medications"] = {}

    return [], state, new_thread_id, "No symptoms or medications recorded yet", ""


def process_medication_upload(file_obj, chat_history, state, thread_id, username):
    """Process uploaded medication label image."""
    if file_obj is None:
        return chat_history, state, "No file uploaded", thread_id, "", username

    # Create a thread if one doesn't exist
    if not thread_id:
        thread_id = create_new_thread(username)
        print(f"Created new thread for medication upload: {thread_id}")

    base_filename = os.path.basename(file_obj.name)
    temp_path = os.path.join("upload", "drug_labels", base_filename)

    # file_obj is the path to the temporary file
    shutil.copy2(file_obj, temp_path)

    # Validate the file
    valid_filename, message = validate_medication_image(temp_path)

    # Add user message to the chat history
    chat_history.append(
        {
            "role": "user",
            "content": f"I'm uploading a medication label: {base_filename}",
        }
    )

    if valid_filename:
        # Initialize state if needed
        if state is None:
            state = initialize_state(username=username)

        # Set thread_id in the state
        state["thread_id"] = thread_id

        # Update state with the filename and prepare for processing
        state["filename"] = valid_filename
        state["current_action"] = "prepare_medication_upload"

        print(f"Processing medication label: {valid_filename}")

        # First, directly run the medication processing through the agent
        response, updated_state = process_user_input(
            f"Process this medication label: {valid_filename}",
            state,
            thread_id,
            username,
        )

        # Update the state with the results
        state = updated_state
        chat_history.append({"role": "assistant", "content": response})

        symptom_summary = format_symptom_summary(state)
        thread_summary = get_thread_summary(thread_id)
        thread_display = f"## Active Thread\n\n{thread_summary}"

        return chat_history, state, symptom_summary, thread_id, thread_display, username
    else:
        # Handle error case
        error_message = f"I couldn't process the medication label. {message} Please try again with a valid image file."
        chat_history.append({"role": "assistant", "content": error_message})
        return chat_history, state, "", thread_id, "", username


# Create Gradio interface
with gr.Blocks(
    title="Healthcare Conversation Assistant",
    css=gradio_css,
) as demo:
    # Add states for conversation
    state = gr.State(None)
    thread_id = gr.State(None)
    username = gr.State(None)

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
        with gr.Row(equal_height=True):
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
                        scale=4,
                        elem_classes=["gr-box"],
                        container=False,
                    )
                    submit_btn = gr.Button("Send 📨", scale=1, variant="primary")

                    file_upload = gr.UploadButton(
                        "Upload 📷",
                        file_types=["image"],
                        scale=1,
                        variant="primary",
                        file_count="single",
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
                with gr.Row():
                    clear = gr.Button(
                        "New Conversation", elem_classes=["secondary-button"]
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

    # File upload handling
    file_upload.upload(
        process_medication_upload,
        inputs=[file_upload, chatbot, state, thread_id, username],
        outputs=[
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

    # Initialize thread list
    # demo.load(refresh_thread_list, inputs=[username], outputs=[thread_dropdown])

if __name__ == "__main__":
    # Launch the demo
    print("Starting Gradio interface for the Healthcare Conversation Assistant...")
    demo.queue().launch()
