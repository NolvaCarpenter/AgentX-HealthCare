import re
import uuid
import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.graph import StateGraph, END
from typing import Dict, List, Any, TypedDict, Optional, Tuple, Literal

from symptoms.symptom_state import SymptomState, SymptomDetail, Severity, Duration
from symptoms.symptom_extraction import SymptomExtractor, SymptomDetailExtractor

from medications.medication_state import build_medication_workflow
from medications.medication_extraction import MedicationProcessState, MedicationLabel
from medications.handle_upload import validate_medication_image, get_available_samples

from conversation_thread import (
    create_new_thread,
    save_message,
    save_symptom_data,
    save_medication_data,
    get_symptom_data,
    get_medication_data,
)
import logging

from utils.display_helpers import display_workflow


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
    follow_up_count: int  # Counter for follow-up questions about current symptom
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
MAX_FOLLOW_UP_QUESTIONS = 3
SYMPTOM_COMPLETION_THRESHOLD = 0.4


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

    # Option 2: Generate a new thread ID if none was provided
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
        "follow_up_count": 0,
        "filename": "",
        "medication_state": MedicationProcessState(),
        "extracted_medications": {},
    }


def load_thread_state(thread_id: str, username: str) -> Dict[str, Any]:
    """
    Load the complete state for a given thread ID, including symptoms and medications data.

    Args:
        thread_id (str): The ID of the thread to load state for
        username (str): The current username

    Returns:
        Dict[str, Any]: A complete conversation state with loaded symptom and medication data
    """
    # Initialize state with the proper username
    state = initialize_state(username=username)
    state["thread_id"] = thread_id

    # Load symptom data from database
    symptom_data = get_symptom_data(thread_id)
    if symptom_data:
        print(
            f"Loaded symptom data for thread {thread_id}: {symptom_data.get('primary_symptoms', [])}"
        )
        symptom_state = SymptomState.model_validate(symptom_data)
        state["symptom_state"] = symptom_state
    else:
        print(f"No symptom data found for thread {thread_id}")

    # Load medication data from database
    medication_data = get_medication_data(thread_id)
    if medication_data:
        print(
            f"Loaded medication data for thread {thread_id}: {list(medication_data.keys())}"
        )

        # Convert medication data back to MedicationLabel objects
        extracted_medications = {}
        for drug_name, med_data in medication_data.items():
            extracted_medications[drug_name] = MedicationLabel.model_validate(med_data)
        state["extracted_medications"] = extracted_medications
    else:
        print(f"No medication data found for thread {thread_id}")

    return state


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
            ai_response = (
                "I couldn't extract any medication information from the uploaded image. "
                "Please ensure the image is clear and contains readable medication label information."
            )
            return {
                **state,
                "medication_state": processed_state,
                "ai_response": ai_response,
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
    """
    Function to detect symptom-related context in user input with improved accuracy,
    handling synonyms, layman terms, and contextual phrases.
    """
    from symptoms.symptom_synonyms import LAYMAN_TO_STANDARD

    # Configure logging
    logger = logging.getLogger("conversation_agent.check_symptom_context")

    user_input = state["user_input"]
    user_input = user_input.lower() if user_input else ""

    # For initial greeting, go directly to generate_response
    if not user_input:
        return "generate_response"

    # Check if user is requesting a summary
    if re.search(r"\b(summarize|recap)\b", user_input):
        logger.info("Summary request detected")
        return "generate_summary"

    # Check if user is uploading a medication label or if a filename is already set
    if (
        "upload" in user_input
        or "medication" in user_input
        or "medicine" in user_input
        or "prescription" in user_input
    ) and state.get("filename", ""):
        logger.info("Medication upload context detected")
        return "prepare_medication_upload"

    # default to symptom extraction if no specific context is detected
    # TODO: potentially optimze workflow to avoid unnecessary symptom extraction
    return "extract_symptoms"


def extract_symptoms(state: ConversationState) -> ConversationState:
    """Extract symptoms from user input."""

    # Configure logging
    logger = logging.getLogger("conversation_agent.extract_symptoms")

    user_input = state["user_input"]

    if not user_input:
        return state

    # Extract symptoms
    symptom_list = symptom_extractor.extract_symptoms(user_input)

    # Convert list to dictionary with empty details
    extracted_symptoms = {}
    for symptom in symptom_list:
        extracted_symptoms[symptom] = {}

    logger.info(f"Extracted symptoms: {extracted_symptoms}")

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

    # Update state with processed symptoms that match the keys in symptom_state
    return {
        **state,
        "symptom_state": symptom_state,
        "extracted_symptoms": extracted_symptoms,
        "current_action": "extract_details",
    }


def extract_details(state: ConversationState) -> ConversationState:
    """Extract details for the current symptom."""
    symptom_state = state["symptom_state"]
    user_input = state["user_input"]
    extracted_symptoms = state["extracted_symptoms"]

    # Get missing fields to extract from state
    missing_fields = state.get("missing_fields", [])

    # # If no current symptom, select one
    # if not symptom_state.current_symptom and symptom_state.primary_symptoms:
    #     symptom_state.current_symptom = symptom_state.primary_symptoms[0]

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

    # Increment the follow-up counter since we just processed a question
    follow_up_count = state.get("follow_up_count", 0) + 1

    # Update state
    return {
        **state,
        "symptom_state": symptom_state,
        "follow_up_count": follow_up_count,
        "current_action": "determine_next_action",
    }


def determine_next_action(state: ConversationState) -> ConversationState:
    """Determine the next action based on the current state."""

    # Configure logging
    logger = logging.getLogger("conversation_agent.determine_next_action")

    symptom_state = state["symptom_state"]
    follow_up_count = state.get("follow_up_count", 0)

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

    # Check if all symptom details are documented
    all_symptoms_documented = symptom_state.is_symptom_tracking_completed(
        SYMPTOM_COMPLETION_THRESHOLD
    )

    logger.info(
        f"All symptoms documented: {all_symptoms_documented}, current symptom: {current_symptom}"
    )

    if all_symptoms_documented:
        # If all symptoms are documented, suggest sharing with healthcare provider
        return {
            **state,
            "symptom_state": symptom_state,
            "current_action": "generate_healthcare_recommendation",
        }

    # Check if we should rotate to the next symptom
    # Rotate if:
    # 1. We've asked enough follow-up questions OR
    # 2. The current symptom is sufficiently documented (reached threshold percentage)
    should_rotate = follow_up_count >= MAX_FOLLOW_UP_QUESTIONS

    if should_rotate:
        # Rotate to next symptom and reset follow-up counter
        symptom_state.rotate_current_symptom()
        follow_up_count = 0
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
            "follow_up_count": follow_up_count,
            "current_action": "generate_question",
        }
    else:
        # No missing fields for current symptom, rotate to next symptom
        symptom_state.rotate_current_symptom()
        follow_up_count = 0

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
                    "follow_up_count": follow_up_count,
                    "current_action": "generate_question",
                }

        # If no missing fields for any symptom, generate response
        return {
            **state,
            "symptom_state": symptom_state,
            "follow_up_count": follow_up_count,
            "current_action": "generate_response",
        }


