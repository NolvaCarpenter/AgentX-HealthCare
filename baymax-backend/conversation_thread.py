#!/usr/bin/env python3

import os
import sqlite3
import uuid
import datetime
from typing import Dict, List, Optional, Any

# Database path
DB_PATH = os.getenv("DB_PATH")


def create_conversation_tables():
    """Create tables for conversation tracking if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create conversation threads table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_threads (
            thread_id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TEXT,
            last_updated TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    """
    )

    # Create conversation messages table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_messages (
            message_id TEXT PRIMARY KEY,
            thread_id TEXT,
            timestamp TEXT,
            role TEXT,  -- 'user' or 'assistant'
            content TEXT,
            FOREIGN KEY (thread_id) REFERENCES conversation_threads(thread_id)
        )
    """
    )

    # Create symptoms data table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS thread_symptoms (
            thread_id TEXT PRIMARY KEY,
            symptom_data TEXT,  -- JSON serialized symptom state
            last_updated TEXT,
            FOREIGN KEY (thread_id) REFERENCES conversation_threads(thread_id)
        )
    """
    )

    # Create medications data table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS thread_medications (
            thread_id TEXT PRIMARY KEY, 
            medication_data TEXT,  -- JSON serialized medication state
            last_updated TEXT,
            FOREIGN KEY (thread_id) REFERENCES conversation_threads(thread_id)
        )
    """
    )

    conn.commit()
    conn.close()


def generate_thread_id() -> str:
    """Generate a unique thread ID."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}-{str(uuid.uuid4())[:8]}"


def create_new_thread(user_id: str = "default_user") -> str:
    """Create a new conversation thread and return its ID."""
    thread_id = generate_thread_id()
    timestamp = datetime.datetime.now().isoformat()

    print(f"Creating new thread: {thread_id} for user: {user_id}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversation_threads (thread_id, user_id, created_at, last_updated)
        VALUES (?, ?, ?, ?)
        """,
        (thread_id, user_id, timestamp, timestamp),
    )

    conn.commit()
    conn.close()

    return thread_id


def save_message(thread_id: str, role: str, content: str) -> None:
    """Save a message to the conversation thread."""
    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Update thread's last_updated timestamp
    cursor.execute(
        """
        UPDATE conversation_threads
        SET last_updated = ?
        WHERE thread_id = ?
        """,
        (timestamp, thread_id),
    )

    # Insert the new message
    cursor.execute(
        """
        INSERT INTO conversation_messages (message_id, thread_id, timestamp, role, content)
        VALUES (?, ?, ?, ?, ?)
        """,
        (message_id, thread_id, timestamp, role, content),
    )

    conn.commit()
    conn.close()


def get_thread_history(thread_id: str) -> List[Dict[str, str]]:
    """Get all messages from a conversation thread."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, content 
        FROM conversation_messages
        WHERE thread_id = ?
        ORDER BY timestamp
        """,
        (thread_id,),
    )

    messages = [
        {"role": role, "content": content} for role, content in cursor.fetchall()
    ]
    conn.close()

    return messages


def get_active_threads(user_id: str = "default_user") -> List[Dict[str, Any]]:
    """Get all active threads for a user."""
    print(f"Getting active threads for user: {user_id}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get threads for specific user if provided, otherwise get all threads
    cursor.execute(
        """
        SELECT thread_id, created_at, last_updated, user_id
        FROM conversation_threads
        WHERE user_id = ? AND is_active = 1
        ORDER BY last_updated DESC
        """,
        (user_id,),
    )

    threads = [
        {
            "thread_id": thread_id,
            "created_at": created_at,
            "last_updated": last_updated,
            "user_id": thread_user_id,
        }
        for thread_id, created_at, last_updated, thread_user_id in cursor.fetchall()
    ]

    conn.close()

    print(f"Found {len(threads)} active threads for user: {user_id}")
    return threads


def get_thread_summary(thread_id: str) -> Dict[str, Any]:
    """Get a summary of a conversation thread."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get thread info
    cursor.execute(
        """
        SELECT user_id, created_at, last_updated
        FROM conversation_threads
        WHERE thread_id = ?
        """,
        (thread_id,),
    )

    thread_info = cursor.fetchone()
    if not thread_info:
        conn.close()
        return {"error": "Thread not found"}

    user_id, created_at, last_updated = thread_info

    # Count messages
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM conversation_messages
        WHERE thread_id = ?
        """,
        (thread_id,),
    )

    message_count = cursor.fetchone()[0]
    conn.close()

    return {
        "thread_id": thread_id,
        "user_id": user_id,
        "created_at": created_at,
        "last_updated": last_updated,
        "message_count": message_count,
    }


def save_symptom_data(thread_id: str, symptom_data: Dict) -> None:
    """Save symptom data for a conversation thread.

    Args:
        thread_id: The ID of the thread
        symptom_data: Dictionary containing serializable symptom state
    """
    import json

    timestamp = datetime.datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Convert symptom data to JSON string
    symptom_json = json.dumps(symptom_data)

    # Check if thread already has symptoms data
    cursor.execute(
        """
        SELECT 1 FROM thread_symptoms WHERE thread_id = ?
        """,
        (thread_id,),
    )

    if cursor.fetchone():
        # Update existing record
        cursor.execute(
            """
            UPDATE thread_symptoms
            SET symptom_data = ?, last_updated = ?
            WHERE thread_id = ?
            """,
            (symptom_json, timestamp, thread_id),
        )
    else:
        # Insert new record
        cursor.execute(
            """
            INSERT INTO thread_symptoms (thread_id, symptom_data, last_updated)
            VALUES (?, ?, ?)
            """,
            (thread_id, symptom_json, timestamp),
        )

    conn.commit()
    conn.close()


def save_medication_data(thread_id: str, medication_data: Dict) -> None:
    """Save medication data for a conversation thread.

    Args:
        thread_id: The ID of the thread
        medication_data: Dictionary containing serializable medication state
    """
    import json

    timestamp = datetime.datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Convert medication data to JSON string
    medication_json = json.dumps(medication_data)

    # Check if thread already has medication data
    cursor.execute(
        """
        SELECT 1 FROM thread_medications WHERE thread_id = ?
        """,
        (thread_id,),
    )

    if cursor.fetchone():
        # Update existing record
        cursor.execute(
            """
            UPDATE thread_medications
            SET medication_data = ?, last_updated = ?
            WHERE thread_id = ?
            """,
            (medication_json, timestamp, thread_id),
        )
    else:
        # Insert new record
        cursor.execute(
            """
            INSERT INTO thread_medications (thread_id, medication_data, last_updated)
            VALUES (?, ?, ?)
            """,
            (thread_id, medication_json, timestamp),
        )

    conn.commit()
    conn.close()


def get_symptom_data(thread_id: str) -> Optional[Dict]:
    """Get symptom data for a conversation thread.

    Args:
        thread_id: The ID of the thread

    Returns:
        Dictionary containing the symptom state or None if not found
    """
    import json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT symptom_data
        FROM thread_symptoms
        WHERE thread_id = ?
        """,
        (thread_id,),
    )

    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        return json.loads(result[0])

    return None


def get_medication_data(thread_id: str) -> Optional[Dict]:
    """Get medication data for a conversation thread.

    Args:
        thread_id: The ID of the thread

    Returns:
        Dictionary containing the medication state or None if not found
    """
    import json

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT medication_data
        FROM thread_medications
        WHERE thread_id = ?
        """,
        (thread_id,),
    )

    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        return json.loads(result[0])

    return None


# Create tables when this module is imported
create_conversation_tables()
