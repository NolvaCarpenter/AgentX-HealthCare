"""
Logging and evaluation system for symptom extraction and follow-up question generation.
This module provides tools to log and analyze the effectiveness of the conversation agent.
"""

import logging
import json
import os
from datetime import datetime
import sqlite3
from typing import Dict, List, Any, Optional
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("symptom_evaluation")


class SymptomEvaluationLogger:
    """Logger for evaluating symptom extraction and follow-up question quality."""

    def __init__(self, db_path: str = "baymax_agentx_health.db"):
        """
        Initialize the logger with a database connection.

        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure the necessary tables exist in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create evaluation table if not exists
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS symptom_evaluation (
            evaluation_id TEXT PRIMARY KEY,
            thread_id TEXT,
            timestamp TEXT,
            user_input TEXT,
            extracted_symptoms TEXT,
            follow_up_questions TEXT,
            quality_score REAL,
            factual_accuracy_score REAL,
            completeness_score REAL,
            metrics TEXT
        )
        """
        )

        conn.commit()
        conn.close()

    def log_extraction(
        self,
        thread_id: str,
        user_input: str,
        extracted_symptoms: Dict,
        follow_up_questions: List[str] = None,
        quality_metrics: Dict = None,
    ):
        """
        Log a symptom extraction event for evaluation.

        Args:
            thread_id: Conversation thread ID
            user_input: User's input that triggered extraction
            extracted_symptoms: Dictionary of extracted symptoms
            follow_up_questions: List of follow-up questions generated
            quality_metrics: Dictionary of quality metrics
        """
        evaluation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Calculate basic scores if not provided
        quality_metrics = quality_metrics or {}
        quality_score = quality_metrics.get("quality_score", 0.0)
        factual_accuracy = quality_metrics.get("factual_accuracy", 0.0)
        completeness = quality_metrics.get("completeness", 0.0)

        # Convert data to JSON strings
        extracted_json = json.dumps(extracted_symptoms)
        questions_json = json.dumps(follow_up_questions or [])
        metrics_json = json.dumps(quality_metrics)

        # Log to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT INTO symptom_evaluation (
            evaluation_id, thread_id, timestamp, user_input, 
            extracted_symptoms, follow_up_questions, quality_score, 
            factual_accuracy_score, completeness_score, metrics
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                evaluation_id,
                thread_id,
                timestamp,
                user_input,
                extracted_json,
                questions_json,
                quality_score,
                factual_accuracy,
                completeness,
                metrics_json,
            ),
        )

        conn.commit()
        conn.close()

        logger.info(
            f"Logged symptom extraction event {evaluation_id} for thread {thread_id}"
        )

    def get_thread_evaluations(self, thread_id: str) -> List[Dict]:
        """
        Get all evaluation entries for a specific thread.

        Args:
            thread_id: The conversation thread ID

        Returns:
            List of evaluation entries as dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT evaluation_id, timestamp, user_input, extracted_symptoms, 
               follow_up_questions, quality_score, factual_accuracy_score, 
               completeness_score, metrics
        FROM symptom_evaluation
        WHERE thread_id = ?
        ORDER BY timestamp
        """,
            (thread_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append(
                {
                    "evaluation_id": row[0],
                    "timestamp": row[1],
                    "user_input": row[2],
                    "extracted_symptoms": json.loads(row[3]),
                    "follow_up_questions": json.loads(row[4]),
                    "quality_score": row[5],
                    "factual_accuracy_score": row[6],
                    "completeness_score": row[7],
                    "metrics": json.loads(row[8]),
                }
            )

        return results

    def get_evaluation_summary(self, thread_id: Optional[str] = None) -> Dict:
        """
        Get a summary of evaluation metrics, optionally filtered by thread.

        Args:
            thread_id: Optional thread ID to filter results

        Returns:
            Dictionary with summary metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT AVG(quality_score), AVG(factual_accuracy_score), 
               AVG(completeness_score), COUNT(*)
        FROM symptom_evaluation
        """

        if thread_id:
            cursor.execute(query + " WHERE thread_id = ?", (thread_id,))
        else:
            cursor.execute(query)

        row = cursor.fetchone()

        # Get most common symptoms
        if thread_id:
            cursor.execute(
                """
            SELECT extracted_symptoms FROM symptom_evaluation
            WHERE thread_id = ?
            """,
                (thread_id,),
            )
        else:
            cursor.execute("SELECT extracted_symptoms FROM symptom_evaluation")

        symptom_rows = cursor.fetchall()
        conn.close()

        # Process symptom frequency
        all_symptoms = []
        for s_row in symptom_rows:
            symptoms = json.loads(s_row[0])
            all_symptoms.extend(list(symptoms.keys()))

        symptom_counts = {}
        for symptom in all_symptoms:
            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1

        # Sort symptoms by frequency
        top_symptoms = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        return {
            "avg_quality_score": row[0] if row[0] is not None else 0,
            "avg_factual_accuracy": row[1] if row[1] is not None else 0,
            "avg_completeness": row[2] if row[2] is not None else 0,
            "total_entries": row[3] if row[3] is not None else 0,
            "top_symptoms": dict(top_symptoms),
        }

    def export_evaluations(self, output_file: str, thread_id: Optional[str] = None):
        """
        Export evaluation data to a JSON file.

        Args:
            output_file: Path to save the export
            thread_id: Optional thread ID to filter results
        """
        if thread_id:
            evaluations = self.get_thread_evaluations(thread_id)
            summary = self.get_evaluation_summary(thread_id)
        else:
            # Get all evaluations
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
            SELECT thread_id, evaluation_id, timestamp, user_input, extracted_symptoms, 
                  follow_up_questions, quality_score, factual_accuracy_score, 
                  completeness_score, metrics
            FROM symptom_evaluation
            ORDER BY thread_id, timestamp
            """
            )

            rows = cursor.fetchall()
            conn.close()

            evaluations = []
            for row in rows:
                evaluations.append(
                    {
                        "thread_id": row[0],
                        "evaluation_id": row[1],
                        "timestamp": row[2],
                        "user_input": row[3],
                        "extracted_symptoms": json.loads(row[4]),
                        "follow_up_questions": json.loads(row[5]),
                        "quality_score": row[6],
                        "factual_accuracy_score": row[7],
                        "completeness_score": row[8],
                        "metrics": json.loads(row[9]),
                    }
                )

            summary = self.get_evaluation_summary()

        # Create export data
        export_data = {
            "summary": summary,
            "evaluations": evaluations,
            "export_date": datetime.now().isoformat(),
            "thread_id": thread_id,
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        # Save to file
        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Exported {len(evaluations)} evaluation records to {output_file}")

        return export_data


# Integration helper function
def log_symptom_extraction(
    thread_id, user_input, extracted_symptoms, follow_up_questions=None, metrics=None
):
    """
    Helper function to log symptom extraction events.

    Args:
        thread_id: Conversation thread ID
        user_input: User's input that triggered extraction
        extracted_symptoms: Dictionary of extracted symptoms
        follow_up_questions: List of follow-up questions generated
        metrics: Dictionary of quality metrics
    """
    logger = SymptomEvaluationLogger()
    logger.log_extraction(
        thread_id, user_input, extracted_symptoms, follow_up_questions, metrics
    )
    return True
