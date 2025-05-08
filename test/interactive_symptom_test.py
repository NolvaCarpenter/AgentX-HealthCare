"""
Interactive test runner for the improved symptom conversation workflow.
This script allows testing the conversation agent directly with predefined or custom inputs.
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import argparse
import json
import colorama
from colorama import Fore, Style

# Add the parent directory to the path to import the modules
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Initialize colorama for colored terminal output
colorama.init()

from conversation_agent import process_user_input
from symptom_test_generator import TestCaseGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"interactive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("symptom_workflow_tester")


def show_banner():
    """Display a colorful banner for the interactive test."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║ {Fore.YELLOW}Symptom Conversation Workflow Interactive Test{Fore.CYAN}           ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


def run_interactive_test():
    """Run an interactive test of the conversation agent."""
    show_banner()

    print(
        f"{Fore.GREEN}Welcome to the interactive symptom conversation test!{Style.RESET_ALL}"
    )
    print("You can type your own inputs or use test scenarios.\n")

    # Initialize the conversation
    state = None
    thread_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Load test generator
    test_generator = TestCaseGenerator()
    available_scenarios = test_generator.scenarios

    while True:
        print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
        print("1. Enter your own input")
        print("2. Use a test scenario")
        print("3. Show current symptom state")
        print("4. Exit")

        choice = input(f"\n{Fore.YELLOW}Select an option (1-4): {Style.RESET_ALL}")

        if choice == "1":
            # User's own input
            user_input = input(f"\n{Fore.GREEN}You: {Style.RESET_ALL}")
            if user_input.lower() in ["exit", "quit", "bye"]:
                break

            print(f"{Fore.CYAN}Processing...{Style.RESET_ALL}")
            ai_response, state = process_user_input(user_input, state, thread_id)

            print(f"\n{Fore.MAGENTA}AI: {Style.RESET_ALL}{ai_response}")

        elif choice == "2":
            # Use a test scenario
            print(f"\n{Fore.CYAN}Available Test Scenarios:{Style.RESET_ALL}")
            for i, scenario in enumerate(available_scenarios):
                print(f"{i+1}. {scenario['name']} - {scenario['description']}")

            try:
                scenario_idx = (
                    int(
                        input(
                            f"\n{Fore.YELLOW}Select a scenario (1-{len(available_scenarios)}): {Style.RESET_ALL}"
                        )
                    )
                    - 1
                )
                if 0 <= scenario_idx < len(available_scenarios):
                    scenario = available_scenarios[scenario_idx]
                    user_input = scenario["initial_input"]

                    print(
                        f"\n{Fore.GREEN}Using scenario: {scenario['name']}{Style.RESET_ALL}"
                    )
                    print(f"{Fore.GREEN}You: {Style.RESET_ALL}{user_input}")

                    print(f"{Fore.CYAN}Processing...{Style.RESET_ALL}")
                    ai_response, state = process_user_input(
                        user_input, state, thread_id
                    )

                    print(f"\n{Fore.MAGENTA}AI: {Style.RESET_ALL}{ai_response}")

                    # Show expected follow-up questions for reference
                    if (
                        "expected_follow_ups" in scenario
                        and scenario["expected_follow_ups"]
                    ):
                        print(
                            f"\n{Fore.YELLOW}Expected follow-up questions from this scenario:{Style.RESET_ALL}"
                        )
                        for q in scenario["expected_follow_ups"]:
                            print(f"- {q}")
                else:
                    print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")

        elif choice == "3":
            # Show current symptom state
            if state and "symptom_state" in state and state["symptom_state"]:
                symptom_state = state["symptom_state"]

                print(
                    f"\n{Fore.CYAN}======= CURRENT SYMPTOM STATE ======={Style.RESET_ALL}"
                )
                print(
                    f"{Fore.YELLOW}Primary Symptoms:{Style.RESET_ALL} {', '.join(symptom_state.primary_symptoms)}"
                )
                print(
                    f"{Fore.YELLOW}Current Symptom:{Style.RESET_ALL} {symptom_state.current_symptom}"
                )

                # Show details for each symptom
                for symptom in symptom_state.primary_symptoms:
                    print(f"\n{Fore.CYAN}Symptom: {symptom}{Style.RESET_ALL}")

                    # Get the details for this symptom
                    try:
                        detail = symptom_state.symptom_details.get(symptom)
                        if detail:
                            if detail.severity and detail.severity.level:
                                print(f"  Severity: {detail.severity.level}/10")

                            if detail.duration:
                                started = detail.duration.start_date or "unknown"
                                status = (
                                    "Ongoing"
                                    if detail.duration.is_ongoing
                                    else "Resolved"
                                )
                                print(
                                    f"  Duration: Started {started}, Status: {status}"
                                )

                            if detail.characteristics:
                                print(
                                    f"  Characteristics: {', '.join(detail.characteristics)}"
                                )

                            if detail.location:
                                print(f"  Location: {detail.location}")

                            if detail.triggers:
                                print(f"  Triggers: {', '.join(detail.triggers)}")

                            if detail.aggravating_factors:
                                print(
                                    f"  Aggravating factors: {', '.join(detail.aggravating_factors)}"
                                )

                            if detail.relieving_factors:
                                print(
                                    f"  Relieving factors: {', '.join(detail.relieving_factors)}"
                                )

                            # Get missing fields for this symptom
                            missing = symptom_state.missing_fields(symptom)
                            if missing:
                                print(
                                    f"  {Fore.YELLOW}Missing fields:{Style.RESET_ALL} {', '.join(missing)}"
                                )
                        else:
                            print("  No details recorded yet")
                    except Exception as e:
                        print(
                            f"  {Fore.RED}Error retrieving details: {str(e)}{Style.RESET_ALL}"
                        )
            else:
                print(f"\n{Fore.YELLOW}No symptom data available yet.{Style.RESET_ALL}")

        elif choice == "4":
            # Exit
            print(
                f"\n{Fore.GREEN}Thank you for testing the symptom conversation workflow!{Style.RESET_ALL}"
            )
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please select 1-4.{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="Run interactive symptom workflow test"
    )
    args = parser.parse_args()

    try:
        run_interactive_test()
    except KeyboardInterrupt:
        print(
            f"\n\n{Fore.GREEN}Test terminated by user. Thanks for testing!{Style.RESET_ALL}"
        )
    except Exception as e:
        logger.error(f"Error in interactive test: {str(e)}", exc_info=True)
        print(f"\n{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")
        print(f"See log file for details.")


if __name__ == "__main__":
    main()