def generate_question(state: ConversationState) -> ConversationState:
    """
    Generate context-aware, medically-informed questions about missing symptom details.
    The questions are tailored based on the specific symptom and what details are missing.
    """
    from symptoms.medical_knowledge import get_follow_up_questions

    # Configure logging
    logger = logging.getLogger("conversation_agent.questions")

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

    # For tracking QA metrics
    qa_metrics = {
        "symptom": current_symptom,
        "missing_fields": missing_fields,
        "question_type": (
            "follow_up" if state.get("follow_up_count", 0) > 0 else "initial"
        ),
    }

    # Get medically-appropriate follow-up questions from our knowledge base
    suggested_questions = []
    for field in missing_fields[:MAX_MISSING_FIELDS_TO_ASK]:
        field_questions = get_follow_up_questions(current_symptom, field)
        if field_questions:
            suggested_questions.append(
                field_questions[0]
            )  # Take the first question for each field

    # Format suggested questions as string examples
    suggested_questions_str = "\n".join([f"- {q}" for q in suggested_questions])

    # Format the missing fields as a comma-separated list
    missing_fields_str = ", ".join(missing_fields[:MAX_MISSING_FIELDS_TO_ASK])

    # Check previously asked questions to avoid repetition
    previous_questions = []
    for message in state["chat_history"][-10:]:  # Look at last 10 messages
        if message["role"] == "assistant" and "?" in message["content"]:
            previous_questions.append(message["content"])

    previous_questions_str = "\n".join(
        [f"- {q}" for q in previous_questions[-3:]]
    )  # Last 3 questions

    # Define the question prompt with medical knowledge integration
    question_prompt = ChatPromptTemplate.from_template(
        """You are a medical assistant conducting a symptom assessment with expertise from Mayo Clinic and MedlinePlus guidelines.
        
        Current symptom: "{symptom}"
        Missing information: {missing_fields_str}
        
        Based on medical knowledge, here are suggested questions for this symptom and missing information:
        {suggested_questions}
        
        Previous questions you've asked (avoid repeating these):
        {previous_questions}
        
        Previous conversation context:
        {chat_history}
        
        Create ONE focused, medically accurate follow-up question in layman terms about the {missing_fields_str} for {symptom}.
        Your question should be:
        1. Concise (one or two sentences max)
        2. Specific to the symptom and missing field(s)
        3. Factual and never speculative
        4. Natural and empathetic in tone
        5. Different from questions you've already asked
        
        Your well-formed medical question:"""
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

    # Generate the question using the LLM
    response = llm.invoke(
        question_prompt.format(
            missing_fields_str=missing_fields_str,
            symptom=current_symptom,
            chat_history=chat_history_text,
            suggested_questions=suggested_questions_str,
            previous_questions=previous_questions_str,
        )
    )

    response.content = response.content.strip("\"'")
    qa_metrics["generated_question"] = response.content
    qa_metrics["completeness_score"] = len(missing_fields) / 8  # Simple metric

    # Log the question generation for evaluation
    logger.info(
        f"\nGenerated question for {current_symptom}: {response.content}"
        f"\nMissing fields: {missing_fields_str}, "
        f"and completeness score: {qa_metrics['completeness_score']}"
    )

    # Update state
    return {
        **state,
        "ai_response": response.content,
        "current_action": "update_history",
        "qa_metrics": qa_metrics,  # Store metrics for evaluation
    }


def generate_response(state: ConversationState) -> ConversationState:
    """
    Generate a factual, concise medical response based on validated information
    from trusted medical knowledge sources.
    """
    from utils.medical_fact_checker import (
        validate_medical_response,
        check_response_quality,
    )

    # Configure logging
    logger = logging.getLogger("conversation_agent.response")

    if not state["user_input"]:
        return {**state, "current_action": "update_history"}

    # Get relevant state components
    extracted_symptoms = state.get("extracted_symptoms", {})
    extracted_medications = state.get("extracted_medications", {})
    symptom_state = state.get("symptom_state")

    # Prepare symptom context for fact checking
    symptom_context = {
        "current_symptom": symptom_state.current_symptom if symptom_state else None,
        "primary_symptoms": symptom_state.primary_symptoms if symptom_state else [],
    }

    # Define the enhanced response prompt with medical fact guidelines
    response_prompt = ChatPromptTemplate.from_template(
        """You are a medical assistant conducting a symptom assessment, adhering strictly to clinical guidelines.
        
        Current symptoms being tracked: {symptoms}
        
        Medications mentioned or uploaded: {medications}
        
        Previous conversation:
        {chat_history}
        
        User's latest message: {user_input}
        
        STRICT GUIDELINES FOR YOUR RESPONSE:
        1. MAXIMUM LENGTH: Three concise sentences per point; no verbose explanations
        2. FACTUAL ONLY: Do not speculate about diagnoses or treatments
        3. MEDICALLY VALIDATED: Only include information verified by clinical guidelines
        4. NO URGENT MEDICAL ADVICE: For chest pain, difficulty breathing, severe symptoms always advise seeking immediate medical attention
        5. CLEAR BOUNDARIES: For complex medical questions, suggest consulting a healthcare professional
        
        If symptoms mentioned:
        - Acknowledge them with factual information
        - Do NOT suggest possible diagnoses
        - Focus on gathering more specific details
        
        If symptoms and medications both present:
        - Factually acknowledge potential connections without speculation
        
        Keep the response direct, concise, and factual.
        
        Your factual, concise response (max 2-3 sentences):"""
    )
    # Format symptoms and chat history for the prompt
    symptoms_text = (
        ", ".join(extracted_symptoms.keys()) if extracted_symptoms else "None"
    )
    # Format medication information for the prompt
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

    # Generate the initial response
    response = llm.invoke(
        response_prompt.format(
            symptoms=symptoms_text,
            medications=medication_text,
            chat_history=chat_history_text,
            user_input=state["user_input"],
        )
    )

    # Validate and improve the response using medical fact checker
    passed, validated_response, quality_metrics = check_response_quality(
        response.content, symptom_context
    )

    if not passed:
        logger.warning(f"Response failed quality check: {quality_metrics['issues']}")

        # Ensure the response is concise (max 2 sentences)
        validated_response = validate_medical_response(
            validated_response, max_sentences=2
        )

        logger.info("Applied medical fact validation to response")

    # Log metrics for evaluation
    response_metrics = {
        "original_length": len(response.content),
        "validated_length": len(validated_response),
        "quality_score": quality_metrics["overall_quality"],
        "issues": quality_metrics["issues"],
    }

    logger.info(
        f"Response metrics: {response_metrics['original_length']} -> {response_metrics['validated_length']} characters, "
        f"Quality score: {response_metrics['quality_score']}, Issues: {response_metrics['issues']}"
    )

    # Update state with the validated response and metrics
    return {
        **state,
        "ai_response": validated_response,
        "current_action": "update_history",
        "response_metrics": response_metrics,
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
    # TODO: deprecate the greeting prompt and use the hard-coded greeting message instead.
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


def generate_healthcare_recommendation(state: ConversationState) -> ConversationState:
    """Generate a response recommending sharing symptoms with healthcare provider."""
    # Configure logging
    logger = logging.getLogger(__name__ + ".generate_healthcare_recommendation")

    symptom_state = state["symptom_state"]

    # Create a symptom summary
    symptom_summary = symptom_state.get_session_summary()

    # Define the healthcare recommendation prompt
    healthcare_prompt = ChatPromptTemplate.from_template(
        """You are a medical assistant helping collect symptom information.
        
        The user has provided sufficient information about their symptoms. 
        Now you should suggest they share this information with their healthcare provider.
        
        Here's a summary of the symptoms they've described:
        
        {symptom_summary}
        
        Create a response that:
        1. Thanks the user for providing detailed information
        2. Summarizes the key symptoms they've reported
        3. Suggests they share this information with their healthcare provider
        4. Reminds them this is not a diagnosis
        5. Asks if they would like any clarification or have other questions
        
        Keep your response concise, empathetic and professional:
        """
    )

    # Generate the response using the LLM
    chain = healthcare_prompt | llm
    response = chain.invoke({"symptom_summary": symptom_summary})

    # Log the healthcare recommendation response
    logger.info(
        f"Generated healthcare recommendation: {response.content[:100]}... (truncated)"
    )

    # Return the updated state with the healthcare recommendation
    return {
        **state,
        "ai_response": response.content,
        "current_action": "update_history",
    }


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
    workflow.add_node(
        "generate_healthcare_recommendation", generate_healthcare_recommendation
    )
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
            "generate_healthcare_recommendation": "generate_healthcare_recommendation",
        },
    )

    # All responses lead to update_history
    workflow.add_edge("generate_question", "update_history")
    workflow.add_edge("generate_response", "update_history")
    workflow.add_edge("generate_summary", "update_history")
    workflow.add_edge("generate_healthcare_recommendation", "update_history")
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


