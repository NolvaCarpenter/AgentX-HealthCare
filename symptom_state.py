from typing import List, Dict, Optional
from pydantic import BaseModel, Field


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
        description="List of symptom names to track. For example: ['headache', 'fever']"
    )
    symptom_details: Dict[str, SymptomDetail] = Field(
        default_factory=dict,
        description="Details of each symptom. The key is the symptom name, and the value is a SymptomDetail object. For example: {'headache': SymptomDetail(...)}"
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="List of follow-up questions. For example: ['Have you experienced this symptom before?', 'How long does it last?']"
    )
    current_symptom: Optional[str] = Field(
        default=None,
        description="The symptom currently being discussed"
    )

    def add_symptom(self, symptom_name: str):
        """Add a new symptom to the state."""
        # Check if the symptom already exists in the primary symptoms list
        if symptom_name not in self.primary_symptoms:
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
            
        current_index = self.primary_symptoms.index(self.current_symptom)
        next_index = (current_index + 1) % len(self.primary_symptoms)
        self.current_symptom = self.primary_symptoms[next_index]
    
    def get_symptom_summary(self, symptom_name: str) -> str:
        """Get a summary of a symptom's details."""
        if symptom_name not in self.primary_symptoms:
            raise ValueError(f"Symptom '{symptom_name}' not found in primary symptoms.")
        
        detail = self.symptom_details.get(symptom_name)
        if not detail:
            return f"Symptom: {symptom_name} (No details available)"
        
        summary = [f"Symptom: {symptom_name}"]
        
        if detail.severity and detail.severity.level is not None:
            summary.append(f"Severity: {detail.severity.level}/10")
            if detail.severity.description:
                summary.append(f"Description: {detail.severity.description}")
        
        if detail.duration:
            duration_info = []
            if detail.duration.start_date:
                duration_info.append(f"Started: {detail.duration.start_date}")
            if detail.duration.is_ongoing is not None:
                status = "Ongoing" if detail.duration.is_ongoing else "Resolved"
                duration_info.append(f"Status: {status}")
            if detail.duration.end_date and not detail.duration.is_ongoing:
                duration_info.append(f"Ended: {detail.duration.end_date}")
            if duration_info:
                summary.append("Duration: " + ", ".join(duration_info))
        
        if detail.characteristics:
            summary.append(f"Characteristics: {', '.join(detail.characteristics)}")
        
        if detail.location:
            summary.append(f"Location: {detail.location}")
            
        if detail.quality:
            summary.append(f"Quality: {detail.quality}")
            
        if detail.frequency:
            summary.append(f"Frequency: {detail.frequency}")
            
        if detail.intensity:
            summary.append(f"Intensity: {detail.intensity}")
            
        if detail.triggers:
            summary.append(f"Triggers: {', '.join(detail.triggers)}")
            
        if detail.aggravating_factors:
            summary.append(f"Aggravating factors: {', '.join(detail.aggravating_factors)}")
            
        if detail.relieving_factors:
            summary.append(f"Relieving factors: {', '.join(detail.relieving_factors)}")
            
        if detail.associated_symptoms:
            summary.append(f"Associated symptoms: {', '.join(detail.associated_symptoms)}")
        
        return "\n".join(summary)
    
    def get_session_summary(self) -> str:
        """Get a summary of all symptoms in the session."""
        if not self.primary_symptoms:
            return "No symptoms have been recorded."
        
        summaries = []
        for symptom in self.primary_symptoms:
            summaries.append(self.get_symptom_summary(symptom))
            
        return "\n\n".join(summaries)
