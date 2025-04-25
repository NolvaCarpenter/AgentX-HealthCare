# Required Libraries
import os
from langchain_core.tools import tool
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableMap
from langchain_core.tools import ToolException
import pytesseract
from PIL import Image
from medications.medication_state import MedicationLabel, MedicationProcessState

from langchain_core.tools import ToolException
import pytesseract
from PIL import Image
import sqlite3
from datetime import datetime

# Configurations
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# Step 1: OCR Tool
@tool
def parse_label_image(filename: str) -> str:
    """
    Parse the medication label image and extract text using OCR.

    Args:
        filename (str): Path to the image file.
    """
    try:
        # Get the base directory of the project
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Construct the proper path to the image file
        if os.path.isabs(filename):
            absolute_path = filename
        else:
            # For relative paths, join with base directory
            absolute_path = os.path.join(base_dir, filename)

        # Check if the file exists
        if not os.path.isfile(absolute_path):
            raise FileNotFoundError(f"Image file not found at: {absolute_path}")

        # Open and process the image
        image = Image.open(absolute_path)
        return pytesseract.image_to_string(image)
    except Exception as e:
        raise ToolException(f"Failed to process image: {str(e)}")


# Step 2: Agentic pipeline for Structuring Text
parser = PydanticOutputParser(pydantic_object=MedicationLabel)

llm = ChatOpenAI(model="gpt-4o", temperature=0)

system_prompt = SystemMessagePromptTemplate.from_template(
    """You are an expert pharmacist with extensive experience in reading and interpreting medication labels. 
    Your primary task is to:
    - Extract the brand name(s) if available from drug labels, if not drug or medication name(s).
    - Carefully extract medication details from prescription labels and pharmacy documentation.
    
    Important Guidelines:
    - Pay special attention to brand names or drug names, including both brand and generic names
    - Extract precise drug facts such as ingredient names, strength and purpose information
    - Extract precise dosage instructions and frequency
    - Note any special instructions or warnings
    - Identify key dates (prescription written, filled, expiry)
    - Look for refill information and quantity details
    - Capture all safety information and federal cautions
    - Use medical domain knowledge only to assist with disambiguation, not to assume missing content.    
    """
)

human_prompt = HumanMessagePromptTemplate.from_template(
    """Analyze the following medication label text and extract the relevant information:

    {text}

    Format the response according to these specifications:
    {format_instructions}

    Make sure to standardize drug names and include all available safety information. If certain fields are not present in the text, leave them empty rather than making assumptions.
    """
)

prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

runable = RunnableMap(
    {
        "text": lambda x: x["raw_text"],
        "format_instructions": lambda _: parser.get_format_instructions(),
    }
)

extract_structured_data = runable | prompt | llm | parser


# Step 3: LangGraph Steps
def ocr_step(state: MedicationProcessState) -> MedicationProcessState:
    """
    Execute OCR on the medication label image.

    Args:
        state: Current processing state

    Returns:
        Updated state with raw text extracted from the image
    """
    text = parse_label_image.run(state.filename)
    return state.model_copy(update={"raw_text": text})


def extract_step(state: MedicationProcessState) -> MedicationProcessState:
    """
    Extract structured medication data from raw OCR text.

    Args: There is some
        state: Current processing state with OCR text

    Returns:
        Updated state with structured medication label data
    """
    # Clean up text if needed before passing to LLM
    cleaned_text = state.raw_text.strip()

    # Extract structured data using LLM
    label = extract_structured_data.invoke({"raw_text": cleaned_text})

    return state.model_copy(update={"label": label})


def validate_step(state: MedicationProcessState) -> MedicationProcessState:
    """
    Validates the extracted medication information.
    In a production environment, this would include user interaction.
    """
    print("\nFinal Medication Information Summary:")
    print("====================================")
    for field, value in state.label.model_dump().items():
        if value:
            print(f"{field.replace('_', ' ').title()}: {value}")

    # In a real application, you would add user validation here
    # For now, we'll assume the information is correct
    final_confirm = (
        input("\nStore this medication information in the database? (y/n): ")
        .lower()
        .strip()
    )

    if final_confirm == "y":
        store_medication(state.user_id, state.label)

        # Add the validated label to the medications list
        updated_medications = state.medications.copy()
        updated_medications.append(state.label)

        return state.model_copy(
            update={"validated": True, "medications": updated_medications}
        )
    else:
        return state.model_copy(update={"validated": False})


def store_medication(user_id: str, label: MedicationLabel):
    conn = sqlite3.connect("bayman_agentx_health.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS medications (
            user_id TEXT,
            label_uploaded_datetime TEXT,
            pharmacy_name TEXT,
            pharmacy_address TEXT,
            pharmacy_phone TEXT,
            patient_name TEXT,
            patient_address TEXT,
            drug_name TEXT,
            drug_strength TEXT,
            drug_instructions TEXT,
            pill_markings TEXT,
            manufacturer TEXT,
            ndc_upc TEXT,
            rx_written_date TEXT,
            discard_after TEXT,
            federal_caution TEXT,
            rx_number TEXT,
            refill_count INTEGER,
            prescriber_name TEXT,
            reorder_after TEXT,
            qty_filled INTEGER,
            location_code TEXT,
            filled_date TEXT,
            pharmacist TEXT,
            barcode TEXT
        )
    """
    )
    c.execute(
        """
        INSERT INTO medications VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?
        )
    """,
        (
            user_id,
            datetime.now().isoformat(),  # Current datetime in ISO format
            label.pharmacy_name,
            label.pharmacy_address,
            label.pharmacy_phone,
            label.patient_name,
            label.patient_address,
            label.drug_name,
            label.drug_strength,
            label.drug_instructions,
            label.pill_markings,
            label.manufacturer,
            label.ndc_upc,
            label.rx_written_date,
            label.discard_after,
            label.federal_caution,
            label.rx_number,
            label.refill_count,
            label.prescriber_name,
            label.reorder_after,
            label.qty_filled,
            label.location_code,
            label.filled_date,
            label.pharmacist,
            label.barcode,
        ),
    )
    conn.commit()
    conn.close()


# Function to test the extraction pipeline
def test_medication_extraction(image_path: str):
    """
    Test the medication extraction pipeline on a single image.

    Args:
        image_path: Path to the medication label image

    Returns:
        Extracted MedicationLabel object
    """
    # Create initial state
    state = MedicationProcessState(filename=image_path)

    # Run OCR
    state = ocr_step(state)
    print(f"OCR Text Extracted: {len(state.raw_text)} characters")

    # Extract structured data
    state = extract_step(state)

    # Print summary
    print("\nExtracted Medication Information:")
    print("====================================")
    print(state.get_medication_summary())

    return state.label


# For testing in standalone mode
if __name__ == "__main__":
    test_image = "data/drug_labels/prescription label example.png"
    label = test_medication_extraction(test_image)
    print("\nComplete Label Data:")
    print(label.model_dump_json(indent=2))
