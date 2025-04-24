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
from langgraph.graph import StateGraph

# from langchain.agents import Tool, AgentExecutor
from langchain_core.tools import ToolException
from pydantic import BaseModel, Field
import pytesseract
from PIL import Image
import sqlite3
from datetime import datetime
import uuid

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

        # Ensure I missed the call but they left a message saying we need to go pick up Eris well maybe her belly stick shall we take her to a urgent care Yeah let's take the first time and let them know you're doing OK Hi this is Lindy i'm iris small we have a proper path to the image file
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


# Step 2: Pydantic Schema for Medication Data
class MedicationLabel(BaseModel):
    pharmacy_name: str = Field(default="")
    pharmacy_address: str = Field(default="")
    pharmacy_phone: str = Field(default="")
    patient_name: str = Field(default="")
    patient_address: str = Field(default="")
    drug_name: str = Field(...)  # required field
    drug_strength: str = Field(default="")
    drug_instructions: str = Field(default="")
    pill_markings: str = Field(default="")
    manufacturer: str = Field(default="")
    ndc_upc: str = Field(default="")
    rx_written_date: str = Field(default="")
    discard_after: str = Field(default="")
    federal_caution: str = Field(default="")
    rx_number: str = Field(default="")
    refill_count: int = Field(default=0)
    prescriber_name: str = Field(default="")
    reorder_after: str = Field(default="")
    qty_filled: int = Field(default=0)
    location_code: str = Field(default="")
    filled_date: str = Field(default="")
    pharmacist: str = Field(default="")
    barcode: str = Field(default="")


# Step 3: Agentic pipeline for Structuring Text
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


# Step 4: SQLite for Storing Medications
def store_medication(user_id: str, label: MedicationLabel):
    conn = sqlite3.connect("bayman_agentx_health.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS medications (
            user_id UUID,
            label_uploaded_datetime DATETIME,
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


# Step 5: LangGraph State and Nodes
class MedicationProcessState(BaseModel):
    user_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique user ID"
    )
    filename: str = Field(
        default="data/drug_labels/prescription label example.png",
        description="Path to the medication label image",
    )
    raw_text: str = ""
    label: MedicationLabel | None = None
    validated: bool = False

    def get_medication_summary(self) -> str:
        """Get a summary of the medication in the current state."""
        if not self.label:
            return "No medication information available."

        label = self.label
        summary = [f"Medication: {label.drug_name}"]

        if label.drug_strength:
            summary.append(f"Strength: {label.drug_strength}")

        if label.drug_instructions:
            summary.append(f"Instructions: {label.drug_instructions}")

        if label.pharmacy_name:
            summary.append(f"Pharmacy: {label.pharmacy_name}")

        if label.pharmacy_phone:
            summary.append(f"Pharmacy Phone: {label.pharmacy_phone}")

        if label.prescriber_name:
            summary.append(f"Prescribed by: {label.prescriber_name}")

        if label.rx_number:
            summary.append(f"Rx Number: {label.rx_number}")

        if label.filled_date:
            summary.append(f"Filled Date: {label.filled_date}")

        if label.discard_after:
            summary.append(f"Discard After: {label.discard_after}")

        if label.refill_count:
            summary.append(f"Refills Remaining: {label.refill_count}")

        if label.qty_filled:
            summary.append(f"Quantity: {label.qty_filled}")

        if label.federal_caution:
            summary.append(f"Warning: {label.federal_caution}")

        if label.patient_name:
            summary.append(f"Patient: {label.patient_name}")

        return "\n".join(summary)


def get_session_summary(self) -> str:
    """Get a summary of all medications in the session."""
    if not self.label:
        return "No medication information available."

    summary = []
    for medication in self.medications:
        summary.append(medication.get_medication_summary())

    return "\n\n".join(summary)


def ocr_step(state: MedicationProcessState) -> MedicationProcessState:
    text = parse_label_image.run(state.filename)
    return state.model_copy(update={"raw_text": text})


def extract_step(state: MedicationProcessState) -> MedicationProcessState:
    # TODO: Possibly clean up text here before passing to LLM
    label = extract_structured_data.invoke({"raw_text": state.raw_text})
    return state.model_copy(update={"label": label})


def human_validation(state: MedicationProcessState) -> MedicationProcessState:
    # Human validation step
    print("\nPlease review the extracted medication information:")
    print("====================================")

    # Convert label to dict for easier manipulation
    label_dict = state.label.model_dump()

    # Present each field to user for validation
    for field, value in label_dict.items():
        if value:  # Only show non-empty fields
            print(f"\n{field.replace('_', ' ').title()}: {value}")

            # TODO: implmenet the human validation step on the web page
            # valid = input("Is this information correct? (y/n): ").lower().strip()

            # if valid == "n":
            #     new_value = input(
            #         f"Please enter the correct {field.replace('_', ' ')}: "
            #     ).strip()
            #     if field in ["refill_count", "qty_filled"]:
            #         try:
            #             label_dict[field] = int(new_value) if new_value else 0
            #         except ValueError:
            #             print(f"Invalid input for {field}. Keeping original value.")
            #     else:
            #         label_dict[field] = new_value

    # Create new MedicationLabel instance with validated data
    # validated_label = MedicationLabel(**label_dict)

    return MedicationLabel(**label_dict)


def validate_step(state: MedicationProcessState) -> MedicationProcessState:

    # validated_label = human_validation(state)

    # Final confirmation before storing
    print("\nFinal Medication Information Summary:")
    print("====================================")
    for field, value in state.label.model_dump().items():
        if value:
            print(f"{field.replace('_', ' ').title()}: {value}")

    final_confirm = (
        input("\nStore this medication information in the database? (y/n): ")
        .lower()
        .strip()
    )

    if final_confirm == "y":
        store_medication(state.user_id, state.label)
        return state.model_copy(update={"validated": True, "label": state.label})
    else:
        return state.model_copy(update={"validated": False})


# # Using the tool in an agent
# tools = [
#     Tool(
#         name="OCR_Parser",
#         func=parse_label_image,
#         description="Extract text from medication label images",
#     )
# ]

# Build Graph
graph = StateGraph(MedicationProcessState)
graph.add_node("ocr", ocr_step)
graph.add_node("extract", extract_step)
graph.add_node("validate", validate_step)
graph.set_entry_point("ocr")
graph.add_edge("ocr", "extract")
graph.add_edge("extract", "validate")
graph.set_finish_point("validate")

drug_assistant = graph.compile()

# Example Run
if __name__ == "__main__":
    state = MedicationProcessState(
        # TEST USER
        user_id="7fdb7c3b-f5c2-493c-be52-ebf75ce74cc0",  # str(uuid.uuid4()), # Unique user ID
        # filename="data/drug_labels/DAYTIME_COLD_AND_FLU_NON_DROWSY.jpeg",
        filename="data/drug_labels/prescription label example.png",
    )
    result = drug_assistant.invoke(state)
    # Convert result to dict to access its values
    result_dict = dict(result)
    if "label" in result_dict:
        print("Medication Label:", result_dict["label"])
    print("Validated and stored in DB:", result_dict.get("validated", False))
