"""
Test case generator for the symptom identification and follow-up question workflow.
Creates realistic patient conversation scenarios with varying complexity for testing.
"""

from typing import Dict, List, Any
import json
import random
import os


class TestCaseGenerator:
    """Generator for symptom conversation test cases."""

    def __init__(self):
        """Initialize the test case generator with common scenarios."""
        self.scenarios = [
            {
                "name": "Vague Dizziness",
                "description": "Patient describes feeling 'off' and dizzy",
                "initial_input": "I've been feeling really off lately, kinda dizzy.",
                "expected_symptoms": ["dizziness"],
                "expected_follow_ups": [
                    "Does the dizziness feel more like lightheadedness or like the room is spinning (vertigo)?",
                    "When did you first notice feeling dizzy and how long does it typically last?",
                ],
                "patient_responses": [
                    "It's more like the room is spinning, especially when I turn my head quickly.",
                    "It started about a week ago. Usually lasts for a few minutes, but sometimes longer if I'm moving around a lot.",
                ],
                "complexity": "low",
            },
            {
                "name": "Multiple Vague Symptoms",
                "description": "Patient describes multiple vague symptoms that need clarification",
                "initial_input": "I've been feeling terrible this week. I'm tired all the time, my stomach feels weird, and my head hurts.",
                "expected_symptoms": ["fatigue", "abdominal pain", "headache"],
                "expected_follow_ups": [
                    "Could you describe your headache? Is it throbbing, sharp, or dull?",
                    "Where exactly in your abdomen are you feeling discomfort?",
                    "Has your fatigue been affecting your daily activities?",
                ],
                "patient_responses": [
                    "The headache is usually a dull pain across my forehead, gets worse in the afternoon.",
                    "It's mostly in the upper part of my stomach, kind of like pressure or burning.",
                    "Yes, I'm so tired I can barely get through the workday and I've been going to bed much earlier.",
                ],
                "complexity": "medium",
            },
            {
                "name": "Common Cold with Confusion",
                "description": "Patient describes common cold symptoms but mixes terminology",
                "initial_input": "I think I caught something. My nose is running, I have the sniffles, and I feel hot and cold.",
                "expected_symptoms": [
                    "nasal congestion",
                    "rhinorrhea",
                    "fever",
                    "chills",
                ],
                "expected_follow_ups": [
                    "Have you checked your temperature to confirm if you have a fever?",
                    "When did these symptoms start and have they been getting better or worse?",
                ],
                "patient_responses": [
                    "I haven't checked with a thermometer but I feel warm. The chills come and go.",
                    "Started about 3 days ago after my friend visited. Seems to be getting a bit worse each day.",
                ],
                "complexity": "low",
            },
            {
                "name": "Chronic Back Pain with Detail",
                "description": "Patient provides extensive background on chronic issue",
                "initial_input": "My back's been killing me for months. It started after I helped my friend move furniture. It's mostly on the lower right side and gets worse when I sit for long periods.",
                "expected_symptoms": ["back pain"],
                "expected_follow_ups": [
                    "On a scale of 1-10, how would you rate your back pain at its worst?",
                    "Have you found anything that helps relieve the pain?",
                    "Does the pain radiate to other areas like your legs?",
                ],
                "patient_responses": [
                    "It's about a 7 when it's really bad, like at the end of a workday.",
                    "Heat seems to help a bit, and stretching sometimes. Over-the-counter pain meds don't do much anymore.",
                    "Sometimes it does go down my right leg, especially when I've been sitting too long.",
                ],
                "complexity": "high",
            },
            {
                "name": "Anxiety Symptoms",
                "description": "Patient describes physical symptoms of anxiety without recognizing the cause",
                "initial_input": "Lately I've been having trouble catching my breath, my heart races, and sometimes I feel like I'm going to pass out. Especially when I'm at work or in crowded places.",
                "expected_symptoms": [
                    "shortness of breath",
                    "palpitations",
                    "lightheadedness",
                ],
                "expected_follow_ups": [
                    "Do these episodes come on suddenly or gradually?",
                    "Have you noticed any triggers for these symptoms?",
                    "How long do these episodes typically last?",
                ],
                "patient_responses": [
                    "They come on pretty suddenly, like within minutes.",
                    "They definitely happen more when I'm stressed at work or when there are a lot of people around.",
                    "Usually 15-20 minutes, sometimes longer if I can't get somewhere quiet.",
                ],
                "complexity": "medium",
            },
        ]

    def generate_test_cases(self, num_cases: int = 5) -> List[Dict]:
        """
        Generate a specific number of test cases by selecting or creating scenarios.

        Args:
            num_cases: Number of test cases to generate

        Returns:
            List of test case scenarios as dictionaries
        """
        # If we have enough scenarios, select randomly
        if len(self.scenarios) >= num_cases:
            return random.sample(self.scenarios, num_cases)

        # Otherwise, use all existing scenarios and create more
        result = self.scenarios.copy()

        # Create additional cases by mixing elements from existing ones
        while len(result) < num_cases:
            # Select two random scenarios to mix
            base, secondary = random.sample(self.scenarios, 2)

            # Create a new mixed scenario
            mixed = {
                "name": f"Mixed: {base['name']} + {secondary['name']}",
                "description": f"Combined scenario with elements from multiple conditions",
                "initial_input": f"{base['initial_input']} Also, {secondary['initial_input'].lower()}",
                "expected_symptoms": base["expected_symptoms"]
                + secondary["expected_symptoms"],
                "expected_follow_ups": random.sample(
                    base["expected_follow_ups"] + secondary["expected_follow_ups"], 3
                ),
                "patient_responses": random.sample(
                    base["patient_responses"] + secondary["patient_responses"], 3
                ),
                "complexity": "high",  # Mixed cases are inherently more complex
            }

            result.append(mixed)

        return result

    def save_test_cases(self, output_file: str, num_cases: int = 5):
        """
        Generate and save test cases to a JSON file.

        Args:
            output_file: Path to save the test cases
            num_cases: Number of test cases to generate
        """
        test_cases = self.generate_test_cases(num_cases)

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        # Save to file
        with open(output_file, "w") as f:
            json.dump({"test_cases": test_cases}, f, indent=2)

        print(f"Generated {len(test_cases)} test cases and saved to {output_file}")

    def run_interactive_test(self, scenario_index: int = None):
        """
        Run an interactive test using a specific scenario.

        Args:
            scenario_index: Index of the scenario to use, or None for random selection
        """
        if scenario_index is None:
            scenario = random.choice(self.scenarios)
        else:
            scenario = self.scenarios[scenario_index % len(self.scenarios)]

        print("\n" + "=" * 50)
        print(f"TEST SCENARIO: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print("=" * 50)
        print("\nPatient input:")
        print(f"  \"{scenario['initial_input']}\"")

        print("\nExpected symptoms to identify:")
        for symptom in scenario["expected_symptoms"]:
            print(f"  - {symptom}")

        print("\nSuggested follow-up questions:")
        for question in scenario["expected_follow_ups"]:
            print(f"  - {question}")

        print("\nSimulated patient responses:")
        for response in scenario["patient_responses"]:
            print(f'  - "{response}"')

        print("\nComplexity level:", scenario["complexity"])
        print("=" * 50)


if __name__ == "__main__":
    # Example usage
    generator = TestCaseGenerator()

    # Generate and save test cases
    generator.save_test_cases("test/symptom_test_cases.json", num_cases=5)

    # Run an interactive test with a random scenario
    generator.run_interactive_test()
