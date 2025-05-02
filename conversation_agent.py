from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.graph import StateGraph, END
from typing import Dict, List, Any, TypedDict, Optional, Tuple, Literal
import os
import tempfile
import webbrowser

from symptoms.symptom_state import SymptomState, SymptomDetail, Severity, Duration
from symptoms.symptom_extraction import SymptomExtractor, SymptomDetailExtractor

from medications.medication_state import build_medication_workflow
from medications.medication_extraction import MedicationProcessState, MedicationLabel
from medications.handle_upload import validate_medication_image, get_available_samples


# Define the state schema for the conversation graph
class ConversationState(TypedDict):
    user_id: str
    user_input: str
    ai_response: str
    current_action: str
    chat_history: List[Dict[str, str]]
    symptom_state: SymptomState
    extracted_symptoms: Dict[str, SymptomDetail]
    missing_fields: List[str]
    filename: str
    medication_state: MedicationProcessState
    extracted_medications: Dict[str, MedicationLabel]


# Initialize the language model
llm = ChatOpenAI(model_name="gpt-4o")

# Initialize extractors
symptom_extractor = SymptomExtractor()
detail_extractor = SymptomDetailExtractor()

# Configuration constants
MAX_MISSING_FIELDS_TO_ASK = 2  # Maximum number of missing fields to ask about at once


# Define the nodes for the conversation graph
def initialize_state() -> ConversationState:
    """Initialize the conversation state."""
    return {
        "user_id": "default_user",
        "user_input": "",
        "ai_response": "",
        "current_action": "chat",
        "chat_history": [],
        "symptom_state": SymptomState(),
        "extracted_symptoms": {},
        "missing_fields": [],
        "filename": "",
        "medication_state": MedicationProcessState(),
        "extracted_medications": {},
    }


def prepare_medication_upload(state: ConversationState) -> ConversationState:
    """
    Handle medication label upload preparation.
    Updates the state with the validated filename.

    Args:
        state (ConversationState): The current conversation state

    Returns:
        ConversationState: The updated state
    """
    # Display available samples
    print("\nMedication Label Upload:")
    samples = get_available_samples()
    if samples:
        print(f"Available sample files: {', '.join(samples)}")
    else:
        print("No sample files found in default directory.")

    # Prompt for filename
    filename = input(
        "Enter medication label image filename (or press Enter for default): "
    ).strip()

    # Validate the filename
    valid_filename, message = validate_medication_image(filename)
    print(message)

    if valid_filename:
        print(f"Processing file: {valid_filename}")
        # Return updated state with t Fashion he filename and next action
        return {
            **state,
            "filename": valid_filename,
            "ai_response": f"I've successfully processed your medication label from the file: {valid_filename}. Any other things you want to share with me?",
            "current_action": "extract_medication_labels",
        }
    else:
        print("Could not process medication label. Please try again.")
        return {
            **state,
            "ai_response": "I couldn't process the medication label. Please try again with a valid image file.",
            "current_action": "generate_response",
        }


def extract_medication_labels(state: ConversationState) -> ConversationState:
    """
    Extract medication information from label images.
    Processes the medication label and updates extracted_medications in the conversation state.

    Args:
        state (ConversationState): The current conversation state

    Returns:
        ConversationState: The updated state with extracted medication information
    """
    # Get the current medication state and filename
    medication_state = state["medication_state"]
    filename = state["filename"]

    # Update the medication state with the filename
    medication_state.filename = (
        filename  # Run the medication workflow to extract information
    )
    medication_workflow = build_medication_workflow()
    processed_state = medication_workflow.invoke(medication_state)

    # If processed_state is an AdjustableValueDict, convert it to a MedicationProcessState
    if isinstance(processed_state, dict):
        processed_state = MedicationProcessState(**processed_state)

    # Get the extracted medication label
    extracted_label = processed_state.label

    # If a medication was successfully extracted, add it to extracted_medications
    extracted_medications = state.get("extracted_medications", {})
    if extracted_label:
        # Use the drug name as the key for the medication
        drug_name = (
            extracted_label.drug_name
            if extracted_label.drug_name
            else "Unknown Medication"
        )
        extracted_medications[drug_name] = extracted_label

    # Update state with processed medication information
    return {
        **state,
        "medication_state": processed_state,
        "extracted_medications": extracted_medications,
        "current_action": "generate_response",
    }


