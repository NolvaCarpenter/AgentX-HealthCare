"""
Symptom synonym mapping for improved symptom detection.
This module provides dictionaries that map common layman terms and synonyms
to standardized medical terminology.
"""

# Mapping of layman terms to standardized symptom names
LAYMAN_TO_STANDARD = {
    # Digestive/Abdominal
    "tummy ache": "abdominal pain",
    "stomach ache": "abdominal pain",
    "belly pain": "abdominal pain",
    "gut pain": "abdominal pain",
    "stomach cramps": "abdominal cramps",
    "upset stomach": "dyspepsia",
    "heartburn": "acid reflux",
    "acid indigestion": "acid reflux",
    "throwing up": "vomiting",
    "puke": "vomiting",
    "being sick": "vomiting",
    "loose stool": "diarrhea",
    "runny stool": "diarrhea",
    "runs": "diarrhea",
    "constipated": "constipation",
    "can't poop": "constipation",
    "trouble pooping": "constipation",
    "gas": "flatulence",
    # Respiratory
    "short of breath": "shortness of breath",
    "breathlessness": "shortness of breath",
    "trouble breathing": "breathing difficulty",
    "can't catch breath": "breathing difficulty",
    "stuffy nose": "nasal congestion",
    "blocked nose": "nasal congestion",
    "runny nose": "rhinorrhea",
    "phlegm": "mucus production",
    "mucus": "mucus production",
    # Head/Neurological
    "headache": "headache",
    "head hurts": "headache",
    "head pain": "headache",
    "migraine": "migraine",
    "bad headache": "migraine",
    "dizzy": "dizziness",
    "lightheaded": "lightheadedness",
    "vertigo": "vertigo",
    "spinning": "vertigo",
    "room spinning": "vertigo",
    "confused": "confusion",
    "brain fog": "confusion",
    "can't think straight": "confusion",
    "memory issues": "memory problems",
    "forgetful": "memory problems",
    "fainting": "syncope",
    "passing out": "syncope",
    "blacked out": "syncope",
    # Pain-related
    "joint pain": "arthralgia",
    "achy joints": "arthralgia",
    "muscle pain": "myalgia",
    "muscle ache": "myalgia",
    "sore muscles": "myalgia",
    "back pain": "back pain",
    "backache": "back pain",
    "sore back": "back pain",
    "neck pain": "neck pain",
    "stiff neck": "neck stiffness",
    "chest pain": "chest pain",
    "chest tightness": "chest tightness",
    # Skin-related
    "rash": "skin rash",
    "hives": "urticaria",
    "itchy skin": "pruritus",
    "itching": "pruritus",
    "dry skin": "xerosis",
    "bruise": "contusion",
    "bruising": "contusion",
    # ENT (Ear, Nose, Throat)
    "sore throat": "pharyngitis",
    "scratchy throat": "pharyngitis",
    "throat pain": "pharyngitis",
    "earache": "ear pain",
    "ear hurts": "ear pain",
    "ringing in ears": "tinnitus",
    "ear ringing": "tinnitus",
    # General
    "fever": "fever",
    "high temperature": "fever",
    "running a temperature": "fever",
    "chills": "chills",
    "shaking": "tremors",
    "trembling": "tremors",
    "tired": "fatigue",
    "exhausted": "fatigue",
    "no energy": "fatigue",
    "worn out": "fatigue",
    "sleepy all the time": "fatigue",
    "weakness": "weakness",
    "feeling weak": "weakness",
    "sweating": "diaphoresis",
    "night sweats": "night sweats",
    "weight loss": "weight loss",
    "losing weight": "weight loss",
    "appetite loss": "loss of appetite",
    "not hungry": "loss of appetite",
}

# Common misspellings of symptoms
MISSPELLINGS = {
    "diahrea": "diarrhea",
    "diarhea": "diarrhea",
    "diarrhoea": "diarrhea",
    "caugh": "cough",
    "cof": "cough",
    "feever": "fever",
    "feavor": "fever",
    "vomitting": "vomiting",
    "vomiting": "vomiting",
    "headake": "headache",
    "hedache": "headache",
    "miagraine": "migraine",
    "migriane": "migraine",
    "nauesa": "nausea",
    "nausea": "nausea",
    "throwup": "vomiting",
    "soar throat": "sore throat",
    "sore throut": "sore throat",
    "runny knows": "runny nose",
    "runy nose": "runny nose",
    "caugh": "cough",
    "coffing": "coughing",
    "short of breathe": "shortness of breath",
    "cant breath": "breathing difficulty",
    "dizzyness": "dizziness",
    "diziness": "dizziness",
    "fatigue": "fatigue",
    "exausted": "exhausted",
    "tyred": "tired",
    "tierd": "tired",
}


def normalize_symptom(symptom: str) -> str:
    """
    Normalize a symptom by checking against dictionaries of layman terms and misspellings.
    Returns the standardized term if found, otherwise returns the original term.

    Args:
        symptom: The symptom term to normalize

    Returns:
        The normalized/standardized symptom term
    """
    symptom_lower = symptom.lower().strip()

    # Check direct match in layman terms
    if symptom_lower in LAYMAN_TO_STANDARD:
        symptom_std = LAYMAN_TO_STANDARD[symptom_lower]
        return (
            f"{symptom_std} ({symptom})"
            if symptom_std != symptom_lower
            else symptom_std
        )

    # Check misspellings
    if symptom_lower in MISSPELLINGS:
        return MISSPELLINGS[symptom_lower]

    # If no match found, return original
    return symptom
