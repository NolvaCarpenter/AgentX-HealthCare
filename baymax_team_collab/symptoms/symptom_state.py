from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
import re


class Severity(BaseModel):
    level: Optional[int] = None  # Scale 1–10
    description: Optional[str] = None


class Duration(BaseModel):
    start_date: Optional[str] = None  # ISO format string "YYYY-MM-DDTHH:MM:SS"
    end_date: Optional[str] = None  # ISO format string "YYYY-MM-DDTHH:MM:SS"
    is_ongoing: Optional[bool] = None


class SymptomDetail(BaseModel):
    name: Optional[str] = None
    severity: Optional[Severity] = None
    duration: Optional[Duration] = None
    characteristics: Optional[List[str]] = None
    location: Optional[str] = None
    quality: Optional[str] = None
    timing: Optional[str] = None
    context: Optional[str] = None
    onset: Optional[str] = None
    frequency: Optional[str] = None
    intensity: Optional[str] = None
    triggers: Optional[List[str]] = None
    aggravating_factors: Optional[List[str]] = None
    relieving_factors: Optional[List[str]] = None
    associated_symptoms: Optional[List[str]] = None


class SymptomState(BaseModel):
    primary_symptoms: List[str] = Field(
        default_factory=list,
        description="List of symptom names to track. For example: ['headache', 'fever']",
    )
    symptom_details: Dict[str, SymptomDetail] = Field(
        default_factory=dict,
        description="Details of each symptom. The key is the symptom name, and the value is a SymptomDetail object. For example: {'headache': SymptomDetail(...)}",
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="List of follow-up questions. For example: ['Have you experienced this symptom before?', 'How long does it last?']",
    )
    current_symptom: Optional[str] = Field(
        default=None, description="The symptom currently being discussed"
    )

    def find_similar_symptom(self, symptom_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a similar symptom already exists in the primary symptoms list.

        Args:
            symptom_name (str): The symptom name to check against existing symptoms

        Returns:
            Tuple[bool, Optional[str]]: A tuple containing:
                - bool: True if a similar symptom was found, False otherwise
                - Optional[str]: The name of the similar symptom if found, None otherwise
        """
        if not symptom_name:
            return False, None

        # Normalize the symptom name (lowercase and strip any punctuation)
        normalized_name = symptom_name.lower().strip()

        # Direct match check
        for existing in self.primary_symptoms:
            if existing.lower() == normalized_name:
                return True, existing

        # Check if the symptom is a subset of an existing symptom or vice versa
        for existing in self.primary_symptoms:
            existing_lower = existing.lower()

            # Check if one is contained within the other
            if normalized_name in existing_lower or existing_lower in normalized_name:
                return True, existing

            # Check for descriptive modifiers like "mild fever" vs "fever"
            # Extract the base symptom by removing common modifiers
            modifiers = [
                "mild",
                "severe",
                "slight",
                "extreme",
                "moderate",
                "chronic",
                "acute",
            ]

            # Check if normalized_name contains any modifier + existing_symptom
            for modifier in modifiers:
                if (
                    f"{modifier} {existing_lower}" == normalized_name
                    or f"{existing_lower} {modifier}" == normalized_name
                ):
                    return True, existing

                # Also check if existing contains any modifier + normalized_name
                if (
                    f"{modifier} {normalized_name}" == existing_lower
                    or f"{normalized_name} {modifier}" == existing_lower
                ):
                    return True, existing

        return False, None

    def add_symptom(self, symptom_name: str):
        """Add a new symptom to the state."""
        # Skip empty symptom names
        if not symptom_name:
            return

        # Check for similar symptoms first
        similar_found, similar_symptom = self.find_similar_symptom(symptom_name)

        if similar_found:
            # If a similar symptom was found, don't add a new one and use the existing one
            symptom_name = similar_symptom
        elif symptom_name not in self.primary_symptoms:
            # If no similar symptom was found and this is a new symptom, add it
            self.primary_symptoms.append(symptom_name)
            self.symptom_details[symptom_name] = SymptomDetail(name=symptom_name)

        # Set as current symptom if none is set
        if self.current_symptom is None:
            self.current_symptom = symptom_name

    def update_symptom_detail(self, symptom_name: str, detail: Dict):
        """Update the details of an existing symptom."""
        # Check if the symptom exists in the primary symptoms list
        if symptom_name not in self.primary_symptoms:
            raise ValueError(f"Symptom '{symptom_name}' not found in primary symptoms.")

        # Update the symptom detail with new information
        # If the symptom does not exist, add it first
        if symptom_name not in self.symptom_details:
            self.add_symptom(symptom_name)
        updated_detail = self.symptom_details[symptom_name].model_copy(update=detail)
        self.symptom_details[symptom_name] = updated_detail

    def missing_fields(self, symptom_name: str) -> List[str]:
        """Identify missing fields for follow-up"""
        # This function checks if certain fields are missing in the symptom details
        # and returns a list of those fields.
        # The fields checked are severity, duration, characteristics, aggravating_factors, and relieving_factors.

        if symptom_name not in self.primary_symptoms:
            raise ValueError(f"Symptom '{symptom_name}' not found in primary symptoms.")
        missing = []
        detail = self.symptom_details.get(symptom_name)
        if detail:
            if not detail.severity or detail.severity.level is None:
                missing.append("severity")
            if not detail.duration or detail.duration.start_date is None:
                missing.append("start_date")
            if detail.duration and detail.duration.is_ongoing is None:
                missing.append("is_ongoing")
            if not detail.characteristics:
                missing.append("characteristics")
            if not detail.aggravating_factors:
                missing.append("aggravating_factors")
            if not detail.relieving_factors:
                missing.append("relieving_factors")
            if not detail.frequency:
                missing.append("frequency")
            if not detail.intensity:
                missing.append("intensity")
            if not detail.triggers:
                missing.append("triggers")
            if not detail.associated_symptoms:
                missing.append("associated_symptoms")
        return missing

    def get_next_missing_field(self, symptom_name: str) -> Optional[str]:
        """Get the next missing field for a symptom."""
        missing = self.missing_fields(symptom_name)
        return missing[0] if missing else None

    def rotate_current_symptom(self):
        """Rotate to the next symptom in the list."""
        if not self.primary_symptoms:
            return

        if self.current_symptom is None:
            self.current_symptom = self.primary_symptoms[0]
            return

        # Safety check: make sure current_symptom is in primary_symptoms
        try:
            current_index = self.primary_symptoms.index(self.current_symptom)
            next_index = (current_index + 1) % len(self.primary_symptoms)
            self.current_symptom = self.primary_symptoms[next_index]
        except ValueError:
            # If current_symptom is not in primary_symptoms, reset to first symptom
            if self.primary_symptoms:
                self.current_symptom = self.primary_symptoms[0]
            else:
                self.current_symptom = None

    def get_symptom_summary(self, symptom_name: str) -> str:
        """Get a summary of a symptom's details in a human-readable format."""
        if symptom_name not in self.primary_symptoms:
            raise ValueError(f"Symptom '{symptom_name}' not found in primary symptoms.")

        detail = self.symptom_details.get(symptom_name)
        if not detail:
            return f"Symptom: {symptom_name} (No details available)"

        # Use a cleaner format with a title and proper indentation
        summary = [f"Symptom: {symptom_name}"]

        # Format severity with a visual indicator
        if detail.severity and detail.severity.level is not None:
            severity_level = detail.severity.level
            severity_bar = "■" * severity_level + "□" * (10 - severity_level)
            summary.append(f"Severity: {severity_level}/10 [{severity_bar}]")
            if detail.severity.description:
                summary.append(f"  Description: {detail.severity.description}")

        # Format duration in a more structured way
        if detail.duration:
            duration_parts = []
            if detail.duration.start_date:
                # Make the date format more readable
                date = (
                    detail.duration.start_date.split("T")[0]
                    if "T" in detail.duration.start_date
                    else detail.duration.start_date
                )
                duration_parts.append(f"Started: {date}")

            if detail.duration.is_ongoing is not None:
                status = "✓ Ongoing" if detail.duration.is_ongoing else "✗ Resolved"
                duration_parts.append(f"Status: {status}")

            if detail.duration.end_date and not detail.duration.is_ongoing:
                end_date = (
                    detail.duration.end_date.split("T")[0]
                    if "T" in detail.duration.end_date
                    else detail.duration.end_date
                )
                duration_parts.append(f"Ended: {end_date}")

            if duration_parts:
                summary.append("Duration:")
                for part in duration_parts:
                    summary.append(f"  {part}")

        # Group similar categories together for better organization
        characteristic_info = []
        if detail.characteristics:
            characteristic_info.append(
                f"• Characteristics: {', '.join(detail.characteristics)}"
            )
        if detail.quality:
            characteristic_info.append(f"• Quality: {detail.quality}")
        if detail.intensity:
            characteristic_info.append(f"• Intensity: {detail.intensity}")

        if characteristic_info:
            summary.append("Clinical Characteristics:")
            summary.extend([f"  {info}" for info in characteristic_info])

        # Group location and timing together
        location_timing = []
        if detail.location:
            location_timing.append(f"• Location: {detail.location}")
        if detail.timing:
            location_timing.append(f"• Timing: {detail.timing}")
        if detail.frequency:
            location_timing.append(f"• Frequency: {detail.frequency}")

        if location_timing:
            summary.append("Location & Pattern:")
            summary.extend([f"  {info}" for info in location_timing])

        # Group factors together with clearer labeling
        factors = []
        if detail.triggers:
            factors.append(f"• Triggers: {', '.join(detail.triggers)}")
        if detail.aggravating_factors:
            factors.append(
                f"• Aggravating factors: {', '.join(detail.aggravating_factors)}"
            )
        if detail.relieving_factors:
            factors.append(
                f"• Relieving factors: {', '.join(detail.relieving_factors)}"
            )

        if factors:
            summary.append("Contributing Factors:")
            summary.extend([f"  {factor}" for factor in factors])

        # Associated information
        if detail.associated_symptoms:
            summary.append("Associated Symptoms:")
            summary.append(f"  • {', '.join(detail.associated_symptoms)}")

        # Add a separator line at the end for multiple symptom summaries
        summary.append("─" * 40)

        return "\n".join(summary)

    def get_session_summary(self) -> str:
        """Get a summary of all symptoms in the session."""
        if not self.primary_symptoms:
            return "No symptoms have been recorded."

        summaries = []
        for symptom in self.primary_symptoms:
            summaries.append(self.get_symptom_summary(symptom))

        return "\n\n".join(summaries)