def check_symptom_context(state: ConversationState) -> str:
    """Check if user input contains symptom-related context and return the next node."""
    user_input = state["user_input"]

    # For initial greeting, go directly to generate_response
    if not user_input:
        return "generate_response"

    # Check if user is requesting a summary
    if "summary" in user_input.lower() or "summarize" in user_input.lower():
        return "generate_summary"  # upload photo or medication label

    # Check if user is uploading a medication label
    if "upload" in user_input.lower() or "photo" in user_input.lower():
        return "prepare_medication_upload"

    # List of terms that might indicate symptom-related context
    # TODO: enhance the symptom indicators with knowledge-base or RAG.
    symptom_indicators = [
        "pain",
        "ache",
        "hurt",
        "sore",
        "discomfort",
        "fever",
        "temperature",
        "cough",
        "cold",
        "flu",
        "headache",
        "migraine",
        "nausea",
        "vomit",
        "dizzy",
        "tired",
        "fatigue",
        "exhaust",
        "weak",
        "symptom",
        "feel",
        "felt",
        "feeling",
        "experiencing",
        "suffering",
        "sick",
        "ill",
        "unwell",
        "doctor",
        "hospital",
        "medicine",
        "medication",
        "treatment",
        "condition",
    ]

    # Check if any symptom indicator is present in user input
    is_symptom_related = any(
        indicator in user_input.lower() for indicator in symptom_indicators
    )

    # Return the next node as a string, not a dict
    if is_symptom_related:
        return "extract_symptoms"
    # TODO: check if user has medication or drug related to symptoms
    # elif "medication" in user_input.lower() or "drug" in user_input.lower():
    #     return "extract_medications"
    else:
        # If not symptom-related, generate a response and skip symptom extraction
        return "generate_response"


def extract_symptoms(state: ConversationState) -> ConversationState:
    """Extract symptoms from user input."""
    user_input = state["user_input"]

    if not user_input:
        return state

    # Extract symptoms
    symptom_list = symptom_extractor.extract_symptoms(user_input)

    # Convert list to dictionary with empty details
    extracted_symptoms = {}
    for symptom in symptom_list:
        extracted_symptoms[symptom] = {}

    # Update state
    return {
        **state,
        "extracted_symptoms": extracted_symptoms,
        "current_action": "process_symptoms",
    }


def process_symptoms(state: ConversationState) -> ConversationState:
    """Process extracted symptoms and add them to the symptom state."""
    symptom_state = state["symptom_state"]
    extracted_symptoms = state["extracted_symptoms"]

    # Add each extracted symptom to the symptom state
    for symptom in extracted_symptoms.keys():
        symptom_state.add_symptom(symptom)

    # Update state
    return {
        **state,
        "symptom_state": symptom_state,
        "current_action": "extract_details",
    }


def extract_details(state: ConversationState) -> ConversationState:
    """Extract details for the current symptom."""
    symptom_state = state["symptom_state"]
    user_input = state["user_input"]
    extracted_symptoms = state["extracted_symptoms"]

    # Get missing fields to extract from state
    missing_fields = state.get("missing_fields", [])

    # If no current symptom, select one
    if not symptom_state.current_symptom and symptom_state.primary_symptoms:
        symptom_state.current_symptom = symptom_state.primary_symptoms[0]

    # If no symptoms or current_symptom is None, skip detail extraction
    if not symptom_state.primary_symptoms or not symptom_state.current_symptom:
        return {**state, "current_action": "generate_response"}

    current_symptom = symptom_state.current_symptom

    # Make sure current symptom exists in extracted_symptoms
    if current_symptom not in extracted_symptoms:
        extracted_symptoms[current_symptom] = {}

    # Extract details for each missing field from the user's response
    for missing_field in missing_fields:
        # Extract details based on the missing field
        if missing_field == "severity":
            severity_data = detail_extractor.extract_severity(
                current_symptom, user_input
            )
            if severity_data["level"] is not None:
                # Create a proper Severity object instead of using the dictionary directly
                extracted_symptoms[current_symptom]["severity"] = Severity(
                    level=severity_data["level"],
                    description=severity_data["description"],
                )

        elif missing_field in ["start_date", "is_ongoing"]:
            duration_data = detail_extractor.extract_duration(
                current_symptom, user_input
            )
            if any(v is not None for v in duration_data.values()):
                # Create a proper Duration object
                extracted_symptoms[current_symptom]["duration"] = Duration(
                    start_date=duration_data["start_date"],
                    end_date=duration_data["end_date"],
                    is_ongoing=duration_data["is_ongoing"],
                )

        elif missing_field in [
            "characteristics",
            "aggravating_factors",
            "relieving_factors",
            "triggers",
            "associated_symptoms",
        ]:
            list_data = detail_extractor.extract_list_detail(
                current_symptom, missing_field, user_input
            )
            if list_data:
                extracted_symptoms[current_symptom][missing_field] = list_data

        else:
            # For other string fields
            detail_value = detail_extractor.extract_detail(
                current_symptom, missing_field, user_input
            )
            if detail_value:
                extracted_symptoms[current_symptom][
                    missing_field
                ] = detail_value  # Update state
    return {
        **state,
        "symptom_state": symptom_state,
        "extracted_symptoms": extracted_symptoms,
        "current_action": "update_symptom_details",
    }


