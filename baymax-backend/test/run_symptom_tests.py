"""
Test runner for symptom conversation scenarios.
This script tests the conversation agent's ability to correctly identify symptoms,
generate appropriate follow-up questions, and maintain factual responses.
"""

import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime
import argparse

# Add the parent directory to the path to import the modules
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from conversation_agent import (
    initialize_state,
    check_symptom_context,
    extract_symptoms,
    process_symptoms,
)
from conversation_agent import (
    extract_details,
    update_symptom_details,
    determine_next_action,
    generate_question,
)
from conversation_agent import generate_response, update_history
from symptoms.symptom_extraction import SymptomExtractor, SymptomDetailExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("symptom_test_runner")


class SymptomConversationTester:
    """Test runner for symptom conversation workflows."""

    def __init__(self, test_case_file: str = None):
        """
        Initialize the tester.

        Args:
            test_case_file: Path to the JSON file containing test cases
        """
        self.test_cases = []
        if test_case_file:
            self.load_test_cases(test_case_file)

    def load_test_cases(self, test_case_file: str):
        """
        Load test cases from a JSON file.

        Args:
            test_case_file: Path to the JSON file containing test cases
        """
        try:
            with open(test_case_file, "r") as f:
                data = json.load(f)
                self.test_cases = data.get("test_cases", [])
                logger.info(
                    f"Loaded {len(self.test_cases)} test cases from {test_case_file}"
                )
        except Exception as e:
            logger.error(f"Failed to load test cases from {test_case_file}: {e}")
            self.test_cases = []

    def run_step(self, state, action_name):
        """
        Run a single step in the conversation workflow.

        Args:
            state: Current conversation state
            action_name: Name of the action to execute

        Returns:
            Updated state after executing the action
        """
        action_map = {
            "check_symptom_context": check_symptom_context,
            "extract_symptoms": extract_symptoms,
            "process_symptoms": process_symptoms,
            "extract_details": extract_details,
            "update_symptom_details": update_symptom_details,
            "determine_next_action": determine_next_action,
            "generate_question": generate_question,
            "generate_response": generate_response,
            "update_history": update_history,
        }

        if action_name in action_map:
            result = action_map[action_name](state)

            # If the result is a string, it's the next node
            if isinstance(result, str):
                return {"current_action": result, **state}
            # Otherwise, it's an updated state
            return result
        else:
            logger.warning(f"Unknown action: {action_name}")
            return state

    def run_conversation_workflow(
        self, user_input: str, expected_symptoms: list = None
    ):
        """
        Run through the conversation workflow for a single user input.

        Args:
            user_input: The user's input message
            expected_symptoms: List of expected symptoms to be identified

        Returns:
            Final state, extracted symptoms, and response
        """
        # Initialize the state
        state = initialize_state()
        state["user_input"] = user_input

        # Standard workflow steps
        steps = [
            "check_symptom_context",
            "extract_symptoms",
            "process_symptoms",
            "extract_details",
            "update_symptom_details",
            "determine_next_action",
            "generate_question",
            "update_history",
        ]

        current_step = 0
        max_steps = 15  # Prevent infinite loops
        step_count = 0

        # Run through the workflow
        while step_count < max_steps:
            action = state.get("current_action", steps[current_step])
            logger.debug(f"Step {step_count}: {action}")

            # Execute the current action
            state = self.run_step(state, action)
            step_count += 1

            # Check if we've completed the workflow
            if "ai_response" in state:
                break

        # Extract results
        extracted = state.get("extracted_symptoms", {})
        symptom_state = state.get("symptom_state", None)
        response = state.get("ai_response", "No response generated")

        # Evaluate symptom extraction accuracy if expected symptoms provided
        extraction_results = {}
        if expected_symptoms:
            found_symptoms = list(extracted.keys())

            # Calculate precision and recall
            true_positives = [
                s
                for s in found_symptoms
                if any(
                    expected.lower() in s.lower() or s.lower() in expected.lower()
                    for expected in expected_symptoms
                )
            ]
            false_positives = [s for s in found_symptoms if s not in true_positives]
            false_negatives = [
                s
                for s in expected_symptoms
                if not any(
                    s.lower() in found.lower() or found.lower() in s.lower()
                    for found in found_symptoms
                )
            ]

            precision = (
                len(true_positives) / len(found_symptoms) if found_symptoms else 0
            )
            recall = (
                len(true_positives) / len(expected_symptoms) if expected_symptoms else 0
            )
            f1 = (
                2 * (precision * recall) / (precision + recall)
                if (precision + recall) > 0
                else 0
            )

            extraction_results = {
                "expected_symptoms": expected_symptoms,
                "extracted_symptoms": found_symptoms,
                "true_positives": true_positives,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            }

            logger.info(
                f"Extraction results: P={precision:.2f}, R={recall:.2f}, F1={f1:.2f}"
            )

        return state, extracted, response, extraction_results

    def run_test_case(self, test_case):
        """
        Run a single test case.

        Args:
            test_case: Dictionary describing the test case

        Returns:
            Test results dictionary
        """
        logger.info(f"Running test case: {test_case['name']}")

        # Extract test case data
        user_input = test_case["initial_input"]
        expected_symptoms = test_case.get("expected_symptoms", [])
        expected_follow_ups = test_case.get("expected_follow_ups", [])

        # Run the initial conversation
        state, extracted_symptoms, response, extraction_results = (
            self.run_conversation_workflow(user_input, expected_symptoms)
        )

        # Check if the response contains a follow-up question
        contains_question = "?" in response

        # Check if the follow-up question is relevant to the expected ones
        question_relevance = 0.0
        if contains_question and expected_follow_ups:
            # Simple relevance check - if the follow-up contains keywords from expected questions
            keywords = set()
            for q in expected_follow_ups:
                keywords.update(q.lower().split())

            # Remove common words
            stopwords = {
                "a",
                "an",
                "the",
                "is",
                "are",
                "do",
                "does",
                "did",
                "have",
                "has",
                "had",
                "you",
                "your",
                "any",
                "been",
                "to",
                "of",
                "in",
                "on",
                "for",
                "with",
            }
            keywords = keywords - stopwords

            # Count keywords in response
            keyword_count = sum(
                1 for word in response.lower().split() if word in keywords
            )
            question_relevance = keyword_count / len(keywords) if keywords else 0.0

        # Collect results
        results = {
            "test_case": test_case["name"],
            "complexity": test_case.get("complexity", "medium"),
            "user_input": user_input,
            "response": response,
            "contains_question": contains_question,
            "question_relevance": question_relevance,
            "extraction_results": extraction_results,
            "qa_metrics": state.get("qa_metrics", {}),
            "response_metrics": state.get("response_metrics", {}),
        }

        logger.info(f"Test completed. Question relevance: {question_relevance:.2f}")
        return results

    def run_all_tests(self):
        """
        Run all loaded test cases.

        Returns:
            List of test results for each case
        """
        results = []
        for test_case in self.test_cases:
            result = self.run_test_case(test_case)
            results.append(result)

        return results

    def generate_report(self, results):
        """
        Generate a summary report from the test results.

        Args:
            results: List of test results

        Returns:
            Report as a string
        """
        if not results:
            return "No test results to report."

        # Calculate overall metrics
        total_tests = len(results)
        symptom_precision = (
            sum(r["extraction_results"].get("precision", 0) for r in results)
            / total_tests
        )
        symptom_recall = (
            sum(r["extraction_results"].get("recall", 0) for r in results) / total_tests
        )
        symptom_f1 = (
            sum(r["extraction_results"].get("f1_score", 0) for r in results)
            / total_tests
        )

        question_rate = sum(1 for r in results if r["contains_question"]) / total_tests
        question_relevance = sum(r["question_relevance"] for r in results) / total_tests

        # Format report
        report = [
            "=" * 70,
            "SYMPTOM CONVERSATION WORKFLOW TEST REPORT",
            "=" * 70,
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total test cases: {total_tests}",
            "",
            "SYMPTOM EXTRACTION PERFORMANCE",
            f"Overall Precision: {symptom_precision:.2f}",
            f"Overall Recall: {symptom_recall:.2f}",
            f"Overall F1 Score: {symptom_f1:.2f}",
            "",
            "FOLLOW-UP QUESTION PERFORMANCE",
            f"Question Generation Rate: {question_rate:.2f}",
            f"Question Relevance Score: {question_relevance:.2f}",
            "",
            "INDIVIDUAL TEST CASE RESULTS",
            "-" * 70,
        ]

        # Add individual test results
        for i, result in enumerate(results):
            report.extend(
                [
                    f"Test {i+1}: {result['test_case']} (Complexity: {result['complexity']})",
                    f"  Input: \"{result['user_input'][:50]}...\"",
                    f"  Expected symptoms: {result['extraction_results']['expected_symptoms']}",
                    f"  Extracted symptoms: {result['extraction_results']['extracted_symptoms']}",
                    f"  Extraction F1 Score: {result['extraction_results'].get('f1_score', 0):.2f}",
                    f"  Response contains question: {result['contains_question']}",
                    f"  Question relevance: {result['question_relevance']:.2f}",
                    "-" * 70,
                ]
            )

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Run symptom conversation workflow tests"
    )
    parser.add_argument(
        "--test-file",
        default="test/symptom_test_cases.json",
        help="Path to the test case JSON file",
    )
    parser.add_argument(
        "--output",
        default="symptom_test_report.txt",
        help="Path to save the test report",
    )
    args = parser.parse_args()

    # Run tests
    tester = SymptomConversationTester(args.test_file)
    results = tester.run_all_tests()

    # Generate and save report
    report = tester.generate_report(results)
    with open(args.output, "w") as f:
        f.write(report)

    logger.info(f"Test report saved to {args.output}")
    print(f"\nTest completed. Report saved to {args.output}")


if __name__ == "__main__":
    main()
