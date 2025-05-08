#!/usr/bin/env python3

from ..symptoms.symptom_state import SymptomState


def test_symptom_similarity():
    """Test the symptom similarity detection feature."""
    symptom_state = SymptomState()

    print("Testing symptom similarity detection:")
    print("=====================================\n")

    # Test case 1: Exact same symptoms
    symptom_state.add_symptom("Fever")
    similar_found, similar_symptom = symptom_state.find_similar_symptom("Fever")
    print(
        f"1. 'Fever' and 'Fever': Similar? {similar_found}, Matched with: {similar_symptom}"
    )

    # Test case 2: Different case
    similar_found, similar_symptom = symptom_state.find_similar_symptom("fever")
    print(
        f"2. 'Fever' and 'fever': Similar? {similar_found}, Matched with: {similar_symptom}"
    )

    # Test case 3: With modifier
    similar_found, similar_symptom = symptom_state.find_similar_symptom("mild fever")
    print(
        f"3. 'Fever' and 'mild fever': Similar? {similar_found}, Matched with: {similar_symptom}"
    )

    # Test case 4: Just the modifier
    similar_found, similar_symptom = symptom_state.find_similar_symptom("mild")
    print(
        f"4. 'Fever' and 'mild': Similar? {similar_found}, Matched with: {similar_symptom}"
    )

    # Test case 5: Add a new symptom with a modifier, should not duplicate
    symptom_state.add_symptom("mild fever")
    print(
        f"\nAfter adding 'mild fever', current symptoms: {symptom_state.primary_symptoms}"
    )

    # Test case 6: Add a completely different symptom
    symptom_state.add_symptom("Headache")
    print(
        f"After adding 'Headache', current symptoms: {symptom_state.primary_symptoms}"
    )

    # Test case 7: Add a slightly different symptom
    symptom_state.add_symptom("severe headache")
    print(
        f"After adding 'severe headache', current symptoms: {symptom_state.primary_symptoms}"
    )

    # Test the session summary to see how it handles the merged symptoms
    print("\nSession Summary:")
    print(symptom_state.get_session_summary())


if __name__ == "__main__":
    test_symptom_similarity()
