from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.graph import StateGraph, END
from typing import Dict, List, Any, TypedDict, Optional, Tuple, Literal
import os
import tempfile
import webbrowser
import uuid
import datetime

from symptoms.symptom_state import SymptomState, SymptomDetail, Severity, Duration
from symptoms.symptom_extraction import SymptomExtractor, SymptomDetailExtractor

from medications.medication_state import build_medication_workflow
from medications.medication_extraction import MedicationProcessState, MedicationLabel
from medications.handle_upload import validate_medication_image, get_available_samples

from conversation_thread import create_new_thread, save_message


# Define the state schema for the conversation graph
class ConversationState(TypedDict):
    user_id: str
    thread_id: str  # Unique identifier for each conversation thread
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
MAX_CHAT_HISTORY_LENGTH = 5  # Maximum number of chat history messages to keep


# Define the nodes for the conversation graph
def initialize_state(
    configurable=None, username: str = "default_user"
) -> ConversationState:
    """Initialize the conversation state.

    Args:
        configurable: Optional configuration object provided by LangGraph
        username: The username of the current user
    """
    # Check if a thread_id is provided in various sources
    thread_id = None

    # Option 1: Check the configurable parameter from LangGraph
    if configurable and isinstance(configurable, dict) and "thread_id" in configurable:
        thread_id = configurable.get("thread_id")
        print(f"[INFO] Using thread_id from LangGraph configurable: {thread_id}")

    # Option 2: Check the module-level config
    # TODO: this global config is not thread-safe, need to be fixed in the future.
    elif "configurable" in config and "thread_id" in config["configurable"]:
        thread_id = config["configurable"]["thread_id"]
        print(f"[INFO] Using thread_id from module config: {thread_id}")

    # Option 3: Generate a new thread ID if none was provided
    if not thread_id:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        thread_id = f"{timestamp}-{str(uuid.uuid4())[:8]}"
        print(f"[INFO] Generated new thread_id: {thread_id}")

    # Get user_id from configurable or use provided username
    user_id = username
    if configurable and isinstance(configurable, dict) and "user_id" in configurable:
        user_id = configurable.get("user_id")

    return {
        "user_id": user_id,
        "thread_id": thread_id,
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
    # Check if filename is already in state (from Gradio upload)
    if state.get("filename", ""):
        filename = state["filename"]
        print(f"Using uploaded file from Gradio: {filename}")
        valid_filename = filename  # Assume the file is already validated by process_medication_upload

        # Return updated state with the filename and next action
        return {
            **state,
            "filename": valid_filename,
            "current_action": "extract_medication_labels",
        }
    else:
        # Fall back to command line input for non-Gradio interfaces
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
            # Return updated state with the filename and next action
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

    print(f"Processing medication image: {filename}")

    # Update the medication state with the filename and user_id
    medication_state.filename = filename
    medication_state.user_id = state["user_id"]

    try:
        # Run the medication workflow to extract information
        medication_workflow = build_medication_workflow()
        processed_state = medication_workflow.invoke(medication_state)

        # If processed_state is an AdjustableValueDict, convert it to a MedicationProcessState
        if isinstance(processed_state, dict):
            processed_state = MedicationProcessState(**processed_state)

        # Get the extracted medication label
        extracted_label = processed_state.label

        # Format a response message based on the extraction results
        if extracted_label and extracted_label.drug_name:
            # If a medication was successfully extracted, add it to extracted_medications
            extracted_medications = state.get("extracted_medications", {})
            drug_name = extracted_label.drug_name

            # Create a nicely formatted response
            response_parts = [
                f"I've successfully processed your medication label for **{drug_name}**."
            ]

            # Add key medication details if available
            details = []
            if extracted_label.drug_strength:
                details.append(f"Strength: {extracted_label.drug_strength}")
            if extracted_label.drug_instructions:
                details.append(f"Instructions: {extracted_label.drug_instructions}")
            if extracted_label.pharmacy_name:
                details.append(f"Pharmacy: {extracted_label.pharmacy_name}")
            if extracted_label.prescriber_name:
                details.append(f"Prescriber: {extracted_label.prescriber_name}")

            if details:
                response_parts.append("Here are the key details:")
                for detail in details:
                    response_parts.append(f"- {detail}")

            response_parts.append(
                "This information has been stored for reference. Is there anything else you'd like to know about this medication?"
            )

            ai_response = "\n\n".join(response_parts)
            extracted_medications[drug_name] = extracted_label

            return {
                **state,
                "medication_state": processed_state,
                "extracted_medications": extracted_medications,
                "ai_response": ai_response,
                "current_action": "update_history",
            }
        else:
            # If no medication was extracted or the OCR failed
            return {
                **state,
                "medication_state": processed_state,
                "ai_response": "I couldn't identify medication information from the uploaded image. Please make sure the image is clear and contains readable medication label information.",
                "current_action": "update_history",
            }

    except Exception as e:
        print(f"Error processing medication image: {str(e)}")
        return {
            **state,
            "ai_response": f"I encountered an error while processing the medication label: {str(e)}. Please try uploading a clearer image.",
            "current_action": "update_history",
        }


def check_symptom_context(state: ConversationState) -> str:
    """Check if user input contains symptom-related context and return the next node."""
    user_input = state["user_input"]

    # For initial greeting, go directly to generate_response
    if not user_input:
        return "generate_response"

    # Check if user is requesting a summary
    if "summary" in user_input.lower() or "summarize" in user_input.lower():
        return "generate_summary"

    # Check if user is uploading a medication label or if a filename is already set
    # This handles both text commands and direct uploads via the Gradio interface
    if (
        "upload" in user_input.lower()
        or "photo" in user_input.lower()
        or "medication label" in user_input.lower()
        or "process this medication" in user_input.lower()
        or state.get("filename", "")
    ):  # Check if a filename is already in state

        # If this is from a direct file upload and we're just processing the command
        if "process this medication label" in user_input.lower() and state.get(
            "filename", ""
        ):
            return "prepare_medication_upload"

        # If there's a user request to upload
        if any(
            term in user_input.lower()
            for term in ["upload", "photo", "medication label"]
        ):
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
        "treatment",
        "condition",
        "severity",
        "symptoms",
    ]

    # Add medication-related terms to check for medication context
    medication_indicators = [
        "medication",
        "medicine",
        "drug",
        "prescription",
        "pill",
        "tablet",
        "capsule",
        "dose",
        "pharmacy",
        "prescribe",
        "refill",
    ]

    # Check if any symptom indicator is present in user input
    is_symptom_related = any(
        indicator in user_input.lower() for indicator in symptom_indicators
    )

    # Check if any medication indicator is present but not about uploading
    is_medication_related = any(
        indicator in user_input.lower() for indicator in medication_indicators
    ) and not any(term in user_input.lower() for term in ["upload", "photo", "label"])

    # Return the next node as a string, not a dict
    if is_symptom_related:
        return "extract_symptoms"
    elif is_medication_related and state.get("extracted_medications"):
        # If talking about medications and we have medication data, use generate_response
        # The response generator will include medication information
        return "generate_response"
    else:
        # If not symptom-related or medication-related, generate a response and skip extraction
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
    processed_symptoms = {}

    # Add each extracted symptom to the symptom state
    for symptom in extracted_symptoms.keys():
        # symptom_state.add_symptom(symptom)

        # Track original symptom name before adding (it might be merged with a similar one)
        original_symptom = symptom
        similar_found, similar_symptom = symptom_state.find_similar_symptom(symptom)

        # Add symptom - will use existing one if similar found
        symptom_state.add_symptom(symptom)

        # Store the proper key to use for this symptom
        actual_symptom = similar_symptom if similar_found else symptom

        # Copy any details from the extracted symptom to the processed symptom dictionary
        # using the actual symptom name (which might be different if a similar one was found)
        if original_symptom in extracted_symptoms:
            processed_symptoms[actual_symptom] = extracted_symptoms[original_symptom]

    # Update state with processed symptoms that match the keys in symptom_state
    return {
        **state,
        "symptom_state": symptom_state,
        "extracted_symptoms": processed_symptoms,
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
            for msg in state["chat_history"][
                -MAX_CHAT_HISTORY_LENGTH:
            ]  # Include only the last 5 messages
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
    )  # Format medication information for the prompt
    medication_details = []
    if extracted_medications:
        for drug_name, medication in extracted_medications.items():
            med_info = [f"{drug_name}"]
            if medication.drug_strength:
                med_info.append(f"Strength: {medication.drug_strength}")
            if medication.drug_instructions:
                med_info.append(f"Instructions: {medication.drug_instructions}")
            medication_details.append(" - ".join(med_info))

        medication_text = "\n".join(medication_details)
    else:
        medication_text = "None"

    chat_history_text = "\n".join(
        [
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in state["chat_history"][
                -MAX_CHAT_HISTORY_LENGTH:
            ]  # Include only the last 5 messages
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


# Set configuration with default values
# TODO: remove this global config in the future.
config = {"configurable": {"user_id": "default_user", "thread_id": None}}


# Function to process user input
def process_user_input(
    user_input: str,
    state: Optional[ConversationState] = None,
    thread_id: Optional[str] = None,
    username: str = "default_user",
) -> Tuple[str, ConversationState]:
    """Process user input and return the AI response and updated state."""

    # Initialize state if not provided
    if state is None:
        if thread_id is None:
            thread_id = create_new_thread(username)

        # Initialize state with the configurable parameter and username
        graph_configurable = {
            "thread_id": thread_id,
            "user_id": username,
        }

        state = initialize_state(configurable=graph_configurable, username=username)

        # Run the graph to get the greeting with the configurable
        graph_config = {"configurable": graph_configurable}
        state = conversation_graph.invoke(state, graph_config)

        if state["ai_response"]:
            save_message(thread_id, "assistant", state["ai_response"])

        return state["ai_response"], state

    # Use the thread_id from the state if not explicitly provided
    if thread_id is None and "thread_id" in state:
        thread_id = state["thread_id"]

    # Save user message to the thread
    if thread_id:
        save_message(thread_id, "user", user_input)

    # Update state with user input
    state = {
        **state,
        "user_input": user_input,
        "thread_id": thread_id,
        "current_action": "check_symptom_context",  # Set to our new conditional check
    }

    # Create the configurable object for LangGraph
    graph_configurable = {
        "thread_id": state["thread_id"],
        "user_id": state["user_id"] or username,
    }

    # Run the graph with the thread_id in the config
    graph_config = {"configurable": graph_configurable}
    state = conversation_graph.invoke(state, graph_config)

    # Save assistant's response to the thread
    if thread_id and state["ai_response"]:
        save_message(thread_id, "assistant", state["ai_response"])

    # Return the AI response and updated state
    return state["ai_response"], state


if __name__ == "__main__":
    print("\nDisplaying conversation workflow diagram...")
    display_workflow()
