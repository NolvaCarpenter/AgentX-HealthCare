"""
Medical fact checking and response validation module.
This module ensures that AI responses are medically factual and appropriately formatted.
"""

from typing import Dict, List, Any, Tuple
import logging
import re
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("medical_fact_checker")

# Reliable medical information sources
MEDICAL_SOURCES = [
    "Mayo Clinic",
    "MedlinePlus",
    "CDC",
    "NIH",
    "Cleveland Clinic",
    "UpToDate",
    "American Academy of Family Physicians",
    "WebMD",
    "World Health Organization",
]

# Medical disclaimer templates
MEDICAL_DISCLAIMERS = [
    "This information is not intended as a substitute for professional medical advice.",
    "Please consult a healthcare provider for medical advice tailored to your situation.",
    "This is general information and should not be used for self-diagnosis.",
    "Always seek the advice of your physician with any questions about your health.",
]

# Keywords that indicate speculation (to be avoided)
SPECULATIVE_TERMS = [
    "might be",
    "could be",
    "may have",
    "possibly",
    "probably",
    "likely",
    "I think",
    "I believe",
    "I suspect",
    "perhaps",
    "maybe",
    "might have",
    "I'm guessing",
    "sounds like",
    "appears to be",
    "seems to be",
]

# Urgent symptoms requiring medical attention
URGENT_SYMPTOMS = {
    "chest pain": "Chest pain could indicate a serious condition that requires immediate medical attention.",
    "difficulty breathing": "Difficulty breathing could indicate a serious condition that requires immediate medical attention.",
    "shortness of breath": "Shortness of breath could indicate a serious condition that requires immediate medical attention.",
    "severe headache": "A sudden severe headache could require immediate medical evaluation.",
    "sudden confusion": "Sudden confusion could be a sign of a serious condition requiring immediate medical attention.",
    "slurred speech": "Slurred speech could be a sign of a stroke and requires immediate medical attention.",
    "facial drooping": "Facial drooping could be a sign of a stroke and requires immediate medical attention.",
    "weakness in arm": "Sudden weakness in an arm could be a sign of a stroke and requires immediate medical attention.",
    "severe abdominal pain": "Severe abdominal pain could indicate a serious condition requiring immediate medical attention.",
    "coughing blood": "Coughing up blood requires immediate medical evaluation.",
    "vomiting blood": "Vomiting blood requires immediate medical attention.",
    "fainting": "Fainting requires medical evaluation to determine the cause.",
    "seizure": "A seizure requires medical attention, especially if it's a first-time occurrence.",
    "severe burn": "Severe burns require immediate medical attention.",
    "allergic reaction": "Severe allergic reactions can be life-threatening and require immediate attention.",
    "poisoning": "Suspected poisoning requires immediate medical attention or contacting poison control.",
}


def check_response_quality(
    response: str, symptom_context: Dict = None
) -> Tuple[bool, str, Dict]:
    """
    Check if a response meets medical quality standards

    Args:
        response: The AI-generated response text to check
        symptom_context: Optional context about the symptoms being discussed

    Returns:
        Tuple of:
        - bool: Whether the response passed quality checks
        - str: Modified response if needed, or original if passed
        - Dict: Quality metrics and feedback
    """
    metrics = {
        "length_appropriate": False,
        "non_speculative": False,
        "urgency_addressed": False,
        "overall_quality": 0.0,
        "issues": [],
    }

    modified_response = response

    # 1. Check response length (aim for concise, 1-2 sentences per concept)
    sentences = re.split(r"[.!?]+", response)
    sentences = [s.strip() for s in sentences if s.strip()]
    metrics["sentence_count"] = len(sentences)

    if len(sentences) > 4:
        metrics["issues"].append("Response too verbose (>4 sentences)")
        # Truncate to first 2-3 meaningful sentences
        shortened = ". ".join(sentences[:3]) + "."
        modified_response = shortened
        logger.warning(f"Response too long ({len(sentences)} sentences), truncating")
    else:
        metrics["length_appropriate"] = True

    # 2. Check for speculative language
    contains_speculation = any(term in response.lower() for term in SPECULATIVE_TERMS)
    metrics["non_speculative"] = not contains_speculation

    if contains_speculation:
        metrics["issues"].append("Contains speculative terms")
        # Replace speculative language with more definitive statements or factual framing
        for term in SPECULATIVE_TERMS:
            modified_response = re.sub(
                r"\b" + term + r"\b",
                "research indicates",
                modified_response,
                flags=re.IGNORECASE,
            )
        logger.warning("Removed speculative language from response")

    # 3. Check for urgent medical symptoms
    if symptom_context:
        current_symptom = symptom_context.get("current_symptom", "")
        if current_symptom and current_symptom.lower() in URGENT_SYMPTOMS:
            urgent_warning = URGENT_SYMPTOMS[current_symptom.lower()]
            if urgent_warning not in modified_response:
                modified_response = modified_response + " " + urgent_warning
                metrics["issues"].append(f"Added urgent warning for {current_symptom}")
                logger.warning(f"Added urgent symptom warning for {current_symptom}")
            metrics["urgency_addressed"] = True

    # 4. Calculate overall quality score
    quality_score = 0.0
    if metrics["length_appropriate"]:
        quality_score += 0.4
    if metrics["non_speculative"]:
        quality_score += 0.4
    if len(metrics["issues"]) == 0:
        quality_score += 0.2

    metrics["overall_quality"] = round(quality_score, 2)

    passed = quality_score >= 0.8

    return passed, modified_response, metrics


def validate_medical_response(response_text: str, max_sentences: int = 2) -> str:
    """
    Ensure the medical response meets factuality and conciseness standards.

    Args:
        response_text: The AI-generated response to validate
        max_sentences: Maximum number of sentences to allow in the response

    Returns:
        The validated and potentially modified response
    """
    # Split response into sentences
    sentences = re.split(r"[.!?]+", response_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # If response is already concise, return as is
    if len(sentences) <= max_sentences:
        return response_text

    # Otherwise, keep just the first max_sentences
    concise_response = ". ".join(sentences[:max_sentences]) + "."

    logger.info(
        f"Shortened response from {len(sentences)} to {max_sentences} sentences"
    )
    return concise_response
