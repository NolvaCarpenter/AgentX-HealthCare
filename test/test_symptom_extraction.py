#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import the modules
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from symptoms.symptom_extraction import SymptomExtractor
from symptoms.symptom_state import SymptomState


def test_symptom_extraction():
    """Test that symptoms are correctly extracted and modifiers are not mistakenly identified as symptoms."""
    print("\n=== TESTING SYMPTOM EXTRACTION ===")

    # Initialize extractor
    extractor = SymptomExtractor()

    # Test cases with expected results
    test_cases = [
        {
            "input": "I have a fever that worsens after walking and at night.",
            "expected_symptoms": ["fever"],
            "should_not_contain": ["worsens", "walking", "night"],
            "description": "Fever with modifiers",
        },
        {
            "input": "I'm dealing with both fever and sore throat.",
            "expected_symptoms": ["fever", "sore throat"],
            "should_not_contain": ["dealing", "both"],
            "description": "Multiple symptoms",
        },
        {
            "input": "I feel sick with a mild fever since yesterday.",
            "expected_symptoms": ["fever"],
            "should_not_contain": ["mild", "feel", "sick"],
            "description": "Symptom with severity descriptor",
        },
        {
            "input": "My throat hurts when I swallow and I have difficulty breathing.",
            "expected_symptoms": ["sore throat", "difficulty breathing"],
            "should_not_contain": ["hurts", "swallow"],
            "description": "Description of symptoms",
        },
        {
            "input": "None of the medications help with my chronic headache.",
            "expected_symptoms": ["headache"],
            "should_not_contain": ["None", "medications", "chronic"],
            "description": "Symptom with the word 'None'",
        },
    ]

    for i, case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {case['description']}")
        print(f"Input: {case['input']}")

        # Extract symptoms
        extracted_symptoms = extractor.extract_symptoms(case["input"])
        print(f"Extracted: {extracted_symptoms}")

        # Check if the expected symptoms are extracted
        missing_symptoms = [
            s for s in case["expected_symptoms"] if s not in extracted_symptoms
        ]
        if missing_symptoms:
            print(f"❌ Missing expected symptoms: {missing_symptoms}")
        else:
            print("✅ All expected symptoms extracted correctly")

        # Check if any unwanted terms are mistakenly extracted as symptoms
        false_positives = [
            s
            for s in extracted_symptoms
            if any(term in s.lower() for term in case["should_not_contain"])
        ]
        if false_positives:
            print(f"❌ Incorrectly extracted as symptoms: {false_positives}")
        else:
            print("✅ No incorrect symptoms extracted")


def test_symptom_processing():
    """Test how symptoms are processed and potentially merged with similar symptoms."""
    print("\n=== TESTING SYMPTOM PROCESSING ===")

    # Initialize symptom state
    symptom_state = SymptomState()

    # Pre-populate with common symptoms
    symptom_state.add_symptom("fever")
    symptom_state.add_symptom("sore throat")

    # Test cases
    test_cases = [
        {
            "symptom": "worsens after walk",
            "expected_match": False,
            "description": "Symptom modifier mistakenly identified as symptom",
        },
        {
            "symptom": "worsens at night",
            "expected_match": False,
            "description": "Temporal descriptor mistakenly identified as symptom",
        },
        {
            "symptom": "mild fever",
            "expected_match": True,
            "expected_match_with": "fever",
            "description": "Severity + symptom should match with base symptom",
        },
        {
            "symptom": "None",
            "expected_match": False,
            "description": "'None' mistakenly identified as symptom",
        },
        {
            "symptom": "feel",
            "expected_match": False,
            "description": "Verb mistakenly identified as symptom",
        },
        {
            "symptom": "severe sore throat",
            "expected_match": True,
            "expected_match_with": "sore throat",
            "description": "Severity + symptom should match with base symptom",
        },
    ]

    for i, case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {case['description']}")
        print(f"Symptom: '{case['symptom']}'")

        # Check if the symptom is similar to any existing symptom
        similar_found, similar_symptom = symptom_state.find_similar_symptom(
            case["symptom"]
        )

        print(f"Similar found: {similar_found}, Matched with: '{similar_symptom}'")

        if case["expected_match"] == similar_found:
            if similar_found and "expected_match_with" in case:
                if similar_symptom == case["expected_match_with"]:
                    print(f"✅ Correctly matched with '{case['expected_match_with']}'")
                else:
                    print(
                        f"❌ Matched with '{similar_symptom}' instead of expected '{case['expected_match_with']}'"
                    )
            else:
                print("✅ Similarity check behaved as expected")
        else:
            print(
                f"❌ Expected match: {case['expected_match']}, but got: {similar_found}"
            )


if __name__ == "__main__":
    test_symptom_extraction()
    test_symptom_processing()
