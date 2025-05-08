"""
Medical knowledge base for symptom follow-up questions.
This module provides structured information about common symptoms and
appropriate follow-up questions based on medical knowledge repositories.

Later, this module can be expanded to include more symptoms and their
specific follow-up questions based on the latest medical guidelines and research.
"""

from typing import Dict, List, Any

# Mapping of symptoms to specific follow-up questions
SYMPTOM_FOLLOW_UP_QUESTIONS = {
    # Headache follow-ups
    "headache": {
        "characteristics": [
            "Is your headache sharp, dull, throbbing, or pressure-like?",
            "Is the headache on one side or both sides of your head?",
            "On a scale of 1-10, how would you rate the intensity of your headache?",
        ],
        "duration": [
            "How long have you been experiencing these headaches?",
            "Are these headaches constant or do they come and go?",
            "How long does a typical headache episode last?",
        ],
        "triggers": [
            "Do you notice anything that triggers your headaches?",
            "Are your headaches related to stress, certain foods, or physical activity?",
        ],
        "aggravating_factors": [
            "What makes your headache worse? For example: light, noise, movement?"
        ],
        "relieving_factors": [
            "What helps relieve your headache? Rest, medication, darkness, cold/hot compress?"
        ],
        "associated_symptoms": [
            "Do you experience any other symptoms with your headaches, like nausea, sensitivity to light/sound, visual disturbances, or dizziness?"
        ],
    },
    # Abdominal pain follow-ups
    "abdominal pain": {
        "location": [
            "Where exactly in your abdomen is the pain? Upper, lower, right, left, or central?",
            "Does the pain radiate to other areas like your back or chest?",
        ],
        "characteristics": [
            "How would you describe the pain? Sharp, cramping, burning, or dull?",
            "Is the pain constant or does it come and go?",
        ],
        "severity": [
            "On a scale of 1-10, how would you rate your abdominal pain?",
            "Does the intensity of the pain fluctuate throughout the day?",
        ],
        "triggers": [
            "Does eating certain foods trigger or worsen the pain?",
            "Is the pain related to eating in general or to an empty stomach?",
        ],
        "associated_symptoms": [
            "Do you have any other symptoms like nausea, vomiting, diarrhea, constipation, or bloating?"
        ],
        "relieving_factors": [
            "What helps relieve the pain? Medication, certain positions, eating, or not eating?"
        ],
    },
    # Cough follow-ups
    "cough": {
        "characteristics": [
            "Is your cough dry or productive (bringing up phlegm/mucus)?",
            "If productive, what color is the phlegm/mucus? Clear, yellow, green, brown, or bloody?",
        ],
        "duration": [
            "How long have you had this cough?",
            "Is the cough constant or does it come and go?",
        ],
        "timing": [
            "Is the cough worse at any particular time of day or night?",
            "Does the cough wake you from sleep?",
        ],
        "triggers": [
            "Does anything trigger or worsen your cough? Cold air, exercise, talking, or lying down?",
            "Do you notice the cough is related to certain environments or activities?",
        ],
        "associated_symptoms": [
            "Do you have any other symptoms like fever, shortness of breath, chest pain, or nasal congestion?"
        ],
    },
    # Dizziness follow-ups
    "dizziness": {
        "characteristics": [
            "Do you feel lightheaded, like you might faint, or does the room feel like it's spinning (vertigo)?",
            "Do you lose balance or feel unsteady when walking?",
        ],
        "duration": [
            "How long do these episodes of dizziness last?",
            "How frequently do they occur?",
        ],
        "triggers": [
            "Do you notice any triggers for your dizziness? Changes in position, certain movements, or after eating?",
            "Is the dizziness related to specific situations or environments?",
        ],
        "associated_symptoms": [
            "Do you experience any other symptoms alongside the dizziness, like nausea, vomiting, hearing changes, or ringing in the ears?"
        ],
    },
    # Chest pain follow-ups (high priority)
    "chest pain": {
        "characteristics": [
            "How would you describe the chest pain? Sharp, crushing, pressure, burning, or aching?",
            "Is the pain constant or intermittent?",
        ],
        "location": [
            "Where exactly in the chest is the pain? Central, left side, right side?",
            "Does the pain radiate to your arm, jaw, back, or elsewhere?",
        ],
        "duration": [
            "How long does the pain typically last?",
            "When did you first notice this pain?",
        ],
        "triggers": [
            "Does the pain occur with physical exertion or emotional stress?",
            "Is the pain related to breathing, coughing, or movement?",
        ],
        "relieving_factors": [
            "What makes the pain better? Rest, position changes, or medication?",
            "Does the pain improve with rest or continue regardless of activity?",
        ],
        "associated_symptoms": [
            "Do you have any other symptoms like shortness of breath, sweating, nausea, or lightheadedness with the chest pain?"
        ],
    },
    # Fatigue follow-ups
    "fatigue": {
        "characteristics": [
            "Is your fatigue physical exhaustion, mental tiredness, or both?",
            "Does the fatigue improve with rest or persists regardless of how much you rest?",
        ],
        "duration": [
            "How long have you been experiencing this fatigue?",
            "Did it start suddenly or develop gradually?",
        ],
        "timing": [
            "Is your fatigue worse at certain times of the day?",
            "How does your energy level fluctuate throughout the day?",
        ],
        "associated_symptoms": [
            "Do you have any other symptoms like fever, weight changes, poor sleep, or mood changes?"
        ],
        "impact": [
            "How is the fatigue affecting your daily activities and ability to function?"
        ],
    },
}

