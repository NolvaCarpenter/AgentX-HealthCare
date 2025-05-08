from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph

# from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import PydanticOutputParser
# from langchain_core.runnables import RunnableMap


# from langchain.agents import Tool, AgentExecutor

import uuid


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


class MedicationProcessState(BaseModel):
    user_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique user ID"
    )
    filename: str = Field(
        default="data/drug_labels/prescription label example.png",
        description="Path to the medication label image",
    )
    raw_text: str = Field(
        default="",
        description="Raw text extracted from the medication label image",
    )
    label: Optional[MedicationLabel] = Field(
        default=None,
        description="Structured data extracted from the medication label",
    )
    validated: bool = Field(
        default=False,
        description="Flag indicating whether the medication label has been validated",
    )
    medications: List[MedicationLabel] = Field(
        default_factory=list,
        description="List of medications extracted from the label",
    )

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
        if not self.medications:
            return "No medication information available."

        summary = []
        for medication in self.medications:
            med_summary = [f"Medication: {medication.drug_name}"]

            if medication.drug_strength:
                med_summary.append(f"Strength: {medication.drug_strength}")

            if medication.drug_instructions:
                med_summary.append(f"Instructions: {medication.drug_instructions}")

            if medication.pharmacy_name:
                med_summary.append(f"Pharmacy: {medication.pharmacy_name}")

            summary.append("\n".join(med_summary))

        return "\n\n".join(summary)


# Build Graph workflow for processing medication images
def build_medication_workflow():
    from medications.medication_extraction import ocr_step, extract_step, validate_step

    graph = StateGraph(MedicationProcessState)
    graph.add_node("ocr", ocr_step)
    graph.add_node("extract", extract_step)
    graph.add_node("validate", validate_step)
    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "extract")
    graph.add_edge("extract", "validate")
    graph.set_finish_point("validate")

    return graph.compile()