def update_symptom_details(state: ConversationState) -> ConversationState:
    """Update symptom details in the symptom state."""
    symptom_state = state["symptom_state"]
    extracted_symptoms = state["extracted_symptoms"]

    # If no current symptom, skip update
    if not symptom_state.current_symptom:
        return {**state, "current_action": "determine_next_action"}

    current_symptom = symptom_state.current_symptom

    # Check if there are details for the current symptom
    if current_symptom in extracted_symptoms and extracted_symptoms[current_symptom]:
        # Update symptom details
        try:
            symptom_state.update_symptom_detail(
                current_symptom, extracted_symptoms[current_symptom]
            )
        except ValueError:
            # If symptom not found, skip update
            pass

    # Update state
    return {
        **state,
        "symptom_state": symptom_state,
        "current_action": "determine_next_action",
    }


def determine_next_action(state: ConversationState) -> ConversationState:
    """Determine the next action based on the current state."""
    symptom_state = state["symptom_state"]

    # If no symptoms, generate response
    if not symptom_state.primary_symptoms:
        return {**state, "current_action": "generate_response"}

    # If no current symptom, select one
    if not symptom_state.current_symptom:
        if symptom_state.primary_symptoms:
            symptom_state.current_symptom = symptom_state.primary_symptoms[0]
        else:
            return {**state, "current_action": "generate_response"}

    current_symptom = symptom_state.current_symptom

    # Check if there are missing fields for the current symptom
    try:
        missing_fields = symptom_state.missing_fields(current_symptom)
    except ValueError:
        # If symptom not found in primary_symptoms
        return {**state, "current_action": "generate_response"}

    if missing_fields:
        # There are missing fields, ask about the top MAX_MISSING_FIELDS_TO_ASK fields
        top_missing_fields = missing_fields[:MAX_MISSING_FIELDS_TO_ASK]
        return {
            **state,
            "symptom_state": symptom_state,
            "missing_fields": top_missing_fields,
            "current_action": "generate_question",
        }
    else:
        # No missing fields for current symptom, rotate to next symptom
        symptom_state.rotate_current_symptom()

        # Check if the new current symptom has missing fields
        if symptom_state.current_symptom:
            new_missing_fields = symptom_state.missing_fields(
                symptom_state.current_symptom
            )
            if new_missing_fields:
                return {
                    **state,
                    "symptom_state": symptom_state,
                    "missing_fields": new_missing_fields,
                    "current_action": "generate_question",
                }

        # If no missing fields for any symptom, generate response
        return {
            **state,
            "symptom_state": symptom_state,
            "current_action": "generate_response",
        }


def generate_question(state: ConversationState) -> ConversationState:
    """Generate a question about top N missing fields."""
    symptom_state = state["symptom_state"]
    missing_fields = state.get("missing_fields", [])

    # Check both if current_symptom is None or empty, and if missing_fields is empty
    if (
        not symptom_state.current_symptom
        or symptom_state.current_symptom is None
        or not missing_fields
    ):
        return {**state, "current_action": "generate_response"}

    current_symptom = symptom_state.current_symptom

    # Format the missing fields as a comma-separated list
    missing_fields_str = ", ".join(missing_fields)

    # Define the question prompt
    question_prompt = ChatPromptTemplate.from_template(
        """You are a medical assistant conducting a symptom assessment. 
        You need to ask about the {missing_fields_str} for the symptom "{symptom}".
        
        Ask a clear, specific question in a natural, empathetic tone.
        Structure your question concise and focused only on {missing_fields_str}.
        So that the user can understand what information you need.
        
        Previous conversation:
        {chat_history}
        
        Your question about the {missing_fields_str} for {symptom}:"""
    )

    # Format chat history for the prompt
    chat_history_text = "\n".join(
        [
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in state["chat_history"][-5:]  # Include only the last 5 messages
        ]
    )

    # Generate the questions
    response = llm.invoke(
        question_prompt.format(
            missing_fields_str=missing_fields_str,
            symptom=current_symptom,
            chat_history=chat_history_text,
        )
    )

    # Update state
    return {
        **state,
        "ai_response": response.content,
        "current_action": "update_history",
    }


