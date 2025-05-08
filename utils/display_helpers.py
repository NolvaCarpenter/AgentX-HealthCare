"""
Utility functions for formatting and displaying data in the Baymax application.
"""

import os
import tempfile
import webbrowser
import base64
import mimetypes
from typing import Dict, List, Tuple, Any, Optional


# Visualize the workflow
def display_workflow():
    """Display the workflow as a Mermaid diagram."""
    from conversation_agent import conversation_graph

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


def format_symptom_summary(state):
    """Format the symptom state into a readable markdown summary."""
    summary = "## Health Tracking\n\n"
    summary += "### Symptoms\n\n"

    # Get symptom_state from state
    symptom_state = state.get("symptom_state") if state else None

    # Handle symptoms summary - if no symptoms are recorded
    if (
        not symptom_state
        or not hasattr(symptom_state, "primary_symptoms")
        or not symptom_state.primary_symptoms
    ):
        summary += "No symptoms recorded yet\n\n"
    else:
        # Format each symptom with its details
        for symptom in symptom_state.primary_symptoms:
            summary += f"- **{symptom}**\n"

            # Add details if available
            if symptom in symptom_state.symptom_details:
                details = symptom_state.symptom_details[symptom]

                # Severity information
                if details.severity:
                    summary += f"  - Severity: Level {details.severity.level if details.severity.level is not None else 'Not specified'}\n"
                    if details.severity.description:
                        summary += (
                            f"    - Description: {details.severity.description}\n"
                        )

                # Duration information
                if details.duration:
                    if details.duration.start_date:
                        summary += f"  - Started: {details.duration.start_date}\n"
                    if details.duration.is_ongoing:
                        summary += f"  - Status: Ongoing\n"
                    elif details.duration.end_date:
                        summary += f"  - Ended: {details.duration.end_date}\n"

                # Additional symptom characteristics
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

                # Factors affecting symptoms
                if details.aggravating_factors:
                    summary += f"  - Aggravating factors: {', '.join(details.aggravating_factors)}\n"
                if details.relieving_factors:
                    summary += f"  - Relieving factors: {', '.join(details.relieving_factors)}\n"

                # Related information
                if details.associated_symptoms:
                    summary += f"  - Associated symptoms: {', '.join(details.associated_symptoms)}\n"
                if details.context:
                    summary += f"  - Context: {details.context}\n"

                summary += "\n"

    # Add medication information if available
    if state and "extracted_medications" in state and state["extracted_medications"]:
        summary += "### Medications\n\n"

        # Format each medication with its details
        for drug_name, medication in state["extracted_medications"].items():
            summary += f"- **{drug_name}**\n"

            # Medication details
            if hasattr(medication, "drug_strength") and medication.drug_strength:
                summary += f"  - Strength: {medication.drug_strength}\n"
            if (
                hasattr(medication, "drug_instructions")
                and medication.drug_instructions
            ):
                summary += f"  - Instructions: {medication.drug_instructions}\n"

            # Prescription details
            if hasattr(medication, "prescriber_name") and medication.prescriber_name:
                summary += f"  - Prescriber: {medication.prescriber_name}\n"
            if hasattr(medication, "pharmacy_name") and medication.pharmacy_name:
                summary += f"  - Pharmacy: {medication.pharmacy_name}\n"
            if hasattr(medication, "refill_count") and medication.refill_count:
                summary += f"  - Refills: {medication.refill_count}\n"

            # Warnings
            if hasattr(medication, "federal_caution") and medication.federal_caution:
                summary += f"  - Warning: {medication.federal_caution}\n"

            summary += "\n"

    return summary


def convert_image_to_data_url(image_path: str) -> Optional[str]:
    """
    Convert an image file to a data URL that can be displayed directly in HTML/markdown.

    Args:
        image_path (str): Path to the image file

    Returns:
        Optional[str]: Data URL representation of the image, or None if conversion fails
    """
    # Get MIME type based on file extension
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/jpeg"  # Default to jpeg if type can't be determined

    # Read the binary image data
    try:
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()

        # Encode as base64
        b64_encoded = base64.b64encode(img_data).decode("utf-8")

        # Create data URL
        data_url = f"data:{mime_type};base64,{b64_encoded}"
        return data_url
    except Exception as e:
        print(f"Error converting image to data URL: {e}")
        return None