def process_user_input(
    user_input: str,
    state: Optional[ConversationState] = None,
    thread_id: Optional[str] = None,
    username: str = "default_user",
) -> Tuple[str, ConversationState]:
    """Process user input and return the AI response and updated state."""

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

    # Run the graph with the thread_id in the config
    graph_configurable = {
        "thread_id": state["thread_id"],
        "user_id": state["user_id"] or username,
    }
    graph_config = {"configurable": graph_configurable}
    state = conversation_graph.invoke(state, graph_config)

    # Save assistant's response to the thread
    if thread_id and state["ai_response"]:
        save_message(thread_id, "assistant", state["ai_response"])

    # Save symptom data if there are any symptoms
    if (
        thread_id
        and "symptom_state" in state
        and state["symptom_state"].primary_symptoms
    ):
        # Prepare symptom data for serialization
        symptom_data = state["symptom_state"].model_dump()
        save_symptom_data(thread_id, symptom_data)

    # Save medication data if there are any medications
    if (
        thread_id
        and "extracted_medications" in state
        and state["extracted_medications"]
    ):
        # Convert medication data to serializable format
        medication_data = {}
        for drug_name, medication in state["extracted_medications"].items():
            medication_data[drug_name] = medication.model_dump()
        save_medication_data(thread_id, medication_data)

    # Return the AI response and updated state
    return state["ai_response"], state


if __name__ == "__main__":
    print("\nDisplaying conversation workflow diagram...")
    display_workflow()