def generate_response(state: ConversationState) -> ConversationState:
    """Generate a general response."""
    if not state["user_input"]:
        return {**state, "current_action": "update_history"}

    # Get relevant state components
    extracted_symptoms = state.get("extracted_symptoms", {})
    extracted_medications = state.get("extracted_medications", {})

    # Define the response prompt
    response_prompt = ChatPromptTemplate.from_template(
        """You are a medical assistant conducting a symptom assessment.
        
        Current symptoms being tracked: {symptoms}
        
        Medications mentioned or uploaded: {medications}
        
        Previous conversation:
        {chat_history}
        
        User's latest message: {user_input}
        
        Respond in a natural, empathetic tone. If the user has mentioned symptoms, acknowledge them.
        If symptoms and medications are both present, discuss potential connections between them.
        If medications are present without symptoms, ask if they're taking the medication for specific symptoms.
        If no symptoms or medications have been mentioned yet, ask the user what symptoms they're experiencing.
        
        After gathering symptom details and medications have not been mentioned yet:
        - Suggest they upload a medication label by saying "You can upload a photo of your medication label"
        - Or ask "Could you tell me about any medications you're currently taking?"
        
        Keep your response concise and focused.
        
        Your response:"""
    )

    # Format symptoms and chat history for the prompt
    symptoms_text = (
        ", ".join(extracted_symptoms.keys()) if extracted_symptoms else "None"
    )

    # Format medication information for the prompt
    medication_text = (
        ", ".join(extracted_medications.keys()) if extracted_medications else "None"
    )

    chat_history_text = "\n".join(
        [
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in state["chat_history"][-5:]  # Include only the last 5 messages
        ]
    )

    # Generate the response
    response = llm.invoke(
        response_prompt.format(
            symptoms=symptoms_text,
            medications=medication_text,
            chat_history=chat_history_text,
            user_input=state["user_input"],
        )
    )

    # Update state
    return {
        **state,
        "ai_response": response.content,
        "current_action": "update_history",
    }


def generate_summary(state: ConversationState) -> ConversationState:
    """Generate a summary of all symptoms."""
    symptom_state = state["symptom_state"]
    medication_state = state["medication_state"]

    summary = []
    if not symptom_state.primary_symptoms:
        summary.append("No symptoms have been recorded yet.")
    else:
        summary.append("\n" + symptom_state.get_session_summary())

    if not medication_state.label:
        summary.append("\nNo medications have been recorded yet.")
    else:
        summary.append("\n" + medication_state.get_session_summary())

    # Update state
    return {
        **state,
        "ai_response": "\n".join(summary),
        "current_action": "update_history",
    }


def chat(state: ConversationState) -> ConversationState:
    """Generate a greeting message."""
    # If there's user input, we should check for symptoms
    if state["user_input"]:
        return {
            **state,
            "current_action": check_symptom_context(
                state
            ),  # Use the function to determine the next action
        }

    # For initial greeting (no user input)
    greeting_prompt = ChatPromptTemplate.from_template(
        """You are a medical assistant designed to document symptoms.
        
        Generate a friendly, empathetic greeting that:
        1. Introduces yourself as a symptom documentation assistant
        2. Explains that you'll help document their symptoms in detail
        3. Asks what symptoms they're experiencing
        
        Keep it concise and conversational.
        
        Your greeting:"""
    )

    # Generate the greeting
    response = llm.invoke(greeting_prompt.format())

    # Update state
    return {
        **state,
        "ai_response": response.content,
        "current_action": "generate_response",
    }


def update_history(state: ConversationState) -> ConversationState:
    """Update the chat history with the latest user input and AI response."""
    chat_history = state["chat_history"].copy()

    # Add user message if it exists
    if state["user_input"]:
        chat_history.append({"role": "user", "content": state["user_input"]})

    # Add AI response
    chat_history.append({"role": "assistant", "content": state["ai_response"]})

    # Update state
    return {**state, "chat_history": chat_history, "current_action": END}