# Default follow-up questions for symptoms not specifically listed above
DEFAULT_FOLLOW_UP_QUESTIONS = {
    "severity": [
        "On a scale of 1-10, how would you rate the intensity of your {symptom}?",
        "How severe is your {symptom}?",
    ],
    "duration": [
        "When did your {symptom} first begin?",
        "How long have you been experiencing {symptom}?",
        "Is your {symptom} constant or does it come and go?",
    ],
    "characteristics": [
        "How would you describe your {symptom} in your own words?",
        "What is the nature of your {symptom}?",
    ],
    "location": [
        "Where exactly do you experience your {symptom}?",
        "Does your {symptom} affect a specific area or is it more generalized?",
    ],
    "triggers": [
        "Have you noticed anything that seems to trigger or cause your {symptom}?",
        "Are there specific activities, foods, or situations that bring on your {symptom}?",
    ],
    "aggravating_factors": [
        "What makes your {symptom} worse?",
        "Are there activities or situations that worsen your {symptom}?",
    ],
    "relieving_factors": [
        "What helps improve or relieve your {symptom}?",
        "Have you found anything that makes your {symptom} better?",
    ],
    "associated_symptoms": [
        "Are you experiencing any other symptoms along with your {symptom}?",
        "Have you noticed other health changes related to your {symptom}?",
    ],
    "impact": [
        "How is your {symptom} affecting your daily activities or quality of life?",
        "Has your {symptom} limited you in any way?",
    ],
}


def get_follow_up_questions(symptom: str, detail_type: str) -> List[str]:
    """
    Get appropriate follow-up questions for a specific symptom and detail type.

    Args:
        symptom (str): The symptom being discussed
        detail_type (str): The type of detail needed (severity, duration, etc.)

    Returns:
        List of relevant follow-up questions
    """
    symptom_lower = symptom.lower()

    # Check if we have specific questions for this symptom
    if symptom_lower in SYMPTOM_FOLLOW_UP_QUESTIONS:
        symptom_questions = SYMPTOM_FOLLOW_UP_QUESTIONS[symptom_lower]

        # If we have specific questions for this detail type
        if detail_type in symptom_questions:
            return symptom_questions[detail_type]

    # Fall back to default questions
    if detail_type in DEFAULT_FOLLOW_UP_QUESTIONS:
        # Format the questions with the symptom name
        return [
            q.format(symptom=symptom) for q in DEFAULT_FOLLOW_UP_QUESTIONS[detail_type]
        ]

    # If no matching questions found
    return [f"Can you tell me more about the {detail_type} of your {symptom}?"]
