import os
import shutil
import gradio as gr

from utils.gradio_styles import gradio_css
from conversation_agent import process_user_input, initialize_state, load_thread_state
from conversation_thread import (
    create_new_thread,
    get_thread_history,
    get_active_threads,
    get_thread_summary,
)

from medications.handle_upload import validate_medication_image
from utils.display_helpers import format_symptom_summary, convert_image_to_data_url


def start_conversation(name):
    """Initialize a new conversation with a user name."""
    if not name.strip():
        return gr.update(visible=True), gr.update(visible=False), ""

    username = name.strip().lower().replace(" ", "_")
    print(f"Starting conversation for user: {username}")

    # load previous threads for the user
    # refresh_thread_list(username)
    chat_history, state, thread_id, symptoms_display, thread_info = (
        create_new_conversation(username)
    )

    return (
        gr.update(visible=False),  # Hide login screen
        gr.update(visible=True),  # Show chat interface
        username,
        chat_history,
        state,
        thread_id,
        symptoms_display,
        thread_info,
    )


def create_new_conversation(username):
    """Create a new conversation for the current user."""
    print(f"Creating new conversation for user: {username}")
    thread_id = create_new_thread(username)

    # Initialize an empty state with the proper username
    state = initialize_state(username=username)
    state["thread_id"] = thread_id

    chat_history = []
    system_message = f"Hello, I'm here to assist you with documenting your symptoms. How can I help you today?"
    chat_history.append({"role": "assistant", "content": system_message})

    return (
        chat_history,
        state,
        thread_id,
        "No symptoms recorded yet.",
        f"## Active Thread\n\nNew conversation started for {username}",
    )


def process_medication_upload(file_obj, chat_history, state, thread_id, username):
    """Process uploaded medication label image."""
    if file_obj is None:
        return chat_history, state, "No file uploaded", thread_id, "", username

    # Create a thread if one doesn't exist
    if not thread_id:
        thread_id = create_new_thread(username)
        print(f"Created new thread for medication upload: {thread_id}")

    base_filename = os.path.basename(file_obj.name)
    upload_dir = os.path.join("upload", "drug_labels")

    # Ensure the upload directory exists
    os.makedirs(upload_dir, exist_ok=True)

    temp_path = os.path.join(upload_dir, base_filename)

    # file_obj is the path to the temporary file
    shutil.copy2(file_obj, temp_path)

    # Validate the file
    valid_filename, message = validate_medication_image(temp_path)
    display_message = f"I'm uploading a medication label:"

    # Convert the image to a data URL for direct display - only for UI
    image_data_url = convert_image_to_data_url(temp_path)

    # For display in chat history, include the image
    chat_history.append(
        {
            "role": "user",
            "content": f"{display_message}\n![Medication Label]({image_data_url})",
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

        # Process medication upload with just the filename to avoid sending large base64 data
        processing_message = f"I'm uploading a medication label: {valid_filename}"
        response, updated_state = process_user_input(
            processing_message,
            state,
            thread_id,
            username,
        )

        # Update the state with the results
        state = updated_state

        # Add the assistant's text response
        chat_history.append({"role": "assistant", "content": response})

        symptom_summary = format_symptom_summary(state)
        thread_summary = get_thread_summary(thread_id)
        thread_display = f"## Active Thread\n\n{thread_summary}"

        return chat_history, state, symptom_summary, thread_id, thread_display, username
    else:
        # Handle error case
        error_message = f"I couldn't process the medication label. {message} Please try again with a valid image file."
        print(f"Error processing medication label: {error_message}")

        # Add error message
        chat_history.append({"role": "assistant", "content": error_message})
        # Display the image or path in the chat history
        if image_data_url:
            # For display in the chat, show the image
            chat_history.append(
                {"role": "assistant", "content": f"![Problem Image]({image_data_url})"}
            )
        else:
            # Fall back to original behavior
            chat_history.append({"role": "assistant", "content": temp_path})

        return chat_history, state, "", thread_id, "", username


def switch_thread(thread_id, username):
    """Switch to a different conversation thread."""
    if not thread_id:
        return [], {}, "No symptoms recorded yet.", None, "", username

    # Get thread history and summary
    chat_history = get_thread_history(thread_id)
    thread_summary_data = get_thread_summary(thread_id)

    if not chat_history or "error" in thread_summary_data:
        return [], {}, "No thread data found", thread_id, "Thread not found", username

    # Load the thread state
    print(f"Loading thread state for thread ID: {thread_id}")
    state = load_thread_state(thread_id, username)

    # Use thread_summary_data for username if available
    if "user_id" in thread_summary_data and thread_summary_data["user_id"] != username:
        username = thread_summary_data["user_id"]

    symptom_summary = format_symptom_summary(state)
    thread_display = f"## Active Thread\n\n{thread_summary_data}"

    return (
        chat_history,
        state,
        symptom_summary,
        thread_id,
        thread_display,
        username,
    )


def refresh_thread_list(username="default_user"):
    """Refresh the list of conversation threads."""
    print(f"Refreshing threads for user: {username}")
    active_threads = get_active_threads(user_id=username)
    thread_choices = [thread["thread_id"] for thread in active_threads]
    return gr.update(choices=thread_choices)


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
    print(f"User message: {message}")
    # print(f"Current state: {state}")
    # print(f"Using username: {username}")

    response, updated_state = process_user_input(message, state, thread_id, username)

    chat_history.append({"role": "assistant", "content": response})
    symptom_summary = format_symptom_summary(updated_state)

    print(f"AI response: {response}")
    # Update thread summary
    thread_summary = get_thread_summary(thread_id)
    thread_display = f"## Active Thread\n\n{thread_summary}"

    yield "", chat_history, updated_state, symptom_summary, thread_id, thread_display, username


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
            gr.Markdown("# Welcome to Health Conversation Assistant")
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
                    height=600,
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
        outputs=[
            login_screen,
            chat_interface,
            username,
            chatbot,
            state,
            thread_id,
            symptoms_display,
            thread_info,
        ],
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
        refresh_thread_list,
        inputs=[username],
        outputs=[thread_dropdown],
        queue=False,
    )


if __name__ == "__main__":
    print("Starting Healthcare Conversation Assistant...")
    demo.launch(share=False)