# Create the conversation graph
def create_conversation_graph() -> StateGraph:
    """Create the conversation graph."""
    # Initialize the workflow
    workflow = StateGraph(ConversationState)
    # Add nodes
    workflow.add_node("chat", chat)
    workflow.add_node("extract_symptoms", extract_symptoms)
    workflow.add_node("process_symptoms", process_symptoms)
    workflow.add_node("extract_details", extract_details)
    workflow.add_node("update_symptom_details", update_symptom_details)
    workflow.add_node("determine_next_action", determine_next_action)
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("generate_summary", generate_summary)
    workflow.add_node("prepare_medication_upload", prepare_medication_upload)
    workflow.add_node("extract_medication_labels", extract_medication_labels)
    workflow.add_node("update_history", update_history)
    # Add edges between nodes
    workflow.add_conditional_edges(
        "chat",
        lambda x: x["current_action"],
        {
            "extract_symptoms": "extract_symptoms",
            "generate_response": "generate_response",
            "generate_summary": "generate_summary",
            "prepare_medication_upload": "prepare_medication_upload",
        },
    )
    workflow.add_edge("extract_symptoms", "process_symptoms")
    workflow.add_edge("process_symptoms", "extract_details")
    workflow.add_edge("extract_details", "update_symptom_details")
    workflow.add_edge("update_symptom_details", "determine_next_action")
    # Conditional edges from determine_next_action
    workflow.add_conditional_edges(
        "determine_next_action",
        lambda x: x["current_action"],
        {
            "generate_question": "generate_question",
            "generate_response": "generate_response",
        },
    )

    # All responses lead to update_history
    workflow.add_edge("generate_question", "update_history")
    workflow.add_edge("generate_response", "update_history")
    workflow.add_edge("generate_summary", "update_history")
    workflow.add_edge("extract_medication_labels", "update_history")

    # Add conditional edges from prepare_medication_upload based on current_action
    workflow.add_conditional_edges(
        "prepare_medication_upload",
        lambda x: x["current_action"],
        {
            "extract_medication_labels": "extract_medication_labels",
            "generate_response": "generate_response",
        },
    )

    # Set entry point
    workflow.set_entry_point("chat")

    # Compile the graph
    return workflow.compile()


# Create the conversation agent
conversation_graph = create_conversation_graph()


# Visualize the workflow
def display_workflow():
    """Display the workflow as a Mermaid diagram."""
    # Get the Mermaid markdown content directly
    mermaid_code = conversation_graph.get_graph(xray=1).draw_mermaid()

    # Save to a temporary file
    temp_dir = tempfile.gettempdir()
    mermaid_path = os.path.join(temp_dir, "workflow_diagram.mmd")
    html_path = os.path.join(temp_dir, "workflow_diagram.html")

    # Write the Mermaid markdown to the file
    with open(mermaid_path, "w") as f:
        f.write(mermaid_code)

    # Create an HTML file with embedded Mermaid that works offline
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Workflow Diagram</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{ startOnLoad: true }});
        </script>
    </head>
    <body>
        <div class="mermaid">
{mermaid_code}
        </div>
    </body>
    </html>
    """

    with open(html_path, "w") as f:
        f.write(html_content)

    # Open the HTML file with the default web browser
    print(f"Opening workflow diagram at: {html_path}")
    try:
        os.startfile(html_path)  # This works on Windows
    except AttributeError:
        # Fallback for non-Windows systems
        try:
            webbrowser.open(f"file://{html_path}")
        except Exception as e:
            print(f"Could not open the HTML file: {e}")
            print(f"The diagram has been saved to: {mermaid_path}")
            print(f"The HTML viewer has been saved to: {html_path}")

    # Also print the Mermaid code to console for reference
    print("\nMermaid diagram code:")
    print(mermaid_code)

    return mermaid_code


# Set configuration
config = {"configurable": {"thread_id": "1", "user_id": "1"}}


# Function to process user input
def process_user_input(
    user_input: str, state: Optional[ConversationState] = None
) -> Tuple[str, ConversationState]:
    """Process user input and return the AI response and updated state."""
    # Initialize state if not provided
    if state is None:
        state = initialize_state()
        # Run the graph to get the greeting
        state = conversation_graph.invoke(state)
        return state["ai_response"], state

    # Update state with user input
    state = {
        **state,
        "user_input": user_input,
        "current_action": "check_symptom_context",  # Set to our new conditional check
    }

    # Run the graph
    state = conversation_graph.invoke(state)

    # Return the AI response and updated state
    return state["ai_response"], state


if __name__ == "__main__":
    print("\nDisplaying conversation workflow diagram...")
    display_workflow()
