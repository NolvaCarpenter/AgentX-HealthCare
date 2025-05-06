#!/usr/bin/env python3

import os
import sys
import sqlite3
import datetime

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation_thread_fixed import (
    create_new_thread,
    get_active_threads,
    save_message,
    get_thread_history,
    get_thread_summary,
)


def test_username_threads():
    """Test the username integration with thread management."""
    print("Testing username threads integration...")

    # Create threads for different users
    user1 = "test_user_1"
    user2 = "test_user_2"

    # Create a thread for user1
    thread1 = create_new_thread(user1)
    print(f"Created thread {thread1} for user {user1}")
    save_message(thread1, "user", f"This is a message from {user1}")
    save_message(thread1, "assistant", f"Hello {user1}, how can I help you?")

    # Create a thread for user2
    thread2 = create_new_thread(user2)
    print(f"Created thread {thread2} for user {user2}")
    save_message(thread2, "user", f"This is a message from {user2}")
    save_message(thread2, "assistant", f"Hello {user2}, how can I help you?")

    # Create another thread for user1
    thread3 = create_new_thread(user1)
    print(f"Created another thread {thread3} for user {user1}")
    save_message(thread3, "user", f"This is another message from {user1}")
    save_message(thread3, "assistant", f"Hello again {user1}, how else can I help?")

    # Get threads for user1
    user1_threads = get_active_threads(user1)
    print(f"\nThreads for {user1}:")
    for thread in user1_threads:
        print(
            f"- Thread ID: {thread['thread_id']}, Last updated: {thread['last_updated']}"
        )

    # Get threads for user2
    user2_threads = get_active_threads(user2)
    print(f"\nThreads for {user2}:")
    for thread in user2_threads:
        print(
            f"- Thread ID: {thread['thread_id']}, Last updated: {thread['last_updated']}"
        )

    # Verify thread histories
    print(f"\nHistory for {user1}'s thread {thread1}:")
    history1 = get_thread_history(thread1)
    for msg in history1:
        print(f"- {msg['role']}: {msg['content']}")

    print(f"\nHistory for {user2}'s thread {thread2}:")
    history2 = get_thread_history(thread2)
    for msg in history2:
        print(f"- {msg['role']}: {msg['content']}")

    print("\nTest completed successfully!")


if __name__ == "__main__":
    test_username_threads()
